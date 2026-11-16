from dataclasses import replace
from datetime import timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine,delete,select
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
from app.db.session import get_db
from app.main import create_app
from app.models import AccountToken,AuditEvent,AuthSession,BirthProfile,Location,RateLimitCounter,User
from app.models.entities import utcnow

engine=create_engine(get_settings().database_url(test=True),pool_pre_ping=True)
TestingSession=sessionmaker(bind=engine,expire_on_commit=False)
app=create_app()
def override_db():
 with TestingSession() as db:yield db
app.dependency_overrides[get_db]=override_db

@pytest.fixture(autouse=True)
def clean():
 with TestingSession() as db:
  for model in (BirthProfile,AuthSession,AccountToken,AuditEvent,RateLimitCounter,Location,User):db.execute(delete(model))
  db.commit()

def approve_directly(email:str):
 with TestingSession() as db:
  user=db.scalar(select(User).where(User.email==email.lower()));user.approved_at=utcnow();db.commit()

def signup(client:TestClient,email:str,password="correct horse battery staple"):
 registered=client.post("/api/auth/register",json={"full_name":"Test User","email":email,"password":password,"accept_terms":True})
 assert registered.status_code==201
 token=registered.json()["development_token"];assert token
 assert client.post("/api/auth/verify-email",json={"token":token}).status_code==200
 approve_directly(email)
 logged=client.post("/api/auth/login",json={"email":email,"password":password});assert logged.status_code==200
 client.headers["X-CSRF-Token"]=logged.json()["csrf_token"]
 return logged.json()["user"]

def location(client):
 result=client.post("/api/locations",json={"city":"Chandigarh","state":"Chandigarh","country":"India","country_code":"IN","latitude":30.7333,"longitude":76.7794,"timezone":"Asia/Kolkata"})
 assert result.status_code==201;return result.json()
def profile(client,location_id):
 result=client.post("/api/birth-profiles",json={"full_name":"Private Person","birth_date":"2000-01-15","birth_time":"10:30:00","birth_time_unknown":False,"location_id":location_id})
 assert result.status_code==201;return result.json()

def test_registration_argon2id_duplicate_and_unverified_login():
 original=app.state.settings;app.state.settings=replace(original,require_verified_email=True)
 try:
  client=TestClient(app)
  data={"full_name":"Test","email":"Case@Example.com","password":"correct horse battery staple","accept_terms":True}
  result=client.post("/api/auth/register",json=data);assert result.status_code==201
  with TestingSession() as db:
   user=db.scalar(select(User).where(User.email=="case@example.com"));assert user and user.password_hash.startswith("$argon2id$") and "correct horse" not in user.password_hash
  assert client.post("/api/auth/login",json={"email":"case@example.com","password":data["password"]}).status_code==403
  assert client.post("/api/auth/register",json=data).status_code==409
 finally:
  app.state.settings=original

def test_login_me_csrf_logout_and_invalid_cookie():
 client=TestClient(app);signup(client,"one@example.com")
 assert client.get("/api/auth/me").status_code==200
 saved=client.headers.pop("X-CSRF-Token");assert client.post("/api/auth/logout").status_code==403
 client.headers["X-CSRF-Token"]=saved;assert client.post("/api/auth/logout").status_code==200
 assert client.get("/api/auth/me").status_code==401
 client.cookies.set("vedic_session","invalid");assert client.get("/api/auth/me").status_code==401

def test_password_reset_single_use_and_change_revokes_other_sessions():
 first=TestClient(app);signup(first,"reset@example.com")
 second=TestClient(app);login=second.post("/api/auth/login",json={"email":"reset@example.com","password":"correct horse battery staple"});second.headers["X-CSRF-Token"]=login.json()["csrf_token"]
 forgot=first.post("/api/auth/forgot-password",json={"email":"reset@example.com"});token=forgot.json()["development_token"]
 assert first.post("/api/auth/reset-password",json={"token":token,"password":"a new secure password value"}).status_code==200
 assert first.post("/api/auth/reset-password",json={"token":token,"password":"another secure password value"}).status_code==400
 assert second.get("/api/auth/me").status_code==401
 login=first.post("/api/auth/login",json={"email":"reset@example.com","password":"a new secure password value"});first.headers["X-CSRF-Token"]=login.json()["csrf_token"]
 assert first.post("/api/auth/change-password",json={"current_password":"wrong","new_password":"still another secure password"}).status_code==400
 assert first.post("/api/auth/change-password",json={"current_password":"a new secure password value","new_password":"still another secure password"}).status_code==200

