# Deploying to https://cvstudy.in/astrology (GoDaddy cPanel)

This guide installs the app from the deployment pack (`astrology-app-<version>.zip`) using only cPanel screens: no SSH is needed. Your main website and other apps are not touched; everything lives in one new folder and one new database.

Allow about an hour the first time.

## Before you start

Check these in cPanel:

1. **Setup Python App** appears under *Software*, and its Python version list includes **3.11**.
   The astronomy engine only installs on Python 3.11. If 3.11 is not offered, stop and ask GoDaddy support to enable it.
2. **SSL is active** for cvstudy.in (the site opens with `https://`).
3. **No folder or file named `astrology` exists inside `public_html`.** The app takes over the `/astrology` address; an existing folder there would clash.

## Part 1: Create the database

1. cPanel → **MySQL® Databases**.
2. *Create New Database*: type `astrology` → **Create Database**. cPanel adds your username prefix, e.g. `cvstudy_astrology`. Note the full name.
3. *MySQL Users → Add New User*: username `astro`, click **Password Generator**, copy the password somewhere safe → **Create User**. Note the full username, e.g. `cvstudy_astro`.
4. *Add User To Database*: choose the user and the database → **Add** → tick **ALL PRIVILEGES** → **Make Changes**.
5. cPanel → **phpMyAdmin** → click the new database in the left list → **Import** tab → *Choose File* → select `schema.sql` from the pack (unzip it on your computer first) → **Import**.
6. You should see "Import has been successfully finished" and these tables: `account_tokens`, `alembic_version`, `audit_events`, `auth_sessions`, `birth_profiles`, `locations`, `rate_limit_counters`, `users`.

## Part 2: Upload the app

1. cPanel → **File Manager**. Stay in your **home folder** (the top level, *not* `public_html`).
2. **+ Folder** → name it `astrology_app`.
3. Open `astrology_app` → **Upload** → choose `astrology-app-<version>.zip` → wait for 100% → go back.
4. Right-click the zip → **Extract** → extract into `/home/<your-username>/astrology_app`.
5. Check the folder now contains `passenger_wsgi.py`, `app`, `frontend_dist`, `deploy`, `requirements.txt` and `.env.example`. (To see files starting with a dot: *Settings* (top right) → tick **Show Hidden Files**.)
6. Delete the zip from the folder.

## Part 3: Enter the settings

1. In `astrology_app`, right-click `.env.example` → **Copy** → name the copy `.env`.
2. Right-click `.env` → **Edit**, and fill in:
   - `DB_NAME=` the full database name from Part 1 (e.g. `cvstudy_astrology`)
   - `DB_USER=` the full username (e.g. `cvstudy_astro`)
   - `DB_PASSWORD=` the generated password
3. Leave everything else as it is for now and **Save Changes**.

The `.env` file holds your passwords. It is never part of the published source code.

## Part 4: Create the Python app

1. cPanel → **Setup Python App** → **Create Application**:
   - *Python version*: **3.11.x**
   - *Application root*: `astrology_app`
   - *Application URL*: choose `cvstudy.in` and type `astrology`
   - *Application startup file*: `passenger_wsgi.py`
   - *Application Entry point*: `application`
   - *Passenger log file*: `/home/<your-username>/astrology_app/passenger.log`
2. Click **Create**. cPanel creates the app and a small `.htaccess` inside `public_html/astrology`; leave that file alone.
3. On the same page, under *Configuration files*, type `requirements.txt` → **Add** → **Run Pip Install**. This downloads the libraries and can take several minutes.
4. Under *Execute python script*, type `deploy/check_server.py` → **Run Script**. Read the result:
   - `READY` with only warnings is fine.
   - `WARN AGPL source link`: expected until Part 6.
   - `WARN PDF reports`: the server lacks the system libraries for PDFs. Reports still work: the Reports page opens them as a print-ready page, and readers choose **Save as PDF** in the print dialog. See *Troubleshooting*.
   - Any `FAIL`: fix it before continuing (see *Troubleshooting*).
