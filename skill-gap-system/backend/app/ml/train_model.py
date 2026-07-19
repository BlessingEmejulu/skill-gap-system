"""
Train the employability RandomForestClassifier on synthetic data and save it
to app/ml/artifacts/employability_model.joblib.

Run: python -m app.ml.train_model

Replace `generate_synthetic_dataset()` with a loader for your real, labeled
graduate-outcomes dataset once one is available — everything downstream
(feature names, API, prediction service) stays the same.
"""
import os

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from app.ml.employability_model import FEATURE_NAMES, MODEL_PATH

RNG = np.random.default_rng(42)


def generate_synthetic_dataset(n_samples: int = 2000):
    cgpa = RNG.uniform(1.5, 5.0, n_samples)
    skill_count = RNG.integers(0, 20, n_samples)
    avg_skill_proficiency = RNG.uniform(0, 100, n_samples)
    project_count = RNG.integers(0, 10, n_samples)
    internship_count = RNG.integers(0, 4, n_samples)
    certification_count = RNG.integers(0, 8, n_samples)
    experience_years = RNG.uniform(0, 5, n_samples)
    avg_soft_skill_score = RNG.uniform(0, 100, n_samples)

    X = np.column_stack(
        [
            cgpa,
            skill_count,
            avg_skill_proficiency,
            project_count,
            internship_count,
            certification_count,
            experience_years,
            avg_soft_skill_score,
        ]
    )

    # Synthetic "ground truth": a weighted score plus noise, thresholded into employed/not.
    weighted = (
        (cgpa / 5.0) * 0.30
        + (avg_skill_proficiency / 100) * 0.25
        + (np.minimum(internship_count * 5 + experience_years * 4, 20) / 20) * 0.20
        + (np.minimum(project_count * 3, 15) / 15) * 0.15
        + (np.minimum(certification_count * 2.5, 10) / 10) * 0.10
    )
    noise = RNG.normal(0, 0.07, n_samples)
    y = (weighted + noise > 0.55).astype(int)

    return X, y


def main():
    X, y = generate_synthetic_dataset()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    clf = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)
    clf.fit(X_train, y_train)

    preds = clf.predict(X_test)
    print(f"Feature order: {FEATURE_NAMES}")
    print(f"Accuracy: {accuracy_score(y_test, preds):.3f}")
    print(classification_report(y_test, preds))

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
    print(f"Saved trained model to {MODEL_PATH}")


if __name__ == "__main__":
    main()
