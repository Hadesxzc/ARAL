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


def _load_jobs() -> dict:
    path = os.path.join(DATA_DIR, "jobs_by_program.json")
    with open(path) as f:
        return json.load(f)


def _load_program_skills() -> dict[str, list[str]]:
    cmos = _load_cmos()
    return {prog: [s["id"] for s in data["skills"]] for prog, data in cmos.items()}


def _get_skill_label(skill_id: str, cmos: dict) -> str:
    # First check CHED CMO data
    for program_data in cmos.values():
        for skill in program_data.get("skills", []):
            if skill["id"] == skill_id:
                return skill["label"]

    # Task-based skill labels
    TASK_SKILL_LABELS = {
        "skill_teaching": "Teaching",
        "skill_mentoring": "Mentoring",
        "skill_communication": "Communication",
        "skill_critical_thinking": "Critical Thinking",
        "skill_problem_solving": "Problem Solving",
        "skill_leadership": "Leadership",
        "skill_data_analysis": "Data Analysis",
        "skill_data_entry": "Data Entry",
        "skill_document_mgmt": "Document Management",
        "skill_digital_literacy": "Digital Literacy",
        "skill_analytics": "Analytics",
        "skill_client_relations": "Client Relations",
        "skill_teamwork": "Teamwork",
        "skill_interpersonal": "Interpersonal Skills",
        "skill_management": "Management",
        "skill_creativity": "Creativity",
        "skill_caregiving": "Caregiving",
        "skill_empathy": "Empathy",
        "skill_physical": "Physical Skills",
    }

    if skill_id in TASK_SKILL_LABELS:
        return TASK_SKILL_LABELS[skill_id]

    return skill_id.replace("skill_", "").replace("_", " ").title()


def _get_program_typical_skills(degree_program: str) -> dict[str, int]:
    """Return a typical intermediate skill profile (proficiency=3) for a program."""
    program_skills = _load_program_skills()
    skill_ids = program_skills.get(degree_program, [])
    return {skill_id: 3 for skill_id in skill_ids}


