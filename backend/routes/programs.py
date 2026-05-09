"""
GET /api/programs  — all 30 degree programs
GET /api/skills/{program}  — CHED CMO skills for a program
GET /api/jobs/{program}  — job titles for a program
GET /api/skills-by-job/{program}  — derive skills from a job's task distribution (for custom jobs)
"""
import json
import os
import urllib.parse
from fastapi import APIRouter, HTTPException

router = APIRouter()
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


# Mapping of task types to generic skills (for custom jobs not in CHED CMO curriculum)
TASK_TO_SKILLS = {
    "task_data_entry": [
        {"id": "skill_data_entry", "label": "Data Entry", "description": "Accurate and efficient data input and management"},
    ],
    "task_documents": [
        {"id": "skill_document_mgmt", "label": "Document Management", "description": "Create, organize, and maintain documents"},
    ],
    "task_computer_use": [
        {"id": "skill_digital_literacy", "label": "Digital Literacy", "description": "Proficient use of computers and software applications"},
    ],
    "task_data_analysis": [
        {"id": "skill_data_analysis", "label": "Data Analysis", "description": "Analyze and interpret data to inform decisions"},
        {"id": "skill_analytics", "label": "Analytics", "description": "Use analytical tools and techniques"},
    ],
    "task_client_comms": [
        {"id": "skill_communication", "label": "Communication", "description": "Effective written and verbal communication"},
        {"id": "skill_client_relations", "label": "Client Relations", "description": "Build and maintain client relationships"},
    ],
    "task_internal_comms": [
        {"id": "skill_teamwork", "label": "Teamwork", "description": "Collaborate effectively with colleagues"},
        {"id": "skill_interpersonal", "label": "Interpersonal Skills", "description": "Build professional relationships at work"},
    ],
    "task_decision_making": [
        {"id": "skill_critical_thinking", "label": "Critical Thinking", "description": "Analyze situations and make sound decisions"},
        {"id": "skill_problem_solving", "label": "Problem Solving", "description": "Identify and resolve problems efficiently"},
    ],
    "task_managing": [
        {"id": "skill_management", "label": "Management", "description": "Organize and oversee work processes"},
        {"id": "skill_leadership", "label": "Leadership", "description": "Guide and motivate teams"},
    ],
    "task_creative": [
        {"id": "skill_creativity", "label": "Creativity", "description": "Generate innovative ideas and solutions"},
    ],
    "task_teaching": [
        {"id": "skill_teaching", "label": "Teaching", "description": "Instruct and guide learners"},
        {"id": "skill_mentoring", "label": "Mentoring", "description": "Coach and develop others"},
    ],
    "task_physical": [
        {"id": "skill_physical", "label": "Physical Skills", "description": "Manual dexterity and physical coordination"},
    ],
    "task_caregiving": [
        {"id": "skill_caregiving", "label": "Caregiving", "description": "Provide care and support to others"},
        {"id": "skill_empathy", "label": "Empathy", "description": "Understand and share the feelings of others"},
    ],
}

PROGRAMS = [
    "BS Accountancy", "BS Business Administration", "BS Information Technology",
    "BS Computer Science", "Bachelor of Elementary Education",
    "Bachelor of Secondary Education", "BS Nursing", "BS Psychology",
    "BS Tourism Management", "BS Hospitality Management", "BS Civil Engineering",
    "BS Electrical Engineering", "BS Mechanical Engineering",
    "BS Electronics Engineering", "BS Industrial Engineering", "BS Architecture",
    "BS Criminology", "AB Communication", "BS Social Work", "BS Pharmacy",
    "BS Medical Technology", "BS Physical Therapy", "BS Agriculture",
    "BS Environmental Science", "BS Legal Management", "BS Food Technology",
    "BS Computer Engineering", "BS Chemical Engineering", "BS Biology",
    "BS Marketing Management",
]


def _load_cmos() -> dict:
    with open(os.path.join(DATA_DIR, "ched_cmos.json")) as f:
        return json.load(f)


