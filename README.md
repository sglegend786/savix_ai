# SAVIX AI – AI-Powered Expense Manager & Financial Planning System

SAVIX AI is a full-stack Flask web application for tracking expenses/income,
predicting expense categories with a machine learning model, managing a
monthly budget, viewing analytics, and exploring/comparing savings &
investment schemes.

## Features

- Email/password authentication + optional "Continue with Google" (OAuth)
- After first Google login, user sets a local password for future logins
- Add / edit / delete transactions (credit or debit)
- ML-based expense category prediction (TF-IDF + Logistic Regression),
  with a keyword-based fallback if the model file is missing
- Dashboard with live summary cards (balance, credit, debit, budget, etc.)
- Credit vs Debit grouped bar chart (single chart, both series together)
- Category-wise doughnut chart, app/platform-wise spending chart
- Monthly analytics: net savings, average transaction, top category/month
- Monthly budget with alert levels (normal / warning / critical / exceeded)
- Rule-based AI spending insights
- Investment schemes stored in the database (FD, RD, SIP, PPF, NSC, POMIS,
  KVP, SCSS, SSY, etc.) with a comparison tool and a return calculator
- Per-user data isolation — every query is filtered by the logged-in user's ID
- Custom 404 / 500 error pages

## Technology Stack

- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js, Bootstrap Icons
- **Backend:** Python 3, Flask, Flask-SQLAlchemy, Flask-Login, Authlib, python-dotenv
- **Database:** SQLite (via SQLAlchemy ORM)
- **ML:** scikit-learn, pandas, numpy, joblib
- **Deployment target:** Render / Railway / PythonAnywhere

## Folder Structure

```
savix_ai/
├── app.py                  # App factory, blueprint registration
├── config.py                # Config loaded from environment variables
├── extensions.py             # db, login_manager, oauth instances
├── models.py                 # SQLAlchemy models
├── init_db.py                 # Creates database tables
├── seed_investments.py         # Seeds sample investment scheme data
├── requirements.txt
├── .env.example
├── .gitignore
├── ml/
│   ├── train_model.py         # Trains the TF-IDF + Logistic Regression model
│   ├── predict.py               # Loads model / falls back to keyword rules
│   └── expense_model.pkl        # Created after running train_model.py
├── routes/
│   ├── auth.py, dashboard.py, transactions.py, analytics.py,
│   │   budget.py, investments.py, profile.py, insights.py
├── templates/
│   ├── base.html, login.html, register.html, set_password.html,
│   │   dashboard.html, transactions.html, analytics.html, budget.html,
│   │   investments.html, compare.html, profile.html, insights.html,
│   │   404.html, 500.html
└── static/
    ├── css/style.css
    └── js/main.js
```

## Installation (Windows + VS Code)

1. **Create and activate a virtual environment**

```
python -m venv venv
venv\Scripts\activate
```

2. **Install dependencies**

```
pip install -r requirements.txt
```

3. **Create your `.env` file**

Copy `.env.example` to `.env` and fill in the values:

```
copy .env.example .env
```

- `SECRET_KEY` — any long random string (used to sign sessions).
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` — only required if you want
  "Continue with Google" to work. Get them from
  https://console.cloud.google.com/apis/credentials:
  1. Create a project → OAuth consent screen → External.
  2. Create OAuth Client ID → Web application.
  3. Add authorized redirect URI: `http://127.0.0.1:5000/auth/google/callback`
  4. Copy the generated Client ID and Client Secret into `.env`.

  If you leave these blank, the app still runs fine — the Google button is
  simply hidden and normal email/password login is used instead.

4. **Initialize the database**

```
python init_db.py
```

5. **Train the ML category-prediction model**

```
python ml/train_model.py
```

This creates `ml/expense_model.pkl`. If you skip this step, the app still
works — it falls back to simple keyword-based category matching.

6. **Seed sample investment schemes**

```
python seed_investments.py
```

7. **Run the application**

```
python app.py
```

8. **Open in your browser**

```
http://127.0.0.1:5000
```

## How to Use

1. Register with your name/email/password, or continue with Google.
2. If you signed in with Google for the first time, you'll be asked to set
   a local password so you can log in with email + password next time too.
3. Add transactions from the Dashboard or Transactions page — the AI will
   suggest a category as you type the description; you can override it.
4. Set your monthly budget on the Budget page.
5. Explore Analytics for the credit vs debit chart, category breakdown,
   and platform-wise spending.
6. Visit Investments to browse schemes, calculate illustrative returns,
   and select 2+ schemes to compare side by side.
7. Update your name/password from Profile.

## Deployment Notes

- **Render / Railway:** set the same environment variables from `.env` in
  the platform's dashboard, set the start command to `gunicorn app:app`
  (add `gunicorn` to requirements.txt for production), and make sure the
  Google OAuth redirect URI is updated to your deployed domain.
- **PythonAnywhere:** upload the project, create a virtualenv, install
  requirements, and point the WSGI file to `app:app`.
- SQLite is fine for a small/demo deployment; for production scale,
  swap `DATABASE_URL` to a managed Postgres/MySQL instance.

## Security Notes

- Passwords are never stored in plain text — only Werkzeug-hashed values.
- Every transaction/budget/investment query is filtered by the logged-in
  user's ID, so users cannot see each other's data.
- Secrets are read from environment variables only, never hardcoded.
- `.env`, the SQLite database file, and the trained `.pkl` model are
  excluded from version control via `.gitignore`.

## Investment Data Disclaimer

Interest rates and scheme details shown in this app are **indicative
sample/reference figures for demo purposes**, not live market data. Always
verify current rates with the official provider (bank, post office, AMC,
etc.) before making any investment decision. Calculators in this app are
illustrative only and do not guarantee returns.

## Future Improvements

- Real-time interest rate feed integration
- CSV/bank statement import with auto-categorization
- Push/email budget alerts
- Multi-currency support
- Recurring transaction templates
