# Deploying MoneyJar to your iPhone, for free

Two parts: host the app somewhere always-reachable (PythonAnywhere's free tier), then install it to your Home Screen as an app (PWA).

## 1. Host it on PythonAnywhere (free forever, no card required)

1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com) for a free **Beginner** account.
2. Open a **Bash console** from your dashboard and clone the repo:
   ```bash
   git clone https://github.com/madhusudhan1260/moneyjar.git
   cd moneyjar/backend
   ```
3. Create a virtualenv and install dependencies:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 moneyjar-venv
   pip install -r requirements.txt
   ```
4. Create a real secret key (don't skip this — it signs your login sessions):
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   echo "SECRET_KEY=paste-the-value-above-here" > .env
   ```
5. Go to the **Web** tab → **Add a new web app** → choose **Manual configuration** → pick the Python version matching your virtualenv (3.10).
6. In the web app's settings page, set:
   - **Source code**: `/home/YOUR_USERNAME/moneyjar/backend`
   - **Virtualenv**: `/home/YOUR_USERNAME/.virtualenvs/moneyjar-venv`
   - Leave **Working directory** at its default (`/home/YOUR_USERNAME/`) — it doesn't need to change, since the WSGI file below adds the backend folder to `sys.path` itself.
7. Click the **WSGI configuration file** link and replace its contents with `backend/wsgi_pythonanywhere_template.py` from this repo — just swap `YOUR_USERNAME` for your actual PythonAnywhere username.
8. Click the big green **Reload** button.
9. Your app is now live at `https://YOUR_USERNAME.pythonanywhere.com` — HTTPS included, which is required for the installable app step below.

To ship updates later: `git pull` in the Bash console, then hit **Reload** on the Web tab again.

## 2. Install it on your iPhone as an app

1. Open `https://YOUR_USERNAME.pythonanywhere.com` in **Safari** on your iPhone (must be Safari, not Chrome — iOS only allows Safari to install PWAs).
2. Tap the **Share** button (square with an arrow) in the toolbar.
3. Tap **Add to Home Screen**.
4. Tap **Add**.

You'll get a MoneyJar icon on your home screen that opens full-screen, no browser bar — just like a native app. It's still the same website under the hood, so any updates you push and reload on PythonAnywhere show up next time you open it.

## Notes

- Free PythonAnywhere accounts aren't a one-month trial — they're free forever, but the site auto-disables after 1 month of you not checking in. Log into the dashboard and click **"Run until 1 month from today"** on the Web tab about once a month (PythonAnywhere emails you a reminder a week before it would lapse) to keep it running.
- Your data lives in `backend/moneyjar.db` on PythonAnywhere's persistent disk, so it survives reloads and restarts (unlike some other free hosts that wipe the filesystem).
