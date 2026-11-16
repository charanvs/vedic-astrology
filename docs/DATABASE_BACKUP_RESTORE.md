# Database backup and restore

Use separate runtime and migration users. The runtime user needs only application CRUD on the selected schema; schema changes and backups use a separately controlled operator/migration account. Root credentials must not be placed in `.env`.

Local backup (PowerShell sets `MYSQL_PWD` only for the child process; never echo it):

```powershell
mysqldump.exe --no-tablespaces --single-transaction --routines --triggers --host=127.0.0.1 --port=3306 --user=vedic_migrator --result-file=C:\secure-backups\vedic_astrology.sql vedic_astrology
Get-FileHash -Algorithm SHA256 C:\secure-backups\vedic_astrology.sql
```

Restore only to a newly created isolated validation database:

```powershell
mysql.exe --host=127.0.0.1 --port=3306 --user=restore_operator vedic_astrology_restore_check < C:\secure-backups\vedic_astrology.sql
mysql.exe --host=127.0.0.1 --port=3306 --user=restore_operator -e "CHECK TABLE users, birth_profiles, locations" vedic_astrology_restore_check
```

Never restore over development or production without explicit approval and a rollback plan. Encrypt backup storage, restrict ACLs, keep daily backups for 30 days plus monthly copies as policy permits, and test a representative restore quarterly.

The Step 14 pre-migration dump is ignored under `backups/`. It was restored to the exact disposable local database `vedic_astrology_step14_restore_check`; revision `20261112_02`, all four birth profiles, and `CHECK TABLE` for users/locations/profiles were verified before that disposable database was removed.
