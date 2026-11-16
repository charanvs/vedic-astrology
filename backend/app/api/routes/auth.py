from datetime import timedelta
from fastapi import APIRouter,Depends,HTTPException,Request,Response,status
from sqlalchemy import select,update
from sqlalchemy.orm import Session,joinedload
from app.core.security import (PENDING_APPROVAL,audit,awaiting_approval,clear_session_cookie,create_session,current_context,current_user,
 hash_password,hash_token,new_token,normalize_email,rate_limit,require_csrf,set_session_cookie,verify_password)
from app.db.session import get_db
from app.models import AccountToken,AuthSession,BirthProfile,User
from app.models.entities import utcnow
from app.schemas.auth import (AccountUpdateRequest,AuthResponse,ChangePasswordRequest,DeletionRequest,
 ForgotPasswordRequest,LoginRequest,PreferencesRead,PreferencesUpdate,RegisterRequest,ResetPasswordRequest,
 SessionRead,TokenRequest,UserRead)
from app.services.email_delivery import EmailDeliveryError,send_account_token

router=APIRouter(tags=["authentication"])
GENERIC_RECOVERY="If the account is eligible, recovery instructions have been prepared."

def user_read(user:User)->dict:
 return {"id":user.id,"full_name":user.full_name,"email":user.email or "","email_verified":user.email_verified_at is not None,"approved":user.role=="admin" or user.approved_at is not None,"is_active":user.is_active,"role":user.role,"created_at":user.created_at,"last_login_at":user.last_login_at,"deletion_requested_at":user.deletion_requested_at}
def issue_token(db:Session,user:User,purpose:str,minutes:int)->str:
 raw=new_token();now=utcnow()
 db.execute(update(AccountToken).where(AccountToken.user_id==user.id,AccountToken.purpose==purpose,AccountToken.used_at.is_(None)).values(used_at=now))
 db.add(AccountToken(user_id=user.id,purpose=purpose,token_hash=hash_token(raw),created_at=now,expires_at=now+timedelta(minutes=minutes)))
 return raw
def consume_token(db:Session,raw:str,purpose:str)->tuple[AccountToken,User]:
 token=db.scalar(select(AccountToken).where(AccountToken.token_hash==hash_token(raw),AccountToken.purpose==purpose))
 if not token or token.used_at or token.expires_at<=utcnow():raise HTTPException(400,"Token is invalid or expired")
 user=db.get(User,token.user_id)
 if not user or not user.is_active:raise HTTPException(400,"Token is invalid or expired")
 token.used_at=utcnow();return token,user

@router.post("/auth/register",response_model=AuthResponse,status_code=201)
def register(payload:RegisterRequest,request:Request,db:Session=Depends(get_db)):
 email=normalize_email(str(payload.email));rate_limit(db,request,"register",5,3600,email)
 if db.scalar(select(User.id).where(User.email==email)):raise HTTPException(409,"An account with this email already exists")
 user=User(full_name=payload.full_name,email=email,password_hash=hash_password(payload.password),role="user",is_active=True)
 db.add(user);db.flush();raw=issue_token(db,user,"verify_email",request.app.state.settings.verification_token_minutes)
 audit(db,request,"account.register","success",user.id);db.commit();db.refresh(user)
 settings=request.app.state.settings
 if settings.require_verified_email:
  try:send_account_token(settings,email,"verify_email",raw)
  except EmailDeliveryError as exc:raise HTTPException(503,str(exc)) from exc
 steps=[step for step,needed in (("verify your email",settings.require_verified_email),("wait for an administrator to approve it",settings.require_admin_approval)) if needed]
 message="Account created. Before signing in, "+" and ".join(steps)+"." if steps else "Account created. You can now sign in."
 return {"message":message,"user":user_read(user),"development_token":raw if settings.environment=="development" else None}

@router.post("/auth/verify-email",response_model=AuthResponse)
def verify_email(payload:TokenRequest,request:Request,db:Session=Depends(get_db)):
 rate_limit(db,request,"verify_email",10,3600);_,user=consume_token(db,payload.token,"verify_email");user.email_verified_at=utcnow();audit(db,request,"email.verify","success",user.id);db.commit()
 return {"message":"Email verified. You can now sign in.","user":user_read(user)}

