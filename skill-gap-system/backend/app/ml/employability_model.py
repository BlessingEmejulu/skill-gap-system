"""
Employability prediction model.

Wraps a scikit-learn RandomForestClassifier trained on graduate features:
CGPA, skill count/avg-proficiency, project count, internship count,
certification count, years of experience, and average soft-skill score.

Run `python -m app.ml.train_model` to (re)train on synthetic data and
write the fitted model to app/ml/artifacts/employability_model.joblib.
If no trained artifact exists yet, `predict()` falls back to a transparent
rule-based heuristic so the API still works out of the box.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import joblib
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "artifacts", "employability_model.joblib")

FEATURE_NAMES = [
    "cgpa",
    "skill_count",
    "avg_skill_proficiency",
    "project_count",
    "internship_count",
    "certification_count",
    "experience_years",
    "avg_soft_skill_score",
]


@dataclass
class GraduateFeatures:
    cgpa: float = 0.0             # 0-5 Nigerian grading scale
    skill_count: int = 0
    avg_skill_proficiency: float = 0.0   # 0-100
    project_count: int = 0
    internship_count: int = 0
    certification_count: int = 0
    experience_years: float = 0.0
    avg_soft_skill_score: float = 0.0    # 0-100

    def to_vector(self) -> np.ndarray:
        return np.array([[getattr(self, name) for name in FEATURE_NAMES]], dtype=float)


class EmployabilityModel:
    def __init__(self, model_path: str = MODEL_PATH):
        self.model_path = model_path
        self._model = self._load()

    def _load(self):
        if os.path.exists(self.model_path):
            return joblib.load(self.model_path)
        return None  # falls back to heuristic until train_model.py has been run

    def is_trained(self) -> bool:
        return self._model is not None

    def predict(self, features: GraduateFeatures) -> dict:
        if self._model is not None:
            vector = features.to_vector()
            proba = self._model.predict_proba(vector)[0]
            employed_proba = float(proba[1]) if len(proba) > 1 else float(proba[0])
            score = round(employed_proba * 100, 1)
            confidence = round(float(np.max(proba)), 3)
        else:
            employed_proba, score, confidence = self._heuristic(features)

        risk_level = "low" if score >= 70 else "medium" if score >= 45 else "high"
        return {
            "employability_score": score,
            "employment_probability": round(employed_proba, 3),
            "risk_level": risk_level,
            "confidence": confidence,
            "model_version": "rf_v1" if self._model is not None else "heuristic_v1",
        }

    @staticmethod
    def _heuristic(f: GraduateFeatures) -> tuple[float, float, float]:
        """Transparent weighted-average fallback used before a model has been trained."""
        cgpa_component = (f.cgpa / 5.0) * 30
        skills_component = min(f.avg_skill_proficiency, 100) / 100 * 25
        experience_component = min(f.internship_count * 5 + f.experience_years * 4, 20)
        projects_component = min(f.project_count * 3, 15)
        certs_component = min(f.certification_count * 2.5, 10)
        score = round(
            cgpa_component + skills_component + experience_component + projects_component + certs_component,
            1,
        )
        score = min(score, 100.0)
        probability = round(score / 100, 3)
        confidence = 0.5  # heuristic confidence is deliberately modest
        return probability, score, confidence


employability_model = EmployabilityModel()