def test_expired_and_revoked_sessions_are_rejected():
 client=TestClient(app);signup(client,"expired@example.com")
 with TestingSession() as db:
  item=db.scalars(select(AuthSession)).first();item.expires_at=utcnow()-timedelta(seconds=1);db.commit()
 assert client.get("/api/auth/me").status_code==401

def test_inactive_invalid_login_and_rate_limit():
 client=TestClient(app);registered=client.post("/api/auth/register",json={"full_name":"Limited","email":"limited@example.com","password":"correct horse battery staple","accept_terms":True});client.post("/api/auth/verify-email",json={"token":registered.json()["development_token"]})
 assert client.post("/api/auth/login",json={"email":"limited@example.com","password":"wrong"}).status_code==401
 with TestingSession() as db:user=db.scalar(select(User).where(User.email=="limited@example.com"));user.is_active=False;db.commit()
 assert client.post("/api/auth/login",json={"email":"limited@example.com","password":"correct horse battery staple"}).status_code==403
 with TestingSession() as db:user=db.scalar(select(User).where(User.email=="limited@example.com"));user.is_active=True;db.commit()
 codes=[client.post("/api/auth/login",json={"email":"limited@example.com","password":"wrong"}).status_code for _ in range(7)]
 assert codes[-1]==429

def test_expired_reset_token_and_mass_assignment():
 client=TestClient(app);registered=client.post("/api/auth/register",json={"full_name":"Strict","email":"strict@example.com","password":"correct horse battery staple","accept_terms":True,"role":"admin"});assert registered.status_code==422
 signup(client,"strict@example.com");forgot=client.post("/api/auth/forgot-password",json={"email":"strict@example.com"});token=forgot.json()["development_token"]
 with TestingSession() as db:item=db.scalar(select(AccountToken).where(AccountToken.purpose=="reset_password"));item.expires_at=utcnow()-timedelta(seconds=1);db.commit()
 assert client.post("/api/auth/reset-password",json={"token":token,"password":"another secure password"}).status_code==400
 loc=location(client)
 assert client.post("/api/birth-profiles",json={"full_name":"Injected","birth_date":"2000-01-01","birth_time":"10:00","location_id":loc["id"],"user_id":999}).status_code==422

def test_session_ownership_export_and_deletion_request():
 a=TestClient(app);signup(a,"owner@example.com");owned=profile(a,location(a)["id"]);sessions=a.get("/api/auth/sessions").json();assert sessions and sessions[0]["current"]
 b=TestClient(app);signup(b,"other@example.com");assert b.delete("/api/auth/sessions/"+sessions[0]["id"]).status_code==404
 exported=a.get("/api/account/export");assert exported.status_code==200 and exported.json()["birth_profiles"][0]["id"]==owned["id"];assert "password_hash" not in str(exported.json())
 assert a.post("/api/account/deletion-request",json={"current_password":"wrong","confirmation":"DELETE MY ACCOUNT"}).status_code==400
 assert a.post("/api/account/deletion-request",json={"current_password":"correct horse battery staple","confirmation":"DELETE MY ACCOUNT"}).status_code==200