@router.post("/auth/resend-verification",response_model=AuthResponse)
def resend_verification(payload:ForgotPasswordRequest,request:Request,db:Session=Depends(get_db)):
 email=normalize_email(str(payload.email));rate_limit(db,request,"verify_resend",3,3600,email);user=db.scalar(select(User).where(User.email==email))
 raw=None
 if user and user.is_active and not user.email_verified_at:
  raw=issue_token(db,user,"verify_email",request.app.state.settings.verification_token_minutes);audit(db,request,"email.verify_resend","accepted",user.id);db.commit()
  try:send_account_token(request.app.state.settings,email,"verify_email",raw)
  except EmailDeliveryError:pass
 return {"message":"If the account is eligible, verification instructions have been prepared.","development_token":raw if raw and request.app.state.settings.environment=="development" else None}

@router.post("/auth/login",response_model=AuthResponse)
def login(payload:LoginRequest,response:Response,request:Request,db:Session=Depends(get_db)):
 email=normalize_email(str(payload.email));rate_limit(db,request,"login",8,900,email);user=db.scalar(select(User).where(User.email==email))
 if not user or not verify_password(payload.password,user.password_hash):
  audit(db,request,"auth.login","failure",user.id if user else None);db.commit();raise HTTPException(status.HTTP_401_UNAUTHORIZED,"Invalid email or password")
 if not user.is_active:raise HTTPException(status.HTTP_403_FORBIDDEN,"Account is unavailable")
 if request.app.state.settings.require_verified_email and not user.email_verified_at:raise HTTPException(status.HTTP_403_FORBIDDEN,"Email verification is required")
 if awaiting_approval(request,user):raise HTTPException(status.HTTP_403_FORBIDDEN,PENDING_APPROVAL)
 session,raw,csrf=create_session(db,request,user);user.last_login_at=utcnow();audit(db,request,"auth.login","success",user.id);db.commit();set_session_cookie(response,request,raw)
 return {"message":"Signed in successfully.","user":user_read(user),"csrf_token":csrf}

@router.get("/auth/me",response_model=UserRead)
def me(user:User=Depends(current_user)):return user_read(user)

@router.get("/auth/csrf")
def csrf_token(context=Depends(current_context),db:Session=Depends(get_db)):
 raw=new_token();context.session.csrf_hash=hash_token(raw);db.commit();return {"csrf_token":raw}

@router.post("/auth/logout")
def logout(response:Response,request:Request,context=Depends(require_csrf),db:Session=Depends(get_db)):
 context.session.revoked_at=utcnow();audit(db,request,"auth.logout","success",context.user.id);db.commit();clear_session_cookie(response,request);return {"message":"Signed out successfully."}

@router.get("/auth/sessions",response_model=list[SessionRead])
def sessions(context=Depends(current_context),db:Session=Depends(get_db)):
 rows=db.scalars(select(AuthSession).where(AuthSession.user_id==context.user.id,AuthSession.revoked_at.is_(None),AuthSession.expires_at>utcnow()).order_by(AuthSession.created_at.desc())).all()
 return [{"id":x.public_id,"created_at":x.created_at,"last_activity_at":x.last_activity_at,"expires_at":x.expires_at,"current":x.id==context.session.id,"user_agent":x.user_agent} for x in rows]

@router.delete("/auth/sessions/{session_id}")
def revoke_session(session_id:str,request:Request,context=Depends(require_csrf),db:Session=Depends(get_db)):
 item=db.scalar(select(AuthSession).where(AuthSession.public_id==session_id,AuthSession.user_id==context.user.id))
 if not item:raise HTTPException(404,"Session not found")
 item.revoked_at=utcnow();audit(db,request,"session.revoke","success",context.user.id);db.commit();return {"message":"Session revoked."}

@router.post("/auth/forgot-password",response_model=AuthResponse)
def forgot_password(payload:ForgotPasswordRequest,request:Request,db:Session=Depends(get_db)):
 email=normalize_email(str(payload.email));rate_limit(db,request,"password_forgot",3,3600,email);user=db.scalar(select(User).where(User.email==email));raw=None
 if user and user.is_active:
  raw=issue_token(db,user,"reset_password",request.app.state.settings.reset_token_minutes);audit(db,request,"password.reset_requested","accepted",user.id);db.commit()
  try:send_account_token(request.app.state.settings,email,"reset_password",raw)
  except EmailDeliveryError:pass
 return {"message":GENERIC_RECOVERY,"development_token":raw if raw and request.app.state.settings.environment=="development" else None}

