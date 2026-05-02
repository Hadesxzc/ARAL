# ARAL — Automation Risk Assessment for Lokalized Graduates

**University of Saint Louis Tuguegarao** — Thesis Research System

## What It Does

ARAL predicts how vulnerable a Filipino college graduate's career is to AI and automation. It:
1. Collects degree program, job title, skill ratings (CHED CMO), and task time distribution
2. Runs a Random Forest Regressor to output a 0–1 vulnerability score
3. Applies SHAP explainability to show which factors drive the score
4. Identifies skill gaps against CHED CMO curricula
5. Recommends free courses (via Gemini AI or fallback) from Coursera, edX, TESDA, etc.

## Architecture

| Layer | Technology |
|---|---|
| Frontend | React + TypeScript + Vite (artifacts/aral) |
| Backend | Python FastAPI (backend/) |
| API Contract | OpenAPI spec (lib/api-spec/openapi.yaml) → codegen |
| API Client | React Query hooks (lib/api-client-react/) |
| ML Model | scikit-learn Random Forest Regressor |
| Explainability | SHAP TreeExplainer |
| AI Recommendations | Google Gemini 2.5 Flash (GEMINI_API_KEY env var) |
| Dataset | POARD — synthetic dataset generated at backend/data/poard.csv |

## Pages

- `/` — Landing page (hero, stats, how it works, team)
- `/assessment` — 4-step wizard (program → job title → skills → tasks)
- `/results` — Results dashboard (gauge, SHAP chart, skill gaps, courses, comparison)
- `/about` — Research methodology documentation
- `/admin` — Research dashboard (Overview, SHAP Analysis, Per-Program, Curriculum Gaps, SUS Evaluation)

## Programs Covered

BS Accountancy, BS Business Administration, BS Information Technology, BS Computer Science, Bachelor of Elementary Education, BS Nursing

## Risk Levels

| Level | Range | Color |
|---|---|---|
| Low | 0.00–0.29 | Green #22c55e |
| Moderate | 0.30–0.49 | Amber #f59e0b |
| High | 0.50–0.69 | Orange #f97316 |
| Very High | 0.70–1.00 | Red #ef4444 |

## Model Performance

- RMSE: 0.0473 (threshold: < 0.10) ✓
- MAE: 0.0388 (threshold: < 0.08) ✓
- R²: 0.9033 (threshold: > 0.75) ✓

## Workflows

- `artifacts/api-server: API Server` → runs `backend/start.sh` (trains model if needed, starts FastAPI on PORT)
- `artifacts/aral: web` → Vite dev server for React frontend

## Environment Variables

- `GEMINI_API_KEY` — optional; enables live Gemini course recommendations (falls back to curated courses if absent)
- `SESSION_SECRET` — for session management
- `PORT` — assigned per artifact by the proxy

## Key Files

- `backend/main.py` — FastAPI app entrypoint
- `backend/routes/assessment.py` — Core assessment + SHAP pipeline
- `backend/routes/analytics.py` — Research dashboard endpoints
- `backend/model/train.py` — POARD generation + RF training
- `backend/model/predict.py` — Inference + SHAP explanation
- `backend/gemini/recommend.py` — Gemini course recommendations
- `backend/data/ched_cmos.json` — CHED CMO skill definitions per program
- `lib/api-spec/openapi.yaml` — OpenAPI spec (source of truth)
- `lib/api-client-react/src/generated/api.ts` — Generated React Query hooks

## Codegen

After any OpenAPI spec change:
```bash
pnpm --filter @workspace/api-spec run codegen
```

## Research Team

- Gasmen, Kenneth R. — Lead Researcher
- Ignacio, John Jomer R. — Developer
- Maddara, Darren Bjorn P. — Data Analysis
- Tarayao, Mark Daniel B. — Developer