def test_cross_user_object_authorization_and_unowned_quarantine():
 a=TestClient(app);signup(a,"a@example.com");owned=profile(a,location(a)["id"])
 b=TestClient(app);signup(b,"b@example.com");b_owned=profile(b,owned["location_id"])
 assert [item["id"] for item in b.get("/api/birth-profiles").json()]==[b_owned["id"]]
 for path in (f"/api/birth-profiles/{owned['id']}",f"/api/astrology/birth-profiles/{owned['id']}/calculate",f"/api/dasha/birth-profiles/{owned['id']}",f"/api/divisional/birth-profiles/{owned['id']}/d9"):assert b.get(path).status_code==404
 assert b.patch(f"/api/birth-profiles/{owned['id']}",json={"full_name":"Stolen"}).status_code==404
 assert b.post("/api/reports/kundli",json={"profile_id":owned["id"],"language":"en"}).status_code==404
 assert b.post("/api/matching/birth-profiles",json={"partner_one_profile_id":owned["id"],"partner_two_profile_id":b_owned["id"],"partner_one_role":"bride","partner_two_role":"groom"}).status_code==404
 with TestingSession() as db:
  unowned=BirthProfile(full_name="Legacy",birth_date="2001-01-01",birth_time="10:00:00",birth_time_unknown=False,location_id=owned["location_id"]);db.add(unowned);db.commit();legacy_id=unowned.id
 assert a.get(f"/api/birth-profiles/{legacy_id}").status_code==404
 assert a.delete(f"/api/birth-profiles/{owned['id']}").status_code==204
 assert a.get(f"/api/birth-profiles/{owned['id']}").status_code==404

def test_cross_origin_and_missing_csrf_rejected():
 client=TestClient(app);signup(client,"csrf@example.com");token=client.headers.pop("X-CSRF-Token")
 assert client.post("/api/locations",json={}).status_code==403
 client.headers["X-CSRF-Token"]=token
 assert client.post("/api/locations",json={},headers={"Origin":"https://evil.example"}).status_code==403

def test_production_cookie_attributes_and_headers():
 settings=replace(get_settings(),environment="production",session_cookie_secure=True,session_cookie_path="/vedic-astrology/",base_path="/vedic-astrology")
 prod=create_app(settings);prod.dependency_overrides[get_db]=override_db;client=TestClient(prod,base_url="https://testserver")
 registered=client.post("/api/auth/register",json={"full_name":"Prod","email":"prod@example.com","password":"correct horse battery staple","accept_terms":True});token=registered.json().get("development_token")
 assert token is None
 with TestingSession() as db:
  user=db.scalar(select(User).where(User.email=="prod@example.com"));user.email_verified_at=utcnow();user.approved_at=utcnow();db.commit()
 response=client.post("/api/auth/login",json={"email":"prod@example.com","password":"correct horse battery staple"})
 cookie=response.headers["set-cookie"].lower();assert "secure" in cookie and "httponly" in cookie and "samesite=lax" in cookie and "path=/vedic-astrology/" in cookie
 assert response.headers["strict-transport-security"]=="max-age=31536000";assert response.headers["x-content-type-options"]=="nosniff"

def test_preferences_require_auth_default_to_null_and_update_partially():
 anonymous=TestClient(app);assert anonymous.get("/api/account/preferences").status_code==401
 client=TestClient(app);signup(client,"prefs@example.com")
 defaults=client.get("/api/account/preferences");assert defaults.status_code==200
 assert defaults.json()=={"theme":None,"report_language":None,"dasha_year_convention":None,"matching_ruleset":None}
 first=client.patch("/api/account/preferences",json={"theme":"dark"});assert first.status_code==200
 assert first.json()=={"theme":"dark","report_language":None,"dasha_year_convention":None,"matching_ruleset":None}
 second=client.patch("/api/account/preferences",json={"report_language":"hi","dasha_year_convention":"360_day_savana","matching_ruleset":"muhurta_chintamani_joshi_v1"})
 assert second.status_code==200
 assert second.json()=={"theme":"dark","report_language":"hi","dasha_year_convention":"360_day_savana","matching_ruleset":"muhurta_chintamani_joshi_v1"}
 assert client.get("/api/account/preferences").json()==second.json()

def test_preferences_reject_invalid_values_and_extra_fields_and_missing_csrf():
 client=TestClient(app);signup(client,"prefs-invalid@example.com")
 assert client.patch("/api/account/preferences",json={"theme":"neon"}).status_code==422
 assert client.patch("/api/account/preferences",json={"report_language":"fr"}).status_code==422
 assert client.patch("/api/account/preferences",json={"dasha_year_convention":"28_day_lunar"}).status_code==422
 assert client.patch("/api/account/preferences",json={"matching_ruleset":"made_up_ruleset"}).status_code==422
 assert client.patch("/api/account/preferences",json={"theme":"dark","nickname":"nope"}).status_code==422
 token=client.headers.pop("X-CSRF-Token")
 assert client.patch("/api/account/preferences",json={"theme":"dark"}).status_code==403
 client.headers["X-CSRF-Token"]=token