@router.post("/auth/reset-password",response_model=AuthResponse)
def reset_password(payload:ResetPasswordRequest,request:Request,db:Session=Depends(get_db)):
 rate_limit(db,request,"password_reset",8,3600);_,user=consume_token(db,payload.token,"reset_password");user.password_hash=hash_password(payload.password)
 db.execute(update(AuthSession).where(AuthSession.user_id==user.id,AuthSession.revoked_at.is_(None)).values(revoked_at=utcnow()));audit(db,request,"password.reset","success",user.id);db.commit();return {"message":"Password reset. Sign in with your new password."}

@router.post("/auth/change-password",response_model=AuthResponse)
def change_password(payload:ChangePasswordRequest,request:Request,context=Depends(require_csrf),db:Session=Depends(get_db)):
 if not verify_password(payload.current_password,context.user.password_hash):raise HTTPException(400,"Current password is incorrect")
 context.user.password_hash=hash_password(payload.new_password);db.execute(update(AuthSession).where(AuthSession.user_id==context.user.id,AuthSession.id!=context.session.id,AuthSession.revoked_at.is_(None)).values(revoked_at=utcnow()));context.session.csrf_hash=hash_token(new_token());audit(db,request,"password.change","success",context.user.id);db.commit()
 return {"message":"Password changed. Other sessions were revoked.","user":user_read(context.user)}

@router.get("/account/profile",response_model=UserRead)
def account_profile(user:User=Depends(current_user)):return user_read(user)
@router.patch("/account/profile",response_model=UserRead)
def update_account(payload:AccountUpdateRequest,request:Request,context=Depends(require_csrf),db:Session=Depends(get_db)):
 context.user.full_name=payload.full_name;audit(db,request,"account.update","success",context.user.id);db.commit();return user_read(context.user)

def preferences_read(user:User)->dict:
 return {"theme":user.pref_theme,"report_language":user.pref_report_language,"dasha_year_convention":user.pref_dasha_year_convention,"matching_ruleset":user.pref_matching_ruleset}
@router.get("/account/preferences",response_model=PreferencesRead)
def get_preferences(user:User=Depends(current_user)):return preferences_read(user)
@router.patch("/account/preferences",response_model=PreferencesRead)
def update_preferences(payload:PreferencesUpdate,request:Request,context=Depends(require_csrf),db:Session=Depends(get_db)):
 for key,value in payload.model_dump(exclude_unset=True).items():setattr(context.user,f"pref_{key}",value)
 audit(db,request,"account.preferences_update","success",context.user.id);db.commit();return preferences_read(context.user)

@router.get("/account/export")
def export_account(context=Depends(current_context),db:Session=Depends(get_db)):
 if utcnow()-context.session.created_at>timedelta(minutes=10):raise HTTPException(403,"Recent sign-in required for data export")
 profiles=db.scalars(select(BirthProfile).options(joinedload(BirthProfile.location)).where(BirthProfile.user_id==context.user.id)).unique().all()
 return {"exported_at":utcnow().isoformat()+"Z","account":user_read(context.user),"birth_profiles":[{"id":p.id,"full_name":p.full_name,"gender":p.gender,"birth_date":p.birth_date.isoformat(),"birth_time":p.birth_time.isoformat() if p.birth_time else None,"birth_time_unknown":p.birth_time_unknown,"birthplace":{"city":p.location.city,"state":p.location.state,"country":p.location.country,"timezone":p.location.timezone},"notes":p.notes,"created_at":p.created_at.isoformat()} for p in profiles]}

@router.post("/account/deletion-request")
def request_deletion(payload:DeletionRequest,request:Request,context=Depends(require_csrf),db:Session=Depends(get_db)):
 if payload.confirmation!="DELETE MY ACCOUNT":raise HTTPException(400,"Confirmation phrase is incorrect")
 if not verify_password(payload.current_password,context.user.password_hash):raise HTTPException(400,"Current password is incorrect")
 context.user.deletion_requested_at=utcnow();audit(db,request,"account.deletion_requested","success",context.user.id);db.commit();return {"message":"Account deletion request recorded. Data has not been deleted."}
