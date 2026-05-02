"""
GET /api/programs  — all 30 degree programs
GET /api/skills/{program}  — CHED CMO skills for a program
GET /api/jobs/{program}  — job titles for a program
"""
import json
import os
import urllib.parse
from fastapi import APIRouter, HTTPException

router = APIRouter()
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

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
