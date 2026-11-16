"""Promote an existing account to administrator; dry-run unless --apply is supplied."""
import argparse
from sqlalchemy import select
from app.core.config import get_settings
from app.core.security import normalize_email
from app.db.session import SessionLocal
from app.models import AuditEvent, User
from app.models.entities import utcnow


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if get_settings().environment != "development": raise SystemExit("Refusing: APP_ENV must be development")
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == normalize_email(args.email)))
        if not user: raise SystemExit("No account exists for that email")
        print(f"Account {user.id} ({user.full_name}) currently has role '{user.role}', active={user.is_active}.")
        if not args.apply:
            print("Dry run only. Re-run with --apply to grant administrator access.")
            return
        user.role, user.is_active = "admin", True
        user.approved_at = user.approved_at or utcnow()
        db.add(AuditEvent(user_id=user.id, event_type="admin.grant", outcome="success", detail="local CLI"))
        db.commit()
        print(f"Account {user.id} is now an administrator.")


if __name__ == "__main__":
    main()
