# ASEEL | أصيل — Perfume Authentication Prototype

ASEEL is a university capstone prototype for the UAE perfume market. It is **not** a perfume shop. Customers scan a unique QR code on a box or bottle and compare the authentication record with the physical packaging.

Project folder: `C:\Users\zooz1\ASEEL`

Anyone can **verify** a product (scan or type a code). Only admins log in to register perfumes and print QR tags.

---

## Put ASEEL on the internet (public website)

`http://127.0.0.1:5000` only works on this computer. For any visitor (and phone camera scanning) you need a public **https://** address.

The easiest free option **without installing Git** is **PythonAnywhere**. Render is also fine if you already use GitHub.

### Option B1 — PythonAnywhere (recommended on this PC)

1. Create a free account: https://www.pythonanywhere.com
2. Open the **Files** tab → **Upload a file**. Upload these from `C:\Users\zooz1\ASEEL` into a folder named `ASEEL` (create the folder first):
   - `app.py`, `config.py`, `database.py`, `seed.py`, `auth.py`, `helpers.py`, `qr_service.py`
   - `requirements.txt`
   - the `routes` folder, `templates` folder, and `static` folder (including `static/img/aseel-logo.jpg`)
   - Do **not** upload `.venv` or `.env`
3. Open the **Bash** console and run:

```bash
cd ASEEL
pip3.10 install --user -r requirements.txt
```

4. Open **Web** → **Add a new web app** → **Manual configuration** → Python 3.10.
5. In the WSGI configuration file, replace the file contents with `pythonanywhere_wsgi.py` from this project, then change `YOURUSERNAME` to your PythonAnywhere username.
6. Reload the web app.

Your public site will be:

**https://YOURUSERNAME.pythonanywhere.com**

7. In PythonAnywhere **Files**, create `.env` inside `ASEEL` with:

```
SECRET_KEY=a-long-random-string
ADMIN_EMAIL=admin@aseel.ae
ADMIN_PASSWORD=AseelAdmin2026!
FLASK_DEBUG=0
BASE_URL=https://YOURUSERNAME.pythonanywhere.com
```

8. Reload the web app again.
9. On your laptop, log in at `https://YOURUSERNAME.pythonanywhere.com/login`, open each perfume, and **Print sticker** / **Download PNG**. Stick the new QR on the box. Those QRs now open the live ASEEL page on any phone (Wi‑Fi or mobile data).

### Option B2 — Render (needs GitHub)

### 1. Put the project on GitHub

1. Create a GitHub account if you do not have one: https://github.com
2. Create a new repository named `ASEEL` (public is fine for a prototype)
3. Upload everything in `C:\Users\zooz1\ASEEL` **except** `.venv`, `.env`, and `aseel.db`  
   (GitHub Desktop is the simplest on Windows)

Do not upload admin passwords in `.env`. Use Render’s Environment variables instead.

### 2. Create a Render web service

1. Open https://render.com and sign up (GitHub login is easiest)
2. **New +** → **Web Service** → connect the `ASEEL` repository
3. Use these settings:

| Setting | Value |
|---|---|
| Runtime | Python |
| Build command | `pip install -r requirements.txt` |
| Start command | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4` |
| Instance | Free |

4. Add environment variables:

| Key | Value |
|---|---|
| `SECRET_KEY` | a long random string |
| `ADMIN_EMAIL` | `admin@aseel.ae` |
| `ADMIN_PASSWORD` | `AseelAdmin2026!` (change this) |
| `FLASK_DEBUG` | `0` |
| `BASE_URL` | leave empty for the first deploy |

5. Click **Create Web Service** and wait until it says Live.

You will get a URL like:

**https://aseel.onrender.com**

That is the public website. Visitors open it, tap **Scan or Verify Product**, and scan the QR with the phone camera. No login is required for that.

### 3. Point QR codes at the public URL

1. In Render → Environment, set:

```
BASE_URL=https://YOUR-SERVICE.onrender.com
```

(no trailing slash)

2. Save. Render will redeploy.
3. Log in to `/login`, open each product, and **Download PNG** / **Print sticker** again so the QR contains the public https link.
4. Old QR codes that still say `127.0.0.1` will not work on a phone.

### Notes about the free plan

- The site may sleep after idle time. The first visit can take 30–60 seconds.
- SQLite (`aseel.db`) can reset if Render rebuilds the server. Re-register products if that happens, or add a paid persistent disk later.
- Phone **camera** scanning needs HTTPS. Render provides that. It will not work on `http://127.0.0.1` from a phone.

### After it is live, visitors do this

1. Open the public URL (or scan a printed ASEEL QR)
2. Allow camera if asked, or type the unique code
3. Compare the on-screen record with the physical box

Admin login stays private at `/login`.

---

