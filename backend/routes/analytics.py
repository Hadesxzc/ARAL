"""
GET /api/analytics/program-summary — per-program SHAP findings (research dashboard)
GET /api/analytics/global-stats — overall statistics
GET /api/sus/results — aggregated SUS results (admin)
"""
import json
import os
import pandas as pd
import numpy as np
from fastapi import APIRouter

router = APIRouter()

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "model")
SUS_FILE = os.path.join(DATA_DIR, "sus_responses.json")

PROGRAMS = [
    "BS Accountancy",
    "BS Business Administration",
    "BS Information Technology",
    "BS Computer Science",
    "Bachelor of Elementary Education",
    "BS Nursing",
]


def _load_poard() -> pd.DataFrame:
    path = os.path.join(DATA_DIR, "poard.csv")
    return pd.read_csv(path)


def _load_cmos() -> dict:
    path = os.path.join(DATA_DIR, "ched_cmos.json")
    with open(path) as f:
        return json.load(f)


def _get_skill_label(skill_id: str, cmos: dict) -> str:
    for program_data in cmos.values():
        for skill in program_data.get("skills", []):
            if skill["id"] == skill_id:
                return skill["label"]
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


@router.get("/analytics/program-summary")
def get_program_summary():
    try:
        df = _load_poard()
        cmos = _load_cmos()

        from shap_analysis.explain import compute_global_feature_importance
        from model.train import SKILL_RISK_WEIGHTS, PROGRAM_SKILLS

        programs_data = []
        for program in PROGRAMS:
            prog_df = df[df["degree_program"] == program]
            if len(prog_df) == 0:
                continue

            mean_vuln = float(prog_df["vulnerability_score"].mean())
            count = int(len(prog_df))

            program_skill_ids = PROGRAM_SKILLS.get(program, [])
            cmos_skill_ids = {s["id"] for s in cmos.get(program, {}).get("skills", [])}

            # Derive top risk/protective skills for this program
            top_risk = []
            top_protective = []
            for skill_id in program_skill_ids:
                weight = SKILL_RISK_WEIGHTS.get(skill_id, 0)
                label = _get_skill_label(skill_id, cmos)
                if weight > 0.04:
                    top_risk.append({
                        "skill": skill_id,
                        "skill_label": label,
                        "contribution": round(abs(weight), 4),
                        "direction": "increases_risk",
                    })
                elif weight < -0.04:
                    top_protective.append({
                        "skill": skill_id,
                        "skill_label": label,
                        "contribution": round(abs(weight), 4),
                        "direction": "reduces_risk",
                    })

            top_risk.sort(key=lambda x: x["contribution"], reverse=True)
            top_protective.sort(key=lambda x: x["contribution"], reverse=True)

            # Curriculum gaps: protective skills not in CHED CMO
            curriculum_gaps = []
            for factor in top_protective[:5]:
                skill_id = factor["skill"]
                in_ched = skill_id in cmos_skill_ids
                skill_col_avg = float(prog_df[skill_id].mean()) if skill_id in prog_df.columns else 0.5
                gap_type = "implementation" if in_ched and skill_col_avg < 0.6 else ("design" if not in_ched else None)
                if gap_type:
                    curriculum_gaps.append({
                        "skill_id": skill_id,
                        "skill_label": factor["skill_label"],
                        "in_ched_cmo": in_ched,
                        "gap_type": gap_type,
                        "impact_score": factor["contribution"],
                    })

            programs_data.append({
                "program": program,
                "mean_vulnerability": round(mean_vuln, 4),
                "respondent_count": count,
                "top_risk_skills": top_risk[:3],
                "top_protective_skills": top_protective[:3],
                "curriculum_gaps": curriculum_gaps[:4],
            })

        return {"programs": programs_data}

    except Exception as e:
        return {
            "programs": [
                {
                    "program": p,
                    "mean_vulnerability": 0.50,
                    "respondent_count": 0,
                    "top_risk_skills": [],
                    "top_protective_skills": [],
                    "curriculum_gaps": [],
                }
                for p in PROGRAMS
            ]
        }


