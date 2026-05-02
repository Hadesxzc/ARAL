"""
ARAL SHAP explainability module.
Computes per-prediction SHAP values using TreeExplainer on the trained RF model.
"""
import os
import json
import numpy as np
import pandas as pd

_explainer = None
_meta = None
_feature_names = None


def _get_skill_label(skill_id: str) -> str:
    """Map skill_id to human-readable label from ched_cmos.json."""
    try:
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        cmos_path = os.path.join(data_dir, "ched_cmos.json")
        with open(cmos_path) as f:
            cmos = json.load(f)
        for program_data in cmos.values():
            for skill in program_data.get("skills", []):
                if skill["id"] == skill_id:
                    return skill["label"]
    except Exception:
        pass
    return skill_id.replace("skill_", "").replace("_", " ").title()


def _get_task_label(task_id: str) -> str:
    labels = {
        "task_data_entry": "Time on Data Entry",
        "task_data_analysis": "Time on Data Analysis",
        "task_decision_making": "Time on Decision Making",
        "task_computer_use": "Time on Computer Use",
        "task_client_comms": "Time on Client Communication",
        "task_internal_comms": "Time on Internal Communication",
        "task_teaching": "Time on Teaching/Training",
        "task_managing": "Time on Managing/Supervising",
        "task_documents": "Time on Documents/Reports",
        "task_physical": "Time on Physical/Manual Tasks",
        "task_creative": "Time on Creative Work",
        "task_caregiving": "Time on Caregiving",
        "task_other": "Time on Other Tasks",
    }
    return labels.get(task_id, task_id.replace("task_", "").replace("_", " ").title())


def _load_explainer():
    global _explainer, _meta, _feature_names
    if _explainer is not None:
        return _explainer, _meta, _feature_names

    import joblib
    import shap

    model_dir = os.path.join(os.path.dirname(__file__), "..", "model")
    model_path = os.path.join(model_dir, "aral_model.pkl")
    meta_path = os.path.join(model_dir, "model_meta.json")

    pipeline = joblib.load(model_path)
    with open(meta_path) as f:
        _meta = json.load(f)

    rf_model = pipeline.named_steps["model"]
    preprocessor = pipeline.named_steps["preprocessor"]

    # Load POARD for background data
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    df = pd.read_csv(os.path.join(data_dir, "poard.csv"))
    feature_cols = _meta["feature_cols"]
    X_bg = df[feature_cols].sample(100, random_state=42)
    X_bg_transformed = preprocessor.transform(X_bg)

    # Get feature names after transformation
    cat_features = preprocessor.named_transformers_["cat"].get_feature_names_out(["degree_program"])
    num_features = np.array(_meta["task_cols"] + _meta["skill_cols"])
    _feature_names = list(cat_features) + list(num_features)

    _explainer = shap.TreeExplainer(rf_model, data=X_bg_transformed, feature_perturbation="interventional")
    return _explainer, _meta, _feature_names


def explain_prediction(X_transformed, degree_program: str, skills: dict, task_distribution: dict) -> dict:
    """
    Compute SHAP values for a single prediction.
    Returns top risk factors and top protective factors.
    """
    try:
        explainer, meta, feature_names = _load_explainer()

        import joblib
        model_dir = os.path.join(os.path.dirname(__file__), "..", "model")
        pipeline = joblib.load(os.path.join(model_dir, "aral_model.pkl"))
        preprocessor = pipeline.named_steps["preprocessor"]

        X_t = preprocessor.transform(X_transformed)
        shap_vals = explainer.shap_values(X_t)[0]

        # Map SHAP values back to original feature space (aggregate OHE categories)
        cat_feature_names = preprocessor.named_transformers_["cat"].get_feature_names_out(["degree_program"])
        n_cat = len(cat_feature_names)

        shap_by_feature = {}

        # Sum OHE shap values under "degree_program"
        degree_shap = float(np.sum(shap_vals[:n_cat]))
        shap_by_feature["degree_program"] = degree_shap

        # Remaining features (task + skill)
        num_feature_names = meta["task_cols"] + meta["skill_cols"]
        for i, name in enumerate(num_feature_names):
            shap_by_feature[name] = float(shap_vals[n_cat + i])

        # Build results focusing on user-controlled features
        factors = []
        for feature, shap_val in shap_by_feature.items():
            if feature == "degree_program":
                continue
            if feature.startswith("task_"):
                label = _get_task_label(feature)
            else:
                label = _get_skill_label(feature)

            factors.append({
                "skill": feature,
                "skill_label": label,
                "contribution": round(abs(shap_val), 4),
                "direction": "increases_risk" if shap_val > 0 else "reduces_risk",
                "raw_shap": shap_val,
            })

        factors.sort(key=lambda x: abs(x["raw_shap"]), reverse=True)

        top_risk = [
            {k: v for k, v in f.items() if k != "raw_shap"}
            for f in factors if f["direction"] == "increases_risk"
        ][:5]

        top_protective = [
            {k: v for k, v in f.items() if k != "raw_shap"}
            for f in factors if f["direction"] == "reduces_risk"
        ][:5]

        return {
            "top_risk_factors": top_risk,
            "top_protective_factors": top_protective,
        }

    except Exception as e:
        # Fallback: rule-based explanation
        return _fallback_explanation(degree_program, skills, task_distribution)


