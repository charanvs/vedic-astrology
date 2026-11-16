"""Restore the Step 14 backup into a disposable, exact-name local database."""
import os,subprocess
from pathlib import Path
import pymysql
NAME="vedic_astrology_step14_restore_check"
DUMP=Path(__file__).resolve().parents[2]/"backups"/"vedic_astrology_pre_step14.sql"
MYSQL=Path(r"C:\wamp64\bin\mysql\mysql8.4.7\bin\mysql.exe")
host=os.environ["STEP14_ADMIN_HOST"];port=int(os.environ.get("STEP14_ADMIN_PORT","3306"));user=os.environ["STEP14_ADMIN_USER"];password=os.environ["STEP14_ADMIN_PASSWORD"]
if host not in {"127.0.0.1","localhost"}:raise SystemExit("Refusing non-local MySQL host")
if not DUMP.is_file() or not MYSQL.is_file():raise SystemExit("Dump or mysql client is missing")
connection=pymysql.connect(host=host,port=port,user=user,password=password,autocommit=True)
created=False
try:
 with connection.cursor() as cursor:
  cursor.execute("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME=%s",(NAME,))
  if cursor.fetchone():raise SystemExit("Disposable restore database already exists; refusing to alter it")
  cursor.execute(f"CREATE DATABASE `{NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");created=True
 env={**os.environ,"MYSQL_PWD":password}
 with DUMP.open("rb") as source:
  subprocess.run([str(MYSQL),"--host",host,"--port",str(port),"--user",user,NAME],stdin=source,env=env,check=True)
 with connection.cursor() as cursor:
  cursor.execute(f"SELECT COUNT(*) FROM `{NAME}`.birth_profiles");profiles=cursor.fetchone()[0]
  cursor.execute(f"SELECT version_num FROM `{NAME}`.alembic_version");revision=cursor.fetchone()[0]
  cursor.execute(f"CHECK TABLE `{NAME}`.users,`{NAME}`.locations,`{NAME}`.birth_profiles");checks=cursor.fetchall()
 if not checks or any(row[3]!="OK" for row in checks):raise SystemExit("CHECK TABLE failed")
 print(f"Restore verified: revision={revision}, birth_profiles={profiles}, checked_tables={len(checks)}")
finally:
 if created:
  with connection.cursor() as cursor:cursor.execute(f"DROP DATABASE `{NAME}`")
 connection.close()
 if created:print("Disposable restore database removed.")