@router.get("/analytics/global-stats")
def get_global_stats():
    try:
        df = _load_poard()
        cmos = _load_cmos()

        from model.train import SKILL_RISK_WEIGHTS, ALL_SKILLS
        from shap_analysis.explain import compute_global_feature_importance

        total = int(len(df))
        overall_mean = float(df["vulnerability_score"].mean())

        program_averages = df.groupby("degree_program")["vulnerability_score"].mean().round(4).to_dict()

        # Score distribution
        bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.01]
        labels_bins = ["0.0–0.2", "0.2–0.4", "0.4–0.6", "0.6–0.8", "0.8–1.0"]
        df["score_bin"] = pd.cut(df["vulnerability_score"], bins=bins, labels=labels_bins, right=False)
        dist = df["score_bin"].value_counts().reindex(labels_bins, fill_value=0)
        score_distribution = [{"range": r, "count": int(c)} for r, c in dist.items()]

        # Global risk/protective skills
        top_global_risk = []
        top_global_protective = []
        for skill_id in ALL_SKILLS:
            w = SKILL_RISK_WEIGHTS.get(skill_id, 0)
            label = _get_skill_label(skill_id, cmos)
            if w > 0.04:
                top_global_risk.append({"skill": skill_id, "skill_label": label, "contribution": round(abs(w), 4), "direction": "increases_risk"})
            elif w < -0.06:
                top_global_protective.append({"skill": skill_id, "skill_label": label, "contribution": round(abs(w), 4), "direction": "reduces_risk"})

        top_global_risk.sort(key=lambda x: x["contribution"], reverse=True)
        top_global_protective.sort(key=lambda x: x["contribution"], reverse=True)

        # Also include feature importances from model
        try:
            fi = compute_global_feature_importance(10)
            if fi:
                top_global_risk = [f for f in fi if f["direction"] == "increases_risk"][:5]
                top_global_protective = [f for f in fi if f["direction"] == "reduces_risk"][:5]
        except Exception:
            pass

        return {
            "total_respondents": total,
            "overall_mean_vulnerability": round(overall_mean, 4),
            "score_distribution": score_distribution,
            "program_averages": {k: round(v, 4) for k, v in program_averages.items()},
            "top_global_risk_skills": top_global_risk[:5],
            "top_global_protective_skills": top_global_protective[:5],
        }

    except Exception as e:
        return {
            "total_respondents": 0,
            "overall_mean_vulnerability": 0.50,
            "score_distribution": [],
            "program_averages": {},
            "top_global_risk_skills": [],
            "top_global_protective_skills": [],
        }


@router.get("/sus/results")
def get_sus_results():
    try:
        if not os.path.exists(SUS_FILE):
            return {
                "total_responses": 0,
                "mean_sus_score": 0.0,
                "interpretation": "No data",
                "score_by_program": {},
                "responses": [],
            }
        with open(SUS_FILE) as f:
            responses = json.load(f)

        scores = [r["sus_score"] for r in responses]
        mean_score = float(np.mean(scores)) if scores else 0.0

        # Interpret mean
        if mean_score >= 90:
            interp = "Excellent"
        elif mean_score >= 80:
            interp = "Good"
        elif mean_score >= 70:
            interp = "OK"
        elif mean_score >= 51:
            interp = "Poor"
        else:
            interp = "Awful"

        by_program: dict[str, list[float]] = {}
        for r in responses:
            prog = r.get("degree_program") or "Unknown"
            by_program.setdefault(prog, []).append(r["sus_score"])
        score_by_program = {k: round(float(np.mean(v)), 2) for k, v in by_program.items()}

        return {
            "total_responses": len(responses),
            "mean_sus_score": round(mean_score, 2),
            "interpretation": interp,
            "score_by_program": score_by_program,
            "responses": responses[-20:],
        }
    except Exception as e:
        return {
            "total_responses": 0,
            "mean_sus_score": 0.0,
            "interpretation": "No data",
            "score_by_program": {},
            "responses": [],
        }
