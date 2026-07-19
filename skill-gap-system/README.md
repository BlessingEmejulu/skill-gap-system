# Graduate Skill Gap Prediction System

An AI-powered employability and skill-gap prediction platform for Nigerian
graduates — predicts employability, compares graduate skills against labour
market demand, and recommends personalized learning paths.

This is a **working scaffold**: the data model, auth, REST API, ML pipeline,
and every frontend page are wired together and run end-to-end today. AI
features that depend on an external Gemma endpoint degrade gracefully (empty
results, logged warning) until you point `GEMMA_API_URL` at a real model.

## Stack

| Layer      | Technology |
|------------|------------|
| Frontend   | HTML5, CSS3, vanilla JavaScript (ES6+), Chart.js |
| Backend    | FastAPI, SQLAlchemy, SQLite |
| Auth       | JWT (python-jose) + bcrypt |
| AI         | Google Gemma (skill extraction, recommendations) via a swappable client |
| ML         | scikit-learn (RandomForestClassifier) for employability prediction |
| Reports    | ReportLab (PDF), OpenPyXL (Excel) |

## Project structure

```
skill-gap-system/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app + router wiring
│   │   ├── config.py          # Settings (reads .env)
│   │   ├── database/          # SQLAlchemy engine/session
│   │   ├── models/            # 14 tables from the spec (one file per domain)
│   │   ├── schemas/           # Pydantic request/response models
│   │   ├── auth/              # JWT + bcrypt + RBAC dependencies
│   │   ├── routes/            # /auth /users /graduates /employers /skills
│   │   │                        /courses /universities /jobs /prediction
│   │   │                        /recommendations /analytics /reports
│   │   ├── services/          # Skill-gap matching, prediction, analytics
│   │   ├── ai/                # Gemma client wrapper
│   │   ├── ml/                # Employability model + training script
│   │   └── utils/             # Pagination, PDF/Excel report generation
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── index.html              # Landing page
    ├── login.html               # Login + registration (tabbed)
    ├── dashboard.html            # Graduate dashboard (score, charts, recs)
    ├── profile.html               # Academic background, projects, CV upload UI
    ├── assessment.html             # Self-rate skills by category
    ├── prediction.html              # Score detail + prediction history
    ├── analytics.html                # Admin/Researcher labour-market dashboard
    ├── reports.html                   # Generate & download PDF/Excel reports
    └── assets/{css,js}/
```

## Running the backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate     # optional but recommended
pip install -r requirements.txt
cp .env.example .env                                  # then edit SECRET_KEY at minimum

# (optional) train the employability model on synthetic demo data —
# without this, predictions fall back to a transparent weighted heuristic
python -m app.ml.train_model

uvicorn app.main:app --reload
```

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health
- Tables are created automatically on startup via `Base.metadata.create_all()`.
  Swap this for Alembic migrations before production use.

## Running the frontend

The frontend is static — no build step. Serve it with any static server and
point it at your running backend:

```bash
cd frontend
python3 -m http.server 5500
```

Then open http://localhost:5500. If your backend isn't on
`http://localhost:8000`, set `window.API_BASE_URL` before `api.js` loads
(e.g. add `<script>window.API_BASE_URL = "https://your-api.example.com";</script>`
in each HTML `<head>`), or edit the default in `assets/js/api.js`.

## What's implemented vs. what's stubbed

**Fully working:** registration/login/JWT auth, role-based access control
(Administrator/Graduate/Employer/Researcher), graduate profile CRUD, skill
self-assessment, job posting CRUD, skill-gap match percentage calculation,
employability prediction (trained scikit-learn model with heuristic
fallback), analytics aggregation queries, PDF/Excel report generation and
download, and every frontend page wired to the live API with loading/empty/
error states, dark mode, and responsive layout down to 320px.

**Stubbed / extension points, clearly marked in code:**
- **Gemma calls** (`app/ai/gemma_client.py`) point at a local Ollama-style
  endpoint by default. Point `GEMMA_API_URL` / `GEMMA_MODEL_NAME` at your
  actual deployment — no other code needs to change.
- **CV upload & parsing** — the profile page has the upload UI; wire it to a
  new `/api/graduates/me/cv` endpoint that saves the file and calls
  `gemma_client.extract_skills_from_text()`.
- **ML training data** — `app/ml/train_model.py` trains on synthetic data so
  the model works out of the box. Swap `generate_synthetic_dataset()` for a
  loader over real, labeled graduate-outcome data when available.
- **Email delivery** for password resets — `forgot-password` generates a
  token but logs it instead of emailing it (see the `TODO` in `routes/auth.py`).

## Security notes for production

- Change `SECRET_KEY` in `.env` — the default is for local dev only.
- Replace `Base.metadata.create_all()` with Alembic migrations.
- Add rate limiting (the `slowapi` dependency is already in `requirements.txt`).
- Tighten `ALLOWED_ORIGINS` to your real frontend domain(s).
