<div align="center">

# 🏆 Sport Events Web

**A full-stack web platform for managing and discovering sporting events.**  
Built with **FastAPI** · **SQLAlchemy** · **MySQL** · **Vanilla HTML/CSS/JS**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

## ✨ Features

| Area | Highlights |
|---|---|
| **Auth** | JWT-based login · OTP email verification · Forgot-password flow · bcrypt hashing |
| **Roles** | Admin · Manager · Athlete · Visitor — each with its own dashboard |
| **Events** | Create / edit / delete events · Rich event detail pages · Category & location filters |
| **Tournaments** | Full tournament management with teams and brackets |
| **Teams** | Team CRUD · assign athletes · manager ownership |
| **Athletes** | Sport preferences · personal calendar · player profile pages |
| **Admin Panel** | User management · role assignment · manager creation |
| **Email** | Gmail SMTP integration — registration confirmation, OTP, password reset |
| **Media** | Photo & file upload endpoints with static file serving |
| **API Docs** | Swagger UI at `/docs` · ReDoc at `/redoc` |

---

## 🗂️ Project Structure

```
SportEventsWeb/
├── main.py                  # FastAPI app entry point
├── start.bat                # One-click Windows setup & launcher
├── database_setup.sql       # Complete MySQL schema (run once)
│
├── backend/
│   ├── .env.example         # ← copy to .env and fill in your values
│   ├── requirements.txt
│   ├── database.py          # SQLAlchemy engine & session
│   ├── models.py            # ORM models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── auth_utils.py        # JWT helpers, password hashing
│   ├── email_service.py     # Gmail SMTP helpers
│   ├── fix_plaintext_passwords.py  # One-off migration utility
│   └── routers/
│       ├── auth_router.py
│       ├── events_router.py
│       ├── admin_router.py
│       └── comments_router.py
│
├── frontend/
│   ├── index.html           # Landing / redirect page
│   ├── css/style.css
│   ├── js/api.js            # Centralised API client
│   └── pages/
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── event-detail.html
│       ├── tournaments.html
│       ├── player-profile.html
│       ├── athlete-calendar.html
│       ├── athlete-preferences.html
│       ├── profile-settings.html
│       ├── admin-dashboard.html
│       ├── admin-users.html
│       ├── admin-teams.html
│       ├── admin-tournaments.html
│       ├── admin-manager-create.html
│       ├── role-selection.html
│       ├── forgot-password.html
│       ├── verify-otp.html
│       └── visitor-preferences.html
│
├── uploads/                 # User-uploaded event images (git-ignored)
└── photos/                  # User profile photos (git-ignored)
```

---

## ⚙️ Prerequisites

| Tool | Version |
|---|---|
| Python | 3.10 + |
| MySQL | 8.0 + |
| pip | latest |

---

## 🚀 Quick Start

### 1 — Clone the repository

```bash
git clone https://github.com/<your-username>/SportEventsWeb.git
cd SportEventsWeb
```

### 2 — Create the MySQL database

Run the **single** setup file — it creates the database and all tables in one step:

```bash
mysql -u root -p < database_setup.sql
```

### 3 — Configure environment variables

```bash
copy backend\.env.example backend\.env   # Windows
# cp backend/.env.example backend/.env  # macOS / Linux
```

Open `backend/.env` and fill in your values:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=sport_events

SECRET_KEY=<run: python -c "import secrets; print(secrets.token_hex(32))">
ACCESS_TOKEN_EXPIRE_MINUTES=1440

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password   # Gmail App Password
EMAIL_FROM=your-email@gmail.com

FRONTEND_URL=http://localhost:8000
```

> **Gmail App Password**: Go to [Google Account → Security → App Passwords](https://myaccount.google.com/apppasswords) and generate a 16-character password. Do **not** use your regular Gmail password.

### 4 — Start the server

**Windows (recommended):**

```bat
start.bat
```

This script automatically creates the virtual environment, installs dependencies, and starts the server.

**Manual / macOS / Linux:**

```bash
python -m venv backend/venv
# Windows:
backend\venv\Scripts\activate
# macOS/Linux:
source backend/venv/bin/activate

pip install -r backend/requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5 — Open the app

| URL | Description |
|---|---|
| `http://localhost:8000` | Main frontend |
| `http://localhost:8000/docs` | Swagger API docs |
| `http://localhost:8000/redoc` | ReDoc API docs |
| `http://localhost:8000/pages/admin-dashboard.html` | Admin panel |

---

## 🔐 Security Notes

- **Never commit `backend/.env`** — it is listed in `.gitignore`.
- Rotate `SECRET_KEY` before deploying to production.
- Use a dedicated MySQL user with limited privileges instead of `root` in production.
- Email App Passwords should be kept secret and can be revoked at any time from your Google Account.

---

## 🛠️ API Overview

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login, returns JWT |
| `POST` | `/auth/verify-otp` | Verify email OTP |
| `POST` | `/auth/forgot-password` | Request password reset |
| `GET` | `/events/` | List all events |
| `POST` | `/events/` | Create event (auth required) |
| `GET` | `/events/{id}` | Event detail |
| `GET` | `/admin/users` | List users (admin) |
| `GET` | `/api/health` | Health check |

Full interactive docs available at `/docs`.

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "feat: add my feature"`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.
