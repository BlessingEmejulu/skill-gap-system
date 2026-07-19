"""
FastAPI application entrypoint.

Run with:  uvicorn app.main:app --reload
Docs at:   http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app import models  # noqa: F401  (import so Base.metadata sees every table)

from app.routes import (
    auth,
    users,
    graduates,
    employers,
    skills,
    courses,
    universities,
    jobs,
    prediction,
    recommendations,
    analytics,
    reports,
)

app = FastAPI(
    title=settings.app_name,
    description=(
        "AI-powered employability and skill-gap prediction platform for Nigerian graduates. "
        "Predicts employability, identifies skill gaps against labour market demand, and "
        "recommends personalized learning paths."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # For production, replace with Alembic migrations instead of create_all().
    Base.metadata.create_all(bind=engine)


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(graduates.router)
app.include_router(employers.router)
app.include_router(skills.router)
app.include_router(courses.router)
app.include_router(universities.router)
app.include_router(jobs.router)
app.include_router(prediction.router)
app.include_router(recommendations.router)
app.include_router(analytics.router)
app.include_router(reports.router)
