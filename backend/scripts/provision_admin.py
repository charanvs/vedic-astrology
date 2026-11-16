"""Explicit local-only administrator provisioning. Never accepts a password argument."""
import argparse,getpass
from sqlalchemy import select
from app.core.config import get_settings
from app.core.security import hash_password,normalize_email
from app.db.session import SessionLocal
from app.models import AuditEvent,User

def main():
 parser=argparse.ArgumentParser();parser.add_argument("--email",required=True);parser.add_argument("--name",required=True);args=parser.parse_args()
 settings=get_settings()
 if settings.environment!="development":raise SystemExit("Refusing: APP_ENV must be development")
 password=getpass.getpass("New administrator password: ");confirmation=getpass.getpass("Confirm password: ")
 if password!=confirmation:raise SystemExit("Passwords do not match")
 email=normalize_email(args.email)
 with SessionLocal() as db:
  user=db.scalar(select(User).where(User.email==email))
  if user:
   user.full_name=args.name.strip();user.password_hash=hash_password(password);user.role="admin";user.is_active=True
  else:user=User(full_name=args.name.strip(),email=email,password_hash=hash_password(password),role="admin",is_active=True);db.add(user);db.flush()
  db.add(AuditEvent(user_id=user.id,event_type="admin.provision",outcome="success",detail="local CLI"))
  db.commit()
 print(f"Administrator provisioned for {email}; email verification remains required.")
if __name__=="__main__":main()