def _fallback_explanation(degree_program: str, skills: dict, task_distribution: dict) -> dict:
    """Rule-based fallback when SHAP is unavailable."""
    from model.train import ONET_TASK_SCORES, SKILL_RISK_WEIGHTS

    factors = []

    # Task factors
    for task, weight in (task_distribution or {}).items():
        onet_score = ONET_TASK_SCORES.get(task, 0.5)
        contribution = weight * onet_score
        if contribution > 0.01:
            factors.append({
                "skill": task,
                "skill_label": _get_task_label(task),
                "contribution": round(contribution, 4),
                "direction": "increases_risk" if onet_score > 0.5 else "reduces_risk",
                "raw": onet_score,
            })

    # Skill factors
    for skill, has_skill in skills.items():
        if has_skill:
            risk_weight = SKILL_RISK_WEIGHTS.get(skill, 0)
            if abs(risk_weight) > 0.02:
                factors.append({
                    "skill": skill,
                    "skill_label": _get_skill_label(skill),
                    "contribution": round(abs(risk_weight), 4),
                    "direction": "increases_risk" if risk_weight > 0 else "reduces_risk",
                    "raw": risk_weight,
                })

    factors.sort(key=lambda x: x["contribution"], reverse=True)

    top_risk = [
        {k: v for k, v in f.items() if k != "raw"}
        for f in factors if f["direction"] == "increases_risk"
    ][:5]

    top_protective = [
        {k: v for k, v in f.items() if k != "raw"}
        for f in factors if f["direction"] == "reduces_risk"
    ][:5]

    return {
        "top_risk_factors": top_risk,
        "top_protective_factors": top_protective,
    }


def compute_global_feature_importance(top_n: int = 10) -> list[dict]:
    """Compute global feature importance from the trained RF model."""
    try:
        import joblib
        model_dir = os.path.join(os.path.dirname(__file__), "..", "model")
        pipeline = joblib.load(os.path.join(model_dir, "aral_model.pkl"))
        with open(os.path.join(model_dir, "model_meta.json")) as f:
            meta = json.load(f)

        rf_model = pipeline.named_steps["model"]
        preprocessor = pipeline.named_steps["preprocessor"]

        importances = rf_model.feature_importances_
        cat_feature_names = preprocessor.named_transformers_["cat"].get_feature_names_out(["degree_program"])
        n_cat = len(cat_feature_names)

        num_feature_names = meta["task_cols"] + meta["skill_cols"]
        feature_importances = {}
        feature_importances["degree_program"] = float(np.sum(importances[:n_cat]))
        for i, name in enumerate(num_feature_names):
            feature_importances[name] = float(importances[n_cat + i])

        sorted_features = sorted(feature_importances.items(), key=lambda x: x[1], reverse=True)

        results = []
        for feature, importance in sorted_features[:top_n + 5]:
            if feature == "degree_program":
                continue
            if len(results) >= top_n:
                break

            if feature.startswith("task_"):
                label = _get_task_label(feature)
                direction = "increases_risk"
            else:
                from model.train import SKILL_RISK_WEIGHTS
                risk_weight = SKILL_RISK_WEIGHTS.get(feature, 0)
                label = _get_skill_label(feature)
                direction = "increases_risk" if risk_weight >= 0 else "reduces_risk"

            results.append({
                "skill": feature,
                "skill_label": label,
                "contribution": round(importance, 4),
                "direction": direction,
            })

        return results
    except Exception:
        return []
