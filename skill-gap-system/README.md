# Graduate Skill Gap Prediction System (SkillGap.ng)

An AI-powered employability and skill-gap prediction platform for Nigerian graduates — predicts employability, compares graduate skills against labour market demand, and recommends personalized learning paths to help close the gap between school and work.

This is a **fully functional system**: the data model, JWT authentication, REST API, ML prediction pipeline, Google Gemini integration, and frontend pages are wired together and run end-to-end.

## Stack

| Layer      | Technology |
|------------|------------|
| Frontend   | HTML5, CSS3, vanilla JavaScript (ES6+), Chart.js |
| Backend    | FastAPI, SQLAlchemy, SQLite, Pydantic |
| Auth       | JWT (python-jose) + bcrypt for password hashing |
| AI         | Google Gemini (skill extraction from CVs, dynamic recommendations) |
| ML         | scikit-learn (RandomForestClassifier) for employability prediction |
| Docker     | Docker Compose for seamless, reproducible multi-container deployment |

## Features

- **Employability Prediction:** A machine-learning model scores your readiness using your CGPA, projects, internships, certifications, and skills.
- **Skill Assessment:** Rate your proficiency across dozens of technical, soft, digital-literacy, and industry-readiness skills.
- **Job Matching:** Browse live job postings and see a computed match percentage based on your assessed skills. Highlights exactly which required skills you are missing for any given job.
- **CV Skill Extraction:** Upload a PDF or Word CV and the backend uses Google Gemma to automatically extract your skills, education, and experience.
- **AI-generated Roadmap:** Personalized course, certification, and portfolio suggestions generated dynamically by Google Gemma for your specific gaps.

## Running the Application

This project is fully dockerized. To start both the backend FastAPI server and the static frontend web server:

```bash
# Start the containers in the background (builds the images if necessary)
docker-compose up -d --build
```

- **Frontend Application:** http://localhost:5500
- **Backend API:** http://localhost:8001
- **API Documentation (Swagger UI):** http://localhost:8001/docs

### Accessing the Database

To run backend commands (like manual Python scripts or database seeders):
```bash
docker-compose exec backend python <your_script.py>
```

To view backend logs:
```bash
docker-compose logs -f backend
```

## Project Structure

```
skill-gap-system/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app + router wiring
│   │   ├── config.py          # Settings (reads .env)
│   │   ├── database/          # SQLAlchemy engine/session
│   │   ├── models/            # SQLAlchemy Tables (one file per domain)
│   │   ├── schemas/           # Pydantic request/response models
│   │   ├── auth/              # JWT + bcrypt + RBAC dependencies
│   │   ├── routes/            # Route controllers for graduates, jobs, etc.
│   │   ├── services/          # Skill-gap matching, prediction, analytics logic
│   │   ├── ai/                # Gemma/Gemini client wrapper
│   │   ├── ml/                # Employability model
│   │   └── utils/             # Pagination, Report generation
│   ├── alembic/               # Database migrations
│   ├── Dockerfile             # Backend container image
│   ├── requirements.txt       # Python dependencies
│   ├── seed_jobs.py           # Script to seed initial jobs and skills
│   └── uploads/               # Directory for uploaded CVs
├── frontend/
│   ├── index.html              # Landing page
│   ├── login.html              # Login & registration
│   ├── dashboard.html          # Graduate dashboard (score, charts, recs)
│   ├── profile.html            # Academic background, projects, CV upload
│   ├── assessment.html         # Self-rate skills by category
│   ├── jobs.html               # Job Matching interface
│   ├── prediction.html         # Score detail & prediction history
│   └── assets/{css,js}/        # Styles and JavaScript logic
├── docker-compose.yml          # Multi-container orchestration
└── .env                        # Environment variables (API keys, secrets)
```

## Security & Production Readiness

Before deploying to a public production environment:
1. **API Keys:** Ensure `GEMINI_API_KEY` is securely set in `.env` so that AI recommendations and CV parsing work against the live model.
2. **Secret Keys:** Change the `SECRET_KEY` in `.env` — the default is for local development only.
3. **Database Security:** The current application uses SQLite for simplicity. For production, switch the `DATABASE_URL` in `.env` to a managed PostgreSQL instance and update the `psycopg2` dependency.
4. **CORS:** Tighten `ALLOWED_ORIGINS` in `.env` to only allow requests from your verified frontend domains.
