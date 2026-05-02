"""
ARAL prediction logic — wraps the trained pipeline and computes vulnerability scores.
"""
import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Optional

MODEL_DIR = os.path.dirname(__file__)

_pipeline = None
_meta = None


def _load():
    global _pipeline, _meta
    if _pipeline is None:
        model_path = os.path.join(MODEL_DIR, "aral_model.pkl")
        meta_path = os.path.join(MODEL_DIR, "model_meta.json")
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found at {model_path}. Run backend/model/train.py first."
            )
        _pipeline = joblib.load(model_path)
        with open(meta_path) as f:
            _meta = json.load(f)
    return _pipeline, _meta


def classify_risk(score: float) -> dict:
    if score < 0.30:
        return {
            "level": "Low",
            "color": "#22c55e",
            "label": "Your career has low automation vulnerability",
        }
    elif score < 0.50:
        return {
            "level": "Moderate",
            "color": "#f59e0b",
            "label": "Your career has moderate automation vulnerability",
        }
    elif score < 0.70:
        return {
            "level": "High",
            "color": "#f97316",
            "label": "Your career has high automation vulnerability",
        }
    else:
        return {
            "level": "Very High",
            "color": "#ef4444",
            "label": "Your career has very high automation vulnerability",
        }


def predict(
    degree_program: str,
    job_title: str,
    skills: dict[str, int],
    task_distribution: Optional[dict[str, float]] = None,
) -> dict:
    pipeline, meta = _load()

    feature_cols = meta["feature_cols"]
    task_cols = meta["task_cols"]
    all_skills = meta["skill_cols"]

    # Build task distribution
    if task_distribution:
        total = sum(task_distribution.values())
        tasks = {t: task_distribution.get(t, 0) / max(total, 1e-9) for t in task_cols}
    else:
        # Use program averages
        from model.train import PROGRAM_TASK_WEIGHTS
        base = PROGRAM_TASK_WEIGHTS.get(degree_program, {t: 1 / len(task_cols) for t in task_cols})
        tasks = {t: base.get(t, 0) for t in task_cols}
        total = sum(tasks.values())
        tasks = {t: v / max(total, 1e-9) for t, v in tasks.items()}

    # Build skill vector
    skill_vec = {s: int(skills.get(s, 0)) for s in all_skills}

    row = {"degree_program": degree_program}
    row.update(tasks)
    row.update(skill_vec)

    X = pd.DataFrame([row])[feature_cols]
    score = float(np.clip(pipeline.predict(X)[0], 0.0, 1.0))

    return {
        "score": round(score, 4),
        "row": row,
        "X": X,
    }


def get_program_averages() -> dict[str, float]:
    import pandas as pd
    pipeline, meta = _load()
    poard_path = os.path.join(os.path.dirname(MODEL_DIR), "data", "poard.csv")
    df = pd.read_csv(poard_path)
    return df.groupby("degree_program")["vulnerability_score"].mean().round(4).to_dict()


def get_score_percentile(score: float, program: str) -> int:
    import pandas as pd
    poard_path = os.path.join(os.path.dirname(MODEL_DIR), "data", "poard.csv")
    df = pd.read_csv(poard_path)
    program_scores = df[df["degree_program"] == program]["vulnerability_score"].values
    if len(program_scores) == 0:
        return 50
    return int(round(100 * (score > program_scores).mean()))
