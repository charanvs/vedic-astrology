from __future__ import annotations
import hashlib,hmac,secrets,uuid
from dataclasses import dataclass
from datetime import datetime,timedelta,timezone
from cryptography.exceptions import InvalidKey
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from email_validator import EmailNotValidError,validate_email
from fastapi import Depends,HTTPException,Request,status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import AuditEvent,AuthSession,RateLimitCounter,User
from app.models.entities import utcnow

def hash_token(value:str)->str:return hashlib.sha256(value.encode("utf-8")).hexdigest()
def new_token()->str:return secrets.token_urlsafe(48)
def normalize_email(value:str)->str:
    try:return validate_email(value,check_deliverability=False).normalized.lower()
    except EmailNotValidError as exc:raise ValueError("Enter a valid email address") from exc
def hash_password(value:str)->str:
    if len(value)<12 or len(value)>128:raise ValueError("Password must contain 12 to 128 characters")
    return Argon2id(salt=secrets.token_bytes(16),length=32,iterations=2,lanes=1,memory_cost=19456).derive_phc_encoded(value.encode())
def verify_password(value:str,encoded:str|None)->bool:
    if not encoded:return False
    try:Argon2id.verify_phc_encoded(value.encode(),encoded);return True
    except (InvalidKey,ValueError):return False
def request_ip_hash(request:Request)->str|None:
    if not request.client:return None
    return hash_token(request.client.host)
def audit(db:Session,request:Request,event_type:str,outcome:str,user_id:int|None=None,detail:str|None=None)->None:
    db.add(AuditEvent(user_id=user_id,event_type=event_type,outcome=outcome,request_id=getattr(request.state,"request_id",None),ip_hash=request_ip_hash(request),detail=detail[:255] if detail else None))

def rate_limit(db:Session,request:Request,scope:str,limit:int,seconds:int,subject:str|None=None)->None:
    now=utcnow();epoch=int(now.replace(tzinfo=timezone.utc).timestamp());start=datetime.fromtimestamp(epoch-(epoch%seconds),timezone.utc).replace(tzinfo=None)
    key=hash_token(subject or (request.client.host if request.client else "unknown"))
    row=db.scalar(select(RateLimitCounter).where(RateLimitCounter.scope==scope,RateLimitCounter.key_hash==key,RateLimitCounter.window_started_at==start))
    if row:
        row.count+=1
        if row.count>limit:
            db.commit();raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS,"Too many requests; try again later",headers={"Retry-After":str(seconds)})
    else:db.add(RateLimitCounter(scope=scope,key_hash=key,window_started_at=start,count=1,expires_at=start+timedelta(seconds=seconds*2)))
    try:db.commit()
    except IntegrityError:
        db.rollback();raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS,"Too many requests; try again later")

@dataclass
class AuthContext:
    user:User
    session:AuthSession

def create_session(db:Session,request:Request,user:User)->tuple[AuthSession,str,str]:
    raw=new_token();csrf=new_token();now=utcnow();settings=request.app.state.settings
    item=AuthSession(public_id=str(uuid.uuid4()),token_hash=hash_token(raw),csrf_hash=hash_token(csrf),user_id=user.id,created_at=now,last_activity_at=now,expires_at=now+timedelta(minutes=settings.session_idle_minutes),absolute_expires_at=now+timedelta(hours=settings.session_absolute_hours),ip_hash=request_ip_hash(request),user_agent=(request.headers.get("user-agent") or "")[:255] or None)
    db.add(item);db.flush();return item,raw,csrf
def set_session_cookie(response,request:Request,raw:str)->None:
    settings=request.app.state.settings
    response.set_cookie(settings.session_cookie_name,raw,max_age=settings.session_absolute_hours*3600,httponly=True,secure=settings.session_cookie_secure,samesite="lax",path=settings.session_cookie_path)
def clear_session_cookie(response,request:Request)->None:
    settings=request.app.state.settings
    response.delete_cookie(settings.session_cookie_name,path=settings.session_cookie_path,secure=settings.session_cookie_secure,samesite="lax")
PENDING_APPROVAL="Your account is awaiting administrator approval"
def awaiting_approval(request:Request,user:User)->bool:
    return request.app.state.settings.require_admin_approval and user.role!="admin" and user.approved_at is None
def current_context(request:Request,db:Session=Depends(get_db))->AuthContext:
    raw=request.cookies.get(request.app.state.settings.session_cookie_name)
    if not raw:raise HTTPException(status.HTTP_401_UNAUTHORIZED,"Authentication required")
    item=db.scalar(select(AuthSession).where(AuthSession.token_hash==hash_token(raw)))
    now=utcnow()
    if not item or item.revoked_at or item.expires_at<=now or item.absolute_expires_at<=now:
        if item and not item.revoked_at:item.revoked_at=now;db.commit()
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,"Session is invalid or expired")
    user=db.get(User,item.user_id)
    if not user or not user.is_active:raise HTTPException(status.HTTP_401_UNAUTHORIZED,"Account is unavailable")
    if awaiting_approval(request,user):raise HTTPException(status.HTTP_401_UNAUTHORIZED,PENDING_APPROVAL)
    item.last_activity_at=now;item.expires_at=min(now+timedelta(minutes=request.app.state.settings.session_idle_minutes),item.absolute_expires_at);db.commit()
    request.state.auth_session=item
    return AuthContext(user,item)
def current_user(context:AuthContext=Depends(current_context))->User:return context.user
def require_admin(user:User=Depends(current_user))->User:
    if user.role!="admin":raise HTTPException(status.HTTP_403_FORBIDDEN,"Administrator access required")
    return user
def require_csrf(request:Request,context:AuthContext=Depends(current_context))->AuthContext:
    token=request.headers.get("X-CSRF-Token","")
    if not token or not hmac.compare_digest(hash_token(token),context.session.csrf_hash):raise HTTPException(status.HTTP_403_FORBIDDEN,"Invalid CSRF token")
    origin=request.headers.get("origin")
    if origin and origin.rstrip("/") not in {item.rstrip("/") for item in request.app.state.settings.allowed_origins}:raise HTTPException(status.HTTP_403_FORBIDDEN,"Cross-origin request rejected")
    return context
def owned_profile_query(profile_id:int,user:User):
    from app.models import BirthProfile
    return select(BirthProfile).where(BirthProfile.id==profile_id,BirthProfile.user_id==user.id)
