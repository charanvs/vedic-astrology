"""Grant only the permission required by the profile DELETE endpoint."""
import os,re,pymysql
def safe(value:str)->str:
 if not re.fullmatch(r"[A-Za-z0-9_]+",value):raise SystemExit("Unsafe identifier")
 return value
host=os.environ["STEP14_ADMIN_HOST"];port=int(os.environ.get("STEP14_ADMIN_PORT","3306"))
admin=os.environ["STEP14_ADMIN_USER"];password=os.environ["STEP14_ADMIN_PASSWORD"]
database=safe(os.environ.get("DB_NAME","vedic_astrology"));runtime=safe(os.environ.get("DB_USER","vedic_app"))
if host not in {"127.0.0.1","localhost"}:raise SystemExit("Refusing non-local MySQL host")
with pymysql.connect(host=host,port=port,user=admin,password=password,autocommit=True) as connection:
 with connection.cursor() as cursor:
  cursor.execute(f"GRANT DELETE ON `{database}`.`birth_profiles` TO %s@%s",(runtime,"localhost"))
print("Granted DELETE on the local birth_profiles table to the runtime account.")
