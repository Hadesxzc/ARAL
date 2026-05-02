"""
ARAL FastAPI backend — Automation Risk Assessment for Filipino Graduates
University of Saint Louis Tuguegarao
"""
import os
import sys

# Ensure backend/ is on Python path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.programs import router as programs_router
from routes.assessment import router as assessment_router
from routes.analytics import router as analytics_router

app = FastAPI(
    title="ARAL API",
    description="Automation Risk Assessment for Filipino Graduates",
    version="1.0.0",
)

# CORS — allow all origins in dev (frontend served separately)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# All routes served under /api prefix (matching the proxy path)
app.include_router(programs_router, prefix="/api")
app.include_router(assessment_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")


@app.get("/api/healthz")
def health_check():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "ARAL API — see /api/healthz"}