def _load_jobs() -> dict:
    path = os.path.join(DATA_DIR, "jobs_by_program.json")
    with open(path) as f:
        return json.load(f)


def _decode_program(program: str) -> str:
    decoded = urllib.parse.unquote(program)
    if decoded in PROGRAMS:
        return decoded
    match = next((p for p in PROGRAMS if p.lower() == decoded.lower()), None)
    if not match:
        raise HTTPException(status_code=404, detail=f"Program '{decoded}' not found")
    return match


@router.get("/programs")
def get_programs():
    return {"programs": PROGRAMS}


@router.get("/skills/{program}")
def get_skills(program: str):
    decoded = _decode_program(program)
    cmos = _load_cmos()
    if decoded not in cmos:
        raise HTTPException(status_code=404, detail=f"CMO data not found for '{decoded}'")
    data = cmos[decoded]
    return {
        "program": decoded,
        "cmo_reference": data.get("cmo_reference", ""),
        "skills": data.get("skills", []),
    }


@router.get("/jobs/{program}")
def get_jobs(program: str):
    decoded = _decode_program(program)
    jobs_data = _load_jobs()
    jobs = jobs_data.get(decoded, [])
    return {
        "program": decoded,
        "jobs": [j["title"] for j in jobs],
        "jobs_with_tasks": jobs,
    }


@router.get("/skills-by-job/{program}")
def get_skills_by_job(program: str, job_title: str = ""):
    """
    Derive skills from a job's task distribution.
    This is used for custom jobs not in the CHED CMO curriculum.
    If job_title is provided, search across ALL programs to find a matching job
    and derive skills from its task distribution.
    """
    decoded = _decode_program(program)

    # If no job_title provided or it's empty, return CHED CMO skills
    if not job_title:
        return get_skills(decoded)

    jobs_data = _load_jobs()
    input_lower = job_title.lower().strip()

    # Search across ALL programs for a matching job (partial match)
    matched_job = None
    matched_job_source = None

    for prog, program_jobs in jobs_data.items():
        for job in program_jobs:
            job_title_cmp = job["title"].lower().strip()
            # Exact match or partial match (input is contained in job title)
            if job_title_cmp == input_lower or input_lower in job_title_cmp or job_title_cmp in input_lower:
                matched_job = job
                matched_job_source = prog
                break
        if matched_job:
            break

    # If no job found at all, return CHED CMO skills as fallback
    if not matched_job:
        return get_skills(decoded)

    # Derive skills from job's task distribution
    task_dist = matched_job.get("tasks", {})
    derived_skills = []
    seen_skill_ids = set()

    # Sort tasks by weight (highest first) and extract skills
    sorted_tasks = sorted(task_dist.items(), key=lambda x: x[1], reverse=True)

    for task_type, weight in sorted_tasks:
        if weight <= 0:
            continue
        if task_type in TASK_TO_SKILLS:
            for skill in TASK_TO_SKILLS[task_type]:
                if skill["id"] not in seen_skill_ids:
                    seen_skill_ids.add(skill["id"])
                    derived_skills.append({
                        **skill,
                        "source": "task_based",
                        "task_weight": weight,
                    })

    # If we couldn't derive enough skills, add from CHED CMO as backup
    if len(derived_skills) < 4:
        cmos = _load_cmos()
        if decoded in cmos:
            ched_skills = cmos[decoded].get("skills", [])
            for skill in ched_skills:
                if skill["id"] not in seen_skill_ids:
                    seen_skill_ids.add(skill["id"])
                    derived_skills.append({
                        "id": skill["id"],
                        "label": skill["label"],
                        "description": skill.get("description", ""),
                        "source": "ched_cmo_backup",
                        "task_weight": 0,
                    })

    # Add task distribution info
    task_info = {
        "is_custom_job": True,
        "job_title": matched_job["title"],
        "job_found_in_program": matched_job_source,
        "task_distribution": task_dist,
    }

    return {
        "program": decoded,
        "skills": derived_skills[:8],  # Limit to 8 skills
        "skill_source": "task_based",
        "task_info": task_info,
    }
