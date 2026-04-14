# CAFW Full-Stack Starter

This workspace now uses a secure admin-only authentication flow:

- Frontend: React + Vite + Tailwind + Axios + Recharts
- Backend: FastAPI + Uvicorn + SQLAlchemy
- Database: PostgreSQL (or SQLite for quick local testing)
- OTP Store: Redis with expiry and attempt limits
- Auth: bcrypt-hashed password + email OTP + JWT
- Deployment: Render (frontend static + backend web service)

## Folder Structure

- `frontend/` React dashboard app
- `backend/` FastAPI API and firewall middleware

## 1) Backend Setup (Local)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Backend API docs:

- Swagger UI: http://localhost:8000/docs
- Health: http://localhost:8000/health

## 2) Frontend Setup (Local)

```bash
cd frontend
copy .env.example .env
npm install
npm run dev
```

Frontend will run at http://localhost:5173

## 3) Database Switching

Use one environment variable only:

- Local: `DATABASE_URL=sqlite:///./waf.db`
- Production: `DATABASE_URL=postgresql+psycopg://...`

SQLAlchemy code stays the same in both environments.

## 4) Required Environment Variables

Backend `.env` values:

- `SECRET_KEY`
- `DATABASE_URL`
- `REDIS_URL`
- `FRONTEND_ORIGIN`
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD_HASH` or `ADMIN_PASSWORD`
- `OTP_EXPIRE_SECONDS` (default 300)
- `OTP_MAX_ATTEMPTS` (default 3)
- `OTP_LOCK_SECONDS` (default 30)
- `EMAIL_USERNAME`
- `EMAIL_PASSWORD`
- `EMAIL_FROM`

Frontend `.env` values:

- `VITE_API_BASE_URL`

## 5) Render + Supabase Deployment

1. Push repository to GitHub.
2. Create Supabase project and copy PostgreSQL connection string.
3. Deploy backend to Render from `backend/` using `render.yaml`.
4. Set backend env vars in Render:
   - `DATABASE_URL` to Supabase URL
   - `SECRET_KEY` long random string
   - `FRONTEND_ORIGIN` your frontend URL
   - `EMAIL_USERNAME`, `EMAIL_PASSWORD`, `EMAIL_FROM`
5. Deploy frontend to Render static site from `frontend/` using `render.yaml`.
6. Set frontend env var:
   - `VITE_API_BASE_URL` to backend Render URL

## 6) Runtime Commands

Local backend:

```bash
uvicorn app.main:app --reload --port 8000
```

Redis (required for OTP flow):

```bash
docker run -d --name cafw-redis -p 6379:6379 redis:7-alpine
```

Production backend:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Local frontend:

```bash
npm run dev
```

Production frontend build:

```bash
npm run build
```

## 7) Auth Flow

1. Admin submits email + password at `/api/auth/login`.
2. Backend validates bcrypt password from pre-registered admin account.
3. Backend generates a 6-digit OTP, stores hashed OTP in Redis for 5 minutes, and emails it.
4. Admin submits OTP to `/api/auth/verify-otp`.
5. On success, backend issues JWT token.
6. Dashboard endpoints are JWT protected and admin-only.