5. Click **Restart** at the top of the app page.
6. Open **https://cvstudy.in/astrology**. The dashboard should appear.

## Part 5: Make your account the administrator

1. Open https://cvstudy.in/astrology/register and create your account. You will see that it is awaiting approval. That is expected, because there is no administrator yet.
2. cPanel → **phpMyAdmin** → your database → **SQL** tab → run (with your own email):

   ```sql
   UPDATE users SET role = 'admin', approved_at = UTC_TIMESTAMP() WHERE email = 'your-email@example.com';
   ```

   It should report "1 row affected".
3. Sign in. **Administration** now appears in the menu; approve other people's registrations there.

## Part 6: Publish the source code (AGPL licence)

The astronomy engine (Swiss Ephemeris, free edition) is licensed under the GNU AGPL v3, so the app's source code must be available to its users.

1. Publish the project to a public repository (for example GitHub). The `.gitignore` already excludes `.env`, passwords, backups and build folders.
2. Edit `astrology_app/.env`: `SOURCE_CODE_URL=https://github.com/<you>/<repository>` → Save.
3. Setup Python App → **Restart**. The footer's *Source code* link now opens the repository.
4. Whenever you deploy a new version, publish the matching code too.

## Optional: email for "Forgot password"

Without email settings the site works, but password-reset emails are not sent. To enable them:

1. cPanel → **Email Accounts** → create e.g. `noreply@cvstudy.in` → *Connect Devices* shows the *Outgoing Server* and port.
2. In `.env`: `SMTP_HOST` (e.g. `mail.cvstudy.in`), `SMTP_PORT=465`, `SMTP_USERNAME=noreply@cvstudy.in`, `SMTP_PASSWORD`, `SMTP_FROM=noreply@cvstudy.in` → Save → **Restart**.
3. Only after password-reset emails work, you may set `REQUIRE_VERIFIED_EMAIL=true` to require email confirmation on sign-up.

## Updating to a new version later

1. **Back up first**: phpMyAdmin → database → **Export** → *Go* (keep the downloaded `.sql`).
2. Upload the new zip into `astrology_app` and extract it, letting it overwrite existing files. Your `.env` is not in the zip, so it stays.
3. Setup Python App → **Run Pip Install** (in case libraries changed).
4. *Execute python script*: `deploy/migrate.py` (updates the database structure safely), then `deploy/check_server.py`.
5. **Restart**, and publish the matching source code.

## Backups

Export the database from phpMyAdmin regularly (or use cPanel → *Backup*). The database holds all accounts and birth profiles; the app folder can always be rebuilt from the pack.

## Troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| Error page or "Incomplete response" | Run `deploy/check_server.py`; also read `astrology_app/passenger.log` and `stderr.log` in File Manager. |
| `FAIL Python version` | Edit the app in Setup Python App and choose 3.11, then Run Pip Install again. |
| `FAIL Database …` | Check `DB_NAME`, `DB_USER`, `DB_PASSWORD` in `.env` (full names with prefix) and that the user has ALL PRIVILEGES. If it says the schema is behind, run `deploy/migrate.py`. |
| `FAIL Built website pages` | The zip was extracted into the wrong folder; `frontend_dist` must sit directly inside `astrology_app`. |
| `https://cvstudy.in/astrology` shows 404 | The Application URL is not `astrology`, or an old `astrology` folder in `public_html` is in the way. |
| "Invalid host header" | Add the address you used to `TRUSTED_HOSTS` in `.env`, then Restart. |
| Sign-in fails with "Cross-origin request rejected" | Add the site origin (e.g. `https://www.cvstudy.in`) to `ALLOWED_CORS_ORIGINS`, then Restart. |
| Reports page shows “This server can't create PDF files yet” | The server's Pango text library is older than 1.44. This is expected on shared hosting: **Open printable report** shows the full report in a new tab and opens the print dialog; choose **Save as PDF**. If nothing opens, allow pop-ups for cvstudy.in. Server-made PDFs only return if the host provides Pango 1.44 or newer. |
| Changes to `.env` have no effect | Every `.env` change needs **Restart** in Setup Python App. |
