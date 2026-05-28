# Running the E2E test

Prerequisites:

- Backend services running (FastAPI app) on `http://localhost:8000` or set `API_URL` env var.
- MySQL, MongoDB and Redis/Celery available if you want background indexing; however the script only tests API-level persistence and dataset generation.

Quick run (from repo root):

```bash
# Start backend (example)
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, run the test
python scripts/e2e_test.py
```

If your backend is on a different host/port, set the `API_URL` environment variable:

```bash
API_URL=http://127.0.0.1:8000 python scripts/e2e_test.py
```

Seeder (create `Super Admin` role and admin user):

```bash
# from repo root
python backend/scripts/seed_db.py

# optionally set credentials
E2E_ADMIN_EMAIL=admin@elsea.ai E2E_ADMIN_PASSWORD=AdminPass123! python backend/scripts/seed_db.py
```