def _compute_skill_gaps(
    degree_program: str,
    skills: dict,
    shap_explanation: dict,
    cmos: dict,
    use_typical: bool = False,
) -> list[dict]:
    """
    Identify skill gaps from the user's proficiency profile.

    With proficiency scale 1-5:
    - Gaps are skills where the user is weak (proficiency <= 2) AND the skill is protective
    - Or skills the user hasn't rated (proficiency=3 default) that SHAP flagged
    """
    from model.train import SKILL_RISK_WEIGHTS

    program_skills = _load_program_skills()
    gaps = []
    program_data = cmos.get(degree_program, {})
    ched_skill_ids = {s["id"] for s in program_data.get("skills", [])}

    if use_typical:
        # Rule-based: identify most protective skills for this program
        program_skill_ids = program_skills.get(degree_program, [])
        scored = []
        for skill_id in program_skill_ids:
            weight = SKILL_RISK_WEIGHTS.get(skill_id, 0)
            if weight < 0:
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
                "user_proficiency": None,
            })
    else:
        # For custom jobs, show ALL user-rated skills as gaps to generate recommendations
        user_skill_ids = set(skills.keys())

        print(f"DEBUG: user_skill_ids = {user_skill_ids}")
        print(f"DEBUG: user ratings = {skills}")

        # Show ALL user-rated skills as gaps (to generate recommendations)
        for skill_id in user_skill_ids:
            weight = SKILL_RISK_WEIGHTS.get(skill_id, -0.05)  # Default protective weight
            user_proficiency = skills.get(skill_id, 3)
            in_ched = skill_id in ched_skill_ids

            # For any skill rated 3 or below, show as a potential gap
            if user_proficiency <= 3:
                gaps.append({
                    "skill_id": skill_id,
                    "skill_label": _get_skill_label(skill_id, cmos),
                    "in_ched_cmo": in_ched,
                    "gap_type": "implementation" if in_ched else "task_based",
                    "impact_score": round(abs(weight), 4),
                    "user_proficiency": user_proficiency,
                })
            print(f"DEBUG: skill {skill_id}, weight={weight}, prof={user_proficiency}")
        # Sort by impact score
        gaps.sort(key=lambda x: x["impact_score"], reverse=True)
        # Fill from SHAP if few gaps found
        if len(gaps) < 3:
            for factor in shap_explanation.get("top_protective_factors", []):
                skill_id = factor["skill"]
                if not skill_id.startswith("skill_"):
                    continue
                if any(g["skill_id"] == skill_id for g in gaps):
                    continue
                user_proficiency = skills.get(skill_id, 3)
                if user_proficiency < 4:
                    in_ched = skill_id in ched_skill_ids
                    gaps.append({
                        "skill_id": skill_id,
                        "skill_label": _get_skill_label(skill_id, cmos),
                        "in_ched_cmo": in_ched,
                        "gap_type": "implementation" if in_ched else "design",
                        "impact_score": round(factor["contribution"], 4),
                        "user_proficiency": user_proficiency,
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

    print(f"=== ASSESSMENT DEBUG ===")
    print(f"degree_program: {body.degree_program}")
    print(f"job_title: {body.job_title}")
    print(f"skills received: {skills}")
    print(f"task_distribution: {task_distribution}")
    print(f"use_typical: {use_typical}")

    # If no skills provided, use program typical profile (proficiency=3)
    effective_skills = skills if skills else _get_program_typical_skills(body.degree_program)

    # For custom jobs, find the job's task distribution
    is_custom_job = False
    if body.job_title:
        jobs_data = _load_jobs()
        input_lower = body.job_title.lower().strip()

        # Search for the job across all programs
        matched_job = None
        for prog, program_jobs in jobs_data.items():
            for job in program_jobs:
                job_title_cmp = job["title"].lower().strip()
                if job_title_cmp == input_lower or input_lower in job_title_cmp or job_title_cmp in input_lower:
                    matched_job = job
                    break
            if matched_job:
                break

        # If we found a matching job and it's different from expected program jobs
        if matched_job:
            # Use the matched job's task distribution
            task_distribution = matched_job.get("tasks", {})
            is_custom_job = matched_job.get("title", "") != body.job_title

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

    try:
        shap_explanation = explain_prediction(
            result["X"], body.degree_program, effective_skills, task_distribution,
        )
    except Exception as e:
        print(f"SHAP error: {e}")
        shap_explanation = {"top_risk_factors": [], "top_protective_factors": []}

    cmos = _load_cmos()
    print(f"Computing skill gaps with effective_skills: {effective_skills}")
    skill_gaps = _compute_skill_gaps(
        body.degree_program, effective_skills, shap_explanation, cmos, use_typical=use_typical
    )
    print(f"Skill gaps computed: {skill_gaps}")

    try:
        print(f"Generating recommendations for {len(skill_gaps)} gaps")
        recommendations = generate_recommendations(skill_gaps, body.degree_program, body.job_title)
        print(f"Recommendations generated: {len(recommendations)}")
    except Exception as e:
        print(f"Recommendation error: {e}")
        recommendations = []

    # Get matched job info for response
    matched_job_for_response = None
    if body.job_title and task_distribution:
        jobs_data = _load_jobs()
        input_lower = body.job_title.lower().strip()
        for prog, program_jobs in jobs_data.items():
            for job in program_jobs:
                job_title_cmp = job["title"].lower().strip()
                if job_title_cmp == input_lower or input_lower in job_title_cmp or job_title_cmp in input_lower:
                    matched_job_for_response = {
                        "title": job["title"],
                        "source_program": prog,
                        "task_distribution": task_distribution,
                    }
                    break
            if matched_job_for_response:
                break

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
        "analysis_meta": {
            "input_job_title": body.job_title,
            "matched_job": matched_job_for_response,
            "used_task_distribution": bool(task_distribution),
        },
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
