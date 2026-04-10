# CAFW - Centralized Adaptive Firewall

CAFW is a real-time web firewall platform with:

- FastAPI backend and middleware-based firewall engine
- React + Tailwind admin dashboard
- SQLite for logs/rules/users (local file DB)
- Redis for OTP and temporary security state

## Project Structure

- `backend/`: FastAPI API, firewall middleware, authentication, database models
- `frontend/`: React Vite dashboard with charts and controls

## Core Features Implemented

- Middleware request inspection (path, query, headers, body)
- Regex-based attack detection with enable/disable rule switches
- Automatic blocking with `403` response
- Attack logging in SQLite
- Admin login + OTP verification flow
- JWT-protected admin APIs
- Dashboard metrics and visual trend/severity charts
- Paginated attack logs

## Local Dev

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Auth Defaults

- Email: `admin@example.com` (or your `ADMIN_EMAIL` env value)
- Password: Value from `ADMIN_PASSWORD` env variable

OTP codes are printed to backend logs when SMTP is disabled (`SMTP_ENABLED=false`).

## Next Improvements

- Add Redis-backed global rate limiting per IP
- Add account lockout rules after repeated login failures
- Add Alembic migrations
- Add unit and integration tests
- Add WebSocket/SSE for true push-based live updates
