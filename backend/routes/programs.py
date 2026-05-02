"""
GET /api/programs — list all covered degree programs
GET /api/skills/{program} — skills checklist for a degree program
"""
import json
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

PROGRAMS = [
    "BS Accountancy",
    "BS Business Administration",
    "BS Information Technology",
    "BS Computer Science",
    "Bachelor of Elementary Education",
    "BS Nursing",
]


def _load_cmos() -> dict:
    path = os.path.join(DATA_DIR, "ched_cmos.json")
    with open(path) as f:
        return json.load(f)


@router.get("/programs")
def get_programs():
    return {"programs": PROGRAMS}


@router.get("/skills/{program}")
def get_skills(program: str):
    cmos = _load_cmos()
    # URL decode and match
    import urllib.parse
    decoded = urllib.parse.unquote(program)

    if decoded not in cmos:
        # Try case-insensitive match
        match = next((k for k in cmos if k.lower() == decoded.lower()), None)
        if not match:
            raise HTTPException(status_code=404, detail=f"Program '{decoded}' not found")
        decoded = match

    data = cmos[decoded]
    return {
        "program": decoded,
        "cmo_reference": data.get("cmo_reference", ""),
        "skills": data.get("skills", []),
    }