def admin_client(email="admin@example.com"):
 client=TestClient(app);signup(client,email)
 with TestingSession() as db:
  db.scalar(select(User).where(User.email==email)).role="admin";db.commit()
 return client

def register_pending(email,password="correct horse battery staple"):
 client=TestClient(app)
 registered=client.post("/api/auth/register",json={"full_name":"Pending Person","email":email,"password":password,"accept_terms":True})
 assert registered.status_code==201 and "administrator" in registered.json()["message"]
 assert client.post("/api/auth/verify-email",json={"token":registered.json()["development_token"]}).status_code==200
 return client,registered.json()["user"]["id"]

def test_self_registered_account_waits_for_admin_approval():
 applicant,user_id=register_pending("applicant@example.com")
 pending=applicant.post("/api/auth/login",json={"email":"applicant@example.com","password":"correct horse battery staple"})
 assert pending.status_code==403 and pending.json()["detail"]=="Your account is awaiting administrator approval"
 admin=admin_client()
 assert [u["email"] for u in admin.get("/api/admin/users",params={"status":"pending"}).json()]==["applicant@example.com"]
 approved=admin.post(f"/api/admin/users/{user_id}/approve")
 assert approved.status_code==200 and approved.json()["status"]=="approved"
 logged=applicant.post("/api/auth/login",json={"email":"applicant@example.com","password":"correct horse battery staple"})
 assert logged.status_code==200 and logged.json()["user"]["approved"] is True
 with TestingSession() as db:
  user=db.get(User,user_id);admin_id=db.scalar(select(User.id).where(User.email=="admin@example.com"))
  assert user.approved_by_id==admin_id
  assert db.scalar(select(AuditEvent).where(AuditEvent.event_type=="admin.user_approve")).user_id==admin_id

def test_admin_endpoints_reject_anonymous_regular_users_and_missing_csrf():
 _,user_id=register_pending("someone@example.com")
 assert TestClient(app).get("/api/admin/users").status_code==401
 regular=TestClient(app);signup(regular,"regular@example.com")
 assert regular.get("/api/admin/users").status_code==403 and regular.get("/api/admin/summary").status_code==403
 assert regular.post(f"/api/admin/users/{user_id}/approve").status_code==403
 admin=admin_client();admin.headers.pop("X-CSRF-Token")
 assert admin.post(f"/api/admin/users/{user_id}/approve").status_code==403
 with TestingSession() as db:assert db.get(User,user_id).approved_at is None

def test_unapproved_session_is_rejected_even_if_one_exists():
 applicant,user_id=register_pending("sneaky@example.com")
 with TestingSession() as db:
  db.get(User,user_id).approved_at=utcnow();db.commit()
 logged=applicant.post("/api/auth/login",json={"email":"sneaky@example.com","password":"correct horse battery staple"});assert logged.status_code==200
 with TestingSession() as db:
  db.get(User,user_id).approved_at=None;db.commit()
 response=applicant.get("/api/auth/me")
 assert response.status_code==401 and response.json()["detail"]=="Your account is awaiting administrator approval"

def test_deactivation_revokes_sessions_and_reactivation_restores_access():
 member=TestClient(app);user=signup(member,"member@example.com")
 admin=admin_client()
 assert admin.post(f"/api/admin/users/{user['id']}/deactivate").json()["status"]=="inactive"
 assert member.get("/api/auth/me").status_code==401
 assert member.post("/api/auth/login",json={"email":"member@example.com","password":"correct horse battery staple"}).status_code==403
 assert admin.post(f"/api/admin/users/{user['id']}/approve").status_code==409
 assert admin.post(f"/api/admin/users/{user['id']}/reactivate").json()["status"]=="approved"
 assert member.post("/api/auth/login",json={"email":"member@example.com","password":"correct horse battery staple"}).status_code==200

