"""
POST /api/assess — main assessment endpoint
POST /api/sus — submit SUS questionnaire
"""
import json
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter()

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SUS_FILE = os.path.join(DATA_DIR, "sus_responses.json")


class AssessmentInput(BaseModel):
    degree_program: str
    job_title: str
    skills: Optional[dict] = Field(default_factory=dict)
    task_distribution: Optional[dict] = Field(default_factory=dict)


class SusInput(BaseModel):
    responses: list[int]
    degree_program: Optional[str] = None


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


def _get_program_typical_skills(degree_program: str) -> dict[str, int]:
    """Return the typical (mean) skill profile for a program based on POARD averages."""
    from model.train import PROGRAM_SKILLS
    program_skill_ids = PROGRAM_SKILLS.get(degree_program, [])
    # Assume 70% proficiency rate for all program skills (POARD mean is ~0.72)
    return {skill_id: 1 for skill_id in program_skill_ids}


def _compute_skill_gaps(
    degree_program: str,
    skills: dict,
    shap_explanation: dict,
    cmos: dict,
    use_typical: bool = False,
) -> list[dict]:
    """
    Identify skill gaps.

    When `use_typical=True` (no user skills provided), rank gaps by absolute
    SKILL_RISK_WEIGHT — the most protective skills for the program that are
    underutilised in the labour market become the upskilling targets.

    When `use_typical=False` (user provided skills), use SHAP protective factors
    for skills the user doesn't have.
    """
    from model.train import SKILL_RISK_WEIGHTS, PROGRAM_SKILLS

    gaps = []
    program_data = cmos.get(degree_program, {})
    ched_skill_ids = {s["id"] for s in program_data.get("skills", [])}

    if use_typical:
        # Rule-based: pick the most protective skills for this program
        program_skill_ids = PROGRAM_SKILLS.get(degree_program, [])
        scored = []
        for skill_id in program_skill_ids:
            weight = SKILL_RISK_WEIGHTS.get(skill_id, 0)
            if weight < 0:  # protective — negative weight = reduces risk
                scored.append((skill_id, abs(weight)))
        scored.sort(key=lambda x: x[1], reverse=True)

        for skill_id, impact in scored[:6]:
            in_ched = skill_id in ched_skill_ids
            gaps.append({
                "skill_id": skill_id,
                "skill_label": _get_skill_label(skill_id, cmos),
                "in_ched_cmo": in_ched,
                "gap_type": "implementation" if in_ched else "design",
                "impact_score": round(impact, 4),
            })
    else:
        # SHAP-based: protective factors the user doesn't currently have
        for factor in shap_explanation.get("top_protective_factors", []):
            skill_id = factor["skill"]
            if not skill_id.startswith("skill_"):
                continue
            user_has_skill = bool(skills.get(skill_id, 0))
            if not user_has_skill:
                in_ched = skill_id in ched_skill_ids
                gaps.append({
                    "skill_id": skill_id,
                    "skill_label": _get_skill_label(skill_id, cmos),
                    "in_ched_cmo": in_ched,
                    "gap_type": "implementation" if in_ched else "design",
                    "impact_score": round(factor["contribution"], 4),
                })

    return gaps[:6]


def calculate_sus(responses: list[int]) -> float:
    if len(responses) != 10:
        raise ValueError("SUS requires exactly 10 responses")
    odd_sum = sum(responses[i] - 1 for i in [0, 2, 4, 6, 8])
    even_sum = sum(5 - responses[i] for i in [1, 3, 5, 7, 9])
    return (odd_sum + even_sum) * 2.5


def interpret_sus(score: float) -> tuple[str, str]:
    if score >= 90:
        return "Excellent", "A"
    elif score >= 80:
        return "Good", "B"
    elif score >= 70:
        return "OK", "C"
    elif score >= 51:
        return "Poor", "D"
    else:
        return "Awful", "F"


@router.post("/assess")
async def submit_assessment(body: AssessmentInput):
    from model.predict import predict, classify_risk, get_program_averages, get_score_percentile
    from shap_analysis.explain import explain_prediction
    from gemini.recommend import generate_recommendations

    skills = body.skills or {}
    task_distribution = body.task_distribution or {}
    use_typical = len(skills) == 0

    # If no skills provided, use program typical profile
    effective_skills = skills if skills else _get_program_typical_skills(body.degree_program)

    try:
        result = predict(
            degree_program=body.degree_program,
            job_title=body.job_title,
            skills=effective_skills,
            task_distribution=task_distribution if task_distribution else None,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Model not ready: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

    score = result["score"]
    risk = classify_risk(score)

    try:
        program_averages = get_program_averages()
        program_average = program_averages.get(body.degree_program, score)
        percentile = get_score_percentile(score, body.degree_program)
    except Exception:
        program_averages = {
            "BS Accountancy": 0.66, "BS Business Administration": 0.56,
            "BS Information Technology": 0.42, "BS Computer Science": 0.31,
            "Bachelor of Elementary Education": 0.36, "BS Nursing": 0.27,
        }
        program_average = program_averages.get(body.degree_program, 0.50)
        percentile = 50

    # SHAP explanation
    try:
        shap_explanation = explain_prediction(
            result["X"],
            body.degree_program,
            effective_skills,
            task_distribution,
        )
    except Exception as e:
        print(f"SHAP error: {e}")
        shap_explanation = {"top_risk_factors": [], "top_protective_factors": []}

    # Skill gaps
    cmos = _load_cmos()
    skill_gaps = _compute_skill_gaps(
        body.degree_program, effective_skills, shap_explanation, cmos, use_typical=use_typical
    )

    # Course recommendations
    try:
        recommendations = generate_recommendations(skill_gaps, body.degree_program, body.job_title)
    except Exception as e:
        print(f"Recommendation error: {e}")
        recommendations = []

    return {
        "vulnerability_score": score,
        "risk_level": risk["level"],
        "risk_label": risk["label"],
        "risk_color": risk["color"],
        "program_average": round(float(program_average), 4),
        "percentile": percentile,
        "shap_explanation": shap_explanation,
        "skill_gaps": skill_gaps,
        "recommendations": recommendations,
        "program_comparison": {k: round(v, 4) for k, v in program_averages.items()},
    }


@router.post("/sus")
async def submit_sus(body: SusInput):
    if len(body.responses) != 10:
        raise HTTPException(status_code=400, detail="SUS requires exactly 10 responses (1–5 each)")
    for r in body.responses:
        if r < 1 or r > 5:
            raise HTTPException(status_code=400, detail="Each SUS response must be between 1 and 5")

    sus_score = calculate_sus(body.responses)
    interpretation, grade = interpret_sus(sus_score)

    entry = {
        "responses": body.responses,
        "sus_score": sus_score,
        "interpretation": interpretation,
        "grade": grade,
        "degree_program": body.degree_program,
    }
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(SUS_FILE):
            with open(SUS_FILE) as f:
                existing = json.load(f)
        else:
            existing = []
        existing.append(entry)
        with open(SUS_FILE, "w") as f:
            json.dump(existing, f, indent=2)
    except Exception as e:
        print(f"SUS persistence error: {e}")

    return {"sus_score": round(sus_score, 2), "interpretation": interpretation, "grade": grade}
