# 🫙 MoneyJar

A digital money management platform where you divide your income into goal-based savings jars — Emergency, Travel, Laptop, whatever you're saving for — and track progress with an AI-style spending insight.

> Stage 1 MVP: budgeting/savings tracker. Jars are virtual allocations, not real bank transfers — no banking or payment integration is included.

## Features

- Register / log in (Flask-Login, hashed passwords)
- First-time setup: income, pocket money, money owed to others, and current savings — shown on the dashboard, editable anytime
- Dashboard: total balance, this month's spending, money saved in jars, category spending chart
- Rule-based spending insight comparing this month's top category to last month
- Create jars with a target amount, optional monthly target, and emoji; deposit, withdraw, and track progress with an ETA
- Income/expense transactions with categories and full history
- Import transactions from a Paytm (or any bank/UPI app) statement export (CSV/Excel) — auto-categorized, duplicate-safe
- CSRF-protected forms
- Installable as a home-screen app on iOS/Android (PWA — manifest, icons, service worker)

## Tech stack

- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **Database:** SQLite by default (swap `DATABASE_URL` for Postgres — see below)
- **Frontend:** Server-rendered Jinja templates, vanilla CSS, Chart.js

## Getting started

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then edit SECRET_KEY
python app.py
```

The app runs at `http://localhost:5050`. The SQLite database (`moneyjar.db`) and tables are created automatically on first run.

### Using PostgreSQL instead of SQLite

Set `DATABASE_URL` in `.env` to a Postgres connection string, e.g.:

```
DATABASE_URL=postgresql://user:password@localhost:5432/moneyjar
```

Note: the dashboard's monthly spending queries use SQLite's `strftime()` — swap those for SQLAlchemy's `extract()` if you move to Postgres (see `backend/routes/dashboard.py`).

## Project structure

```
backend/
  app.py            # app factory, blueprint registration, error handlers
  config.py         # env-based configuration
  models/           # User, Transaction, Jar, JarTransaction
  routes/           # auth, dashboard, jars, transactions blueprints
frontend/
  templates/        # Jinja templates
  static/css/       # styling
```

## Running it on your phone, for free

See [DEPLOY.md](DEPLOY.md) for step-by-step instructions to host this on PythonAnywhere's free tier and install it to your iPhone/Android home screen as an app.

## Roadmap

- **Stage 2:** monthly budgets, recurring expenses, Auto-Jar income splitting, monthly reports
- **Stage 3:** real bank/payment integration via a regulated provider (not a DIY bank-credential store)