## How to run it again on this PC (Windows)

You need **Python 3** installed. Use **PowerShell**.

### Every later time (venv already exists)

This is the usual case after the first setup.

```powershell
cd C:\Users\zooz1\ASEEL
.\.venv\Scripts\Activate.ps1
python app.py
```

Then open:

**http://127.0.0.1:5000**

You should see `Running on http://127.0.0.1:5000` in the terminal. Leave that window open while you use the site.

**Stop the app:** click the terminal and press `Ctrl+C`.

### First time only (or if `.venv` is missing)

```powershell
cd C:\Users\zooz1\ASEEL
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python app.py
```

Then open **http://127.0.0.1:5000**

If `Activate.ps1` is blocked, run this once, then try activate again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

You can also skip activate and run:

```powershell
cd C:\Users\zooz1\ASEEL
.\.venv\Scripts\python.exe app.py
```

### If the page does not open

- Confirm the terminal still shows Flask running.
- Use `http://127.0.0.1:5000`, not `https`.
- If port 5000 is already in use, close the old ASEEL window (`Ctrl+C`) or close Cursor’s old terminal that is still running `python app.py`, then start it again.
- The database file `aseel.db` is created automatically. Do not delete it unless you want a fresh demo (seed products will be recreated).

---

## Admin login

- Email: `admin@aseel.ae`
- Password: `AseelAdmin2026!`

Change these in `.env` before a public demo.

Useful pages:

| Page | URL |
|---|---|
| Home | http://127.0.0.1:5000/ |
| How it works | http://127.0.0.1:5000/how-it-works |
| Verify | http://127.0.0.1:5000/verify |
| Admin login | http://127.0.0.1:5000/login |
| Dashboard (after login) | http://127.0.0.1:5000/admin/ |

---

## What you can demonstrate

1. Log in as admin
2. Register a perfume unit
3. Generate a unique QR code
4. Scan the QR code on a phone
5. See the authentication details
6. Compare them with a physical box
7. Watch the scan count increase
8. See a warning after more than 5 scans
9. See **Product Not Verified** for a fake code

---

## Phone scanning

The app listens on all interfaces (`0.0.0.0:5000`) so a phone on the **same Wi-Fi** can open it.

1. Find your PC’s IPv4 address (for example `192.168.1.10`). In PowerShell:

```powershell
ipconfig
```

Look for **IPv4 Address** under your Wi-Fi adapter.

2. Put this in `.env` (use your real IP):

```
BASE_URL=http://192.168.1.10:5000
```

3. Stop the app with `Ctrl+C` and start it again (`python app.py`).
4. Log in, open a perfume, and download or print a **new** QR code (old QR images may still point at localhost).
5. Scan with your phone camera.

Windows Firewall may ask to allow Python on the private network — allow it.

---

## Seed products

These records are created automatically the first time the app runs (or after you delete `aseel.db`):

| Perfume | Brand | Serial | Demo code |
|---|---|---|---|
| Royal Oud | Super Oud | SO-000001 | `ASEEL-ROYAL-OUD-001` |
| Desert Musk | Al Noor Perfumes | AN-000002 | `ASEEL-DESERT-MUSK-002` |
| Amber Night | Oud House | OH-000003 | `ASEEL-AMBER-NIGHT-003` |

Authentic example: http://127.0.0.1:5000/verify/ASEEL-ROYAL-OUD-001

Fake example: http://127.0.0.1:5000/verify/FAKE-123

Scan **Amber Night** more than 5 times to show the authenticity warning.

---

## Verification rules

When someone opens `/verify/<uniqueCode>`:

- **Not found** → red *Product Not Verified*, invalid scan logged
- **Disabled** → red *Code Disabled*, scan logged
- **Found and scan count ≤ 5** → green *Authentic Product*
- **Found and scan count > 5** → orange *Authenticity Warning* (record is also marked Suspicious)

The scan count increases every time the public URL is opened. Customers do not create accounts.

On a product page you can **Reset scan count** to replay authentic → warning.

---

## Admin extras for the demo

- **How it works** — 2-minute demo script
- Search and filter registered units
- Export registered units as CSV
- **Scan activity** — full audit trail
- Disable a code, mark Suspicious, or restore Genuine

---

## Project layout

- `app.py` — Flask entry point (`python app.py`)
- `requirements.txt` — Python packages
- `.env.example` — copy to `.env` for admin email/password and `BASE_URL`
- `database.py` — SQLite tables (`perfumes`, `scan_logs`, `invalid_scan_logs`)
- `routes/public.py` — home and verification
- `routes/admin.py` — dashboard, register, QR, edit, status
- `routes/auth.py` — admin login
- `static/img/aseel-logo.jpg` — official ASEEL logo
- `aseel.db` — created on first run
