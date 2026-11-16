"""Controlled local ownership recovery; dry-run unless --apply is supplied."""
import argparse
from sqlalchemy import select
from app.core.config import get_settings
from app.core.security import normalize_email
from app.db.session import SessionLocal
from app.models import AuditEvent,BirthProfile,User
def main():
 p=argparse.ArgumentParser();p.add_argument("--email",required=True);p.add_argument("--profile-id",type=int,action="append",required=True);p.add_argument("--apply",action="store_true");args=p.parse_args()
 if get_settings().environment!="development":raise SystemExit("Refusing: APP_ENV must be development")
 with SessionLocal() as db:
  user=db.scalar(select(User).where(User.email==normalize_email(args.email)))
  if not user:raise SystemExit("Target user does not exist")
  rows=db.scalars(select(BirthProfile).where(BirthProfile.id.in_(args.profile_id),BirthProfile.user_id.is_(None))).all()
  if len(rows)!=len(set(args.profile_id)):raise SystemExit("Every requested profile must exist and be unowned")
  print(f"{len(rows)} unowned profile(s) validated for user {user.id}.")
  if not args.apply:print("Dry run only. Re-run with --apply after independent identity review.");return
  for row in rows:row.user_id=user.id
  db.add(AuditEvent(user_id=user.id,event_type="profiles.claim",outcome="success",detail=f"count={len(rows)} local CLI"));db.commit()
  print("Ownership applied.")
if __name__=="__main__":main()
