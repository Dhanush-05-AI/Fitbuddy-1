# FitBuddy – AI Fitness Plan Generator

FastAPI + Jinja2 + SQLite (SQLAlchemy) + Gemini. Generates a 7-day workout plan and a nutrition/recovery tip, updates the plan from feedback, and includes a password-protected admin dashboard.

## Setup
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then set GOOGLE_API_KEY and ADMIN_PASSWORD
python run.py                   # http://127.0.0.1:8000
```
Admin dashboard: `/view-all-users` (HTTP Basic auth with `ADMIN_USERNAME` / `ADMIN_PASSWORD`; disabled if the password is empty). API docs: `/docs`. Health check: `/health`.

## Tests
```bash
pip install -r requirements-dev.txt
python -m pytest
```

## Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
# or Docker
docker build -t fitbuddy .
docker run -p 8000:8000 --env-file .env -v fitbuddy-data:/data fitbuddy
```
Put it behind HTTPS (Nginx, Caddy, or your host's proxy) so admin credentials are encrypted in transit.

## Structure
```
app/ (main, routes, database, schemas, gemini_client, gemini_generator, gemini_flash_generator)
templates/ (index, result, all_users, error)   static/ (style.css, app.js)
tests/test_app.py   Dockerfile   run.py   requirements*.txt   .env.example
```