def test_admins_cannot_deactivate_themselves_or_other_admins():
 admin=admin_client();other=admin_client("second-admin@example.com")
 with TestingSession() as db:
  ids={email:db.scalar(select(User.id).where(User.email==email)) for email in ("admin@example.com","second-admin@example.com")}
 assert admin.post(f"/api/admin/users/{ids['admin@example.com']}/deactivate").status_code==400
 assert admin.post(f"/api/admin/users/{ids['second-admin@example.com']}/deactivate").status_code==409
 assert admin.post("/api/admin/users/999999/approve").status_code==404

def test_summary_counts_and_status_filters():
 register_pending("waiting-one@example.com");register_pending("waiting-two@example.com")
 member=TestClient(app);member_user=signup(member,"approved-member@example.com")
 admin=admin_client();admin.post(f"/api/admin/users/{member_user['id']}/deactivate")
 assert admin.get("/api/admin/summary").json()=={"pending":2,"approved":1,"inactive":1,"all":4}
 assert {u["email"] for u in admin.get("/api/admin/users",params={"status":"inactive"}).json()}=={"approved-member@example.com"}
 assert admin.get("/api/admin/users",params={"status":"bogus"}).status_code==422

def test_newly_approved_user_sees_only_their_own_profiles_and_cannot_reach_the_admins():
 admin=admin_client();place=location(admin)["id"]
 admin_profiles=[profile(admin,place),profile(admin,place)]
 newcomer,newcomer_id=register_pending("newcomer@example.com")
 assert admin.post(f"/api/admin/users/{newcomer_id}/approve").status_code==200
 logged=newcomer.post("/api/auth/login",json={"email":"newcomer@example.com","password":"correct horse battery staple"})
 newcomer.headers["X-CSRF-Token"]=logged.json()["csrf_token"]
 listing=newcomer.get("/api/birth-profiles")
 assert listing.json()==[] and listing.headers["x-total-count"]=="0"
 for theirs in admin_profiles:
  pid=theirs["id"]
  for path in (f"/api/birth-profiles/{pid}",f"/api/astrology/birth-profiles/{pid}/calculate",f"/api/dasha/birth-profiles/{pid}",f"/api/divisional/birth-profiles/{pid}/d9",f"/api/divisional/birth-profiles/{pid}/d10"):
   assert newcomer.get(path).status_code==404,path
  assert newcomer.patch(f"/api/birth-profiles/{pid}",json={"full_name":"Taken"}).status_code==404
  assert newcomer.delete(f"/api/birth-profiles/{pid}").status_code==404
  for path in ("/api/reports/kundli","/api/reports/preview"):
   assert newcomer.post(path,json={"profile_id":pid,"language":"en"}).status_code==404
 mine=profile(newcomer,place)
 assert [item["id"] for item in newcomer.get("/api/birth-profiles").json()]==[mine["id"]]
 pair={"partner_one_profile_id":admin_profiles[0]["id"],"partner_two_profile_id":mine["id"],"partner_one_role":"bride","partner_two_role":"groom"}
 assert newcomer.post("/api/matching/birth-profiles",json=pair).status_code==404
 assert newcomer.post("/api/reports/matching",json=pair).status_code==404
 assert [p["full_name"] for p in newcomer.get("/api/account/export").json()["birth_profiles"]]==["Private Person"] and len(newcomer.get("/api/account/export").json()["birth_profiles"])==1
 assert {item["id"] for item in admin.get("/api/birth-profiles").json()}=={p["id"] for p in admin_profiles}
 assert admin.get(f"/api/birth-profiles/{mine['id']}").status_code==404
 with TestingSession() as db:
  assert db.get(BirthProfile,admin_profiles[0]["id"]).full_name=="Private Person" and db.get(BirthProfile,admin_profiles[0]["id"]).user_id!=newcomer_id

def test_approval_requirement_can_be_disabled_by_configuration():
 original=app.state.settings;app.state.settings=replace(original,require_admin_approval=False)
 try:
  client=TestClient(app)
  registered=client.post("/api/auth/register",json={"full_name":"Open","email":"open@example.com","password":"correct horse battery staple","accept_terms":True})
  assert "administrator" not in registered.json()["message"]
  client.post("/api/auth/verify-email",json={"token":registered.json()["development_token"]})
  assert client.post("/api/auth/login",json={"email":"open@example.com","password":"correct horse battery staple"}).status_code==200
 finally:
  app.state.settings=original
