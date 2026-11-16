from datetime import timedelta
import uuid
from app.core.security import hash_token
from app.models import AuthSession,User
from app.models.entities import utcnow
def authenticate(client,session_factory,app):
 raw="test-"+uuid.uuid4().hex;csrf="csrf-"+uuid.uuid4().hex;now=utcnow()
 with session_factory() as db:
  user=User(full_name="Synthetic User",email=uuid.uuid4().hex+"@example.test",password_hash="test-only",email_verified_at=now,approved_at=now,is_active=True,role="user")
  db.add(user);db.flush();db.add(AuthSession(public_id=str(uuid.uuid4()),token_hash=hash_token(raw),csrf_hash=hash_token(csrf),user_id=user.id,created_at=now,last_activity_at=now,expires_at=now+timedelta(hours=1),absolute_expires_at=now+timedelta(hours=2)));db.commit();user_id=user.id
 client.cookies.set(app.state.settings.session_cookie_name,raw);client.headers["X-CSRF-Token"]=csrf
 return user_id
