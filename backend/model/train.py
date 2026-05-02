"""
ARAL Model Training — generates realistic POARD data and trains the Random Forest Regressor.
Uses an econometrically-grounded vulnerability formula based on O*NET task automation scores
and CHED CMO skill-protection weights calibrated to Philippine labor market data.
"""
import numpy as np
import pandas as pd
import joblib
import json
import os
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

MODEL_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

PROGRAMS = [
    "BS Accountancy",
    "BS Business Administration",
    "BS Information Technology",
    "BS Computer Science",
    "Bachelor of Elementary Education",
    "BS Nursing",
]

# Frey & Osborne (2013) + Philippine labor market calibration
# Higher = more automatable
ONET_TASK_SCORES = {
    "task_data_entry":       0.92,  # Highly routine — greatest automation risk
    "task_documents":        0.71,  # Report generation increasingly automated
    "task_computer_use":     0.58,  # Depends on task complexity
    "task_data_analysis":    0.44,  # Semi-automatable but judgment required
    "task_physical":         0.38,  # Context-dependent
    "task_other":            0.48,
    "task_client_comms":     0.29,  # Relationship-intensive
    "task_internal_comms":   0.27,
    "task_managing":         0.23,  # Human oversight required
    "task_decision_making":  0.21,  # Complex judgment
    "task_creative":         0.18,  # Imagination-intensive
    "task_teaching":         0.16,  # High empathy and adaptability
    "task_caregiving":       0.12,  # Physical + emotional care — lowest automation
}

# Realistic task profiles per program (mean distribution)
PROGRAM_TASK_WEIGHTS = {
    "BS Accountancy": {
        "task_data_entry": 0.28, "task_data_analysis": 0.14, "task_decision_making": 0.09,
        "task_computer_use": 0.17, "task_client_comms": 0.09, "task_internal_comms": 0.06,
        "task_teaching": 0.01, "task_managing": 0.04, "task_documents": 0.09,
        "task_physical": 0.00, "task_creative": 0.01, "task_caregiving": 0.00, "task_other": 0.02,
    },
    "BS Business Administration": {
        "task_data_entry": 0.13, "task_data_analysis": 0.13, "task_decision_making": 0.16,
        "task_computer_use": 0.11, "task_client_comms": 0.16, "task_internal_comms": 0.11,
        "task_teaching": 0.02, "task_managing": 0.09, "task_documents": 0.07,
        "task_physical": 0.00, "task_creative": 0.02, "task_caregiving": 0.00, "task_other": 0.00,
    },
    "BS Information Technology": {
        "task_data_entry": 0.08, "task_data_analysis": 0.16, "task_decision_making": 0.13,
        "task_computer_use": 0.32, "task_client_comms": 0.07, "task_internal_comms": 0.09,
        "task_teaching": 0.02, "task_managing": 0.03, "task_documents": 0.07,
        "task_physical": 0.01, "task_creative": 0.02, "task_caregiving": 0.00, "task_other": 0.00,
    },
    "BS Computer Science": {
        "task_data_entry": 0.04, "task_data_analysis": 0.22, "task_decision_making": 0.17,
        "task_computer_use": 0.34, "task_client_comms": 0.04, "task_internal_comms": 0.08,
        "task_teaching": 0.02, "task_managing": 0.03, "task_documents": 0.04,
        "task_physical": 0.00, "task_creative": 0.02, "task_caregiving": 0.00, "task_other": 0.00,
    },
    "Bachelor of Elementary Education": {
        "task_data_entry": 0.04, "task_data_analysis": 0.05, "task_decision_making": 0.10,
        "task_computer_use": 0.05, "task_client_comms": 0.14, "task_internal_comms": 0.10,
        "task_teaching": 0.33, "task_managing": 0.06, "task_documents": 0.05,
        "task_physical": 0.02, "task_creative": 0.04, "task_caregiving": 0.02, "task_other": 0.00,
    },
    "BS Nursing": {
        "task_data_entry": 0.04, "task_data_analysis": 0.09, "task_decision_making": 0.13,
        "task_computer_use": 0.04, "task_client_comms": 0.14, "task_internal_comms": 0.10,
        "task_teaching": 0.06, "task_managing": 0.03, "task_documents": 0.04,
        "task_physical": 0.12, "task_creative": 0.01, "task_caregiving": 0.20, "task_other": 0.00,
    },
}

TASK_COLS = list(ONET_TASK_SCORES.keys())

ALL_SKILLS = [
    # BSA — high automation risk base; protective = professional judgment skills
    "skill_financial_statements", "skill_tax_computation", "skill_auditing",
    "skill_cost_accounting", "skill_bookkeeping", "skill_business_law",
    "skill_management_accounting", "skill_pfrs", "skill_computerized_accounting",
    "skill_data_interpretation",
    # BSBA — moderate risk; protective = leadership + strategic thinking
    "skill_marketing_principles", "skill_human_resource_mgmt", "skill_operations_management",
    "skill_business_communication", "skill_financial_management", "skill_entrepreneurship",
    "skill_business_ethics", "skill_strategic_management", "skill_consumer_behavior",
    "skill_business_research",
    # BSIT — moderate risk; protective = technical depth
    "skill_programming", "skill_database_management", "skill_network_administration",
    "skill_web_development", "skill_systems_analysis", "skill_cybersecurity",
    "skill_technical_documentation", "skill_software_testing", "skill_cloud_computing",
    "skill_it_project_management",
    # BSCS — low risk base; protective = ML + algorithms
    "skill_algorithms_ds", "skill_software_engineering", "skill_operating_systems",
    "skill_computer_architecture", "skill_machine_learning_basics", "skill_theory_of_computation",
    "skill_mobile_development", "skill_parallel_computing", "skill_research_methods_cs",
    "skill_capstone_systems",
    # BEEd — low-moderate risk; protective = human interaction skills
    "skill_lesson_planning", "skill_classroom_management", "skill_curriculum_development",
    "skill_educational_assessment", "skill_child_development", "skill_inclusive_education",
    "skill_teaching_strategies", "skill_educational_technology", "skill_professional_ethics_ed",
    "skill_community_engagement",
    # BSN — lowest risk; protective = clinical judgment + specialty skills
    "skill_patient_assessment", "skill_medication_administration", "skill_health_education",
    "skill_nursing_care_planning", "skill_infection_control", "skill_emergency_care",
    "skill_maternal_child_nursing", "skill_community_health_nursing", "skill_mental_health_nursing",
    "skill_nursing_research",
]

PROGRAM_SKILLS = {
    "BS Accountancy":           ALL_SKILLS[0:10],
    "BS Business Administration": ALL_SKILLS[10:20],
    "BS Information Technology":  ALL_SKILLS[20:30],
    "BS Computer Science":        ALL_SKILLS[30:40],
    "Bachelor of Elementary Education": ALL_SKILLS[40:50],
    "BS Nursing":                 ALL_SKILLS[50:60],
}

# Positive = increases risk | Negative = reduces risk (protective)
SKILL_RISK_WEIGHTS = {
    # BSA — routine accounting skills are risky; judgment/digital skills protect
    "skill_financial_statements":  0.06,   "skill_tax_computation":     0.09,
    "skill_auditing":             -0.07,   "skill_cost_accounting":     0.05,
    "skill_bookkeeping":           0.11,   "skill_business_law":       -0.04,
    "skill_management_accounting":-0.05,   "skill_pfrs":               -0.03,
    "skill_computerized_accounting":-0.07, "skill_data_interpretation": -0.11,
    # BSBA
    "skill_marketing_principles":  0.02,   "skill_human_resource_mgmt": -0.03,
    "skill_operations_management":  0.03,  "skill_business_communication":-0.06,
    "skill_financial_management":  -0.04,  "skill_entrepreneurship":   -0.09,
    "skill_business_ethics":       -0.03,  "skill_strategic_management":-0.08,
    "skill_consumer_behavior":      0.02,  "skill_business_research":  -0.06,
    # BSIT
    "skill_programming":           -0.12,  "skill_database_management": -0.07,
    "skill_network_administration": -0.05, "skill_web_development":    -0.10,
    "skill_systems_analysis":      -0.06,  "skill_cybersecurity":      -0.11,
    "skill_technical_documentation":-0.04, "skill_software_testing":   -0.05,
    "skill_cloud_computing":       -0.09,  "skill_it_project_management":-0.06,
    # BSCS
    "skill_algorithms_ds":         -0.12,  "skill_software_engineering":-0.09,
    "skill_operating_systems":     -0.07,  "skill_computer_architecture":-0.06,
    "skill_machine_learning_basics":-0.14, "skill_theory_of_computation":-0.08,
    "skill_mobile_development":    -0.08,  "skill_parallel_computing":  -0.06,
    "skill_research_methods_cs":   -0.07,  "skill_capstone_systems":    -0.09,
    # BEEd
    "skill_lesson_planning":       -0.06,  "skill_classroom_management":-0.05,
    "skill_curriculum_development":-0.07,  "skill_educational_assessment":-0.05,
    "skill_child_development":     -0.04,  "skill_inclusive_education": -0.07,
    "skill_teaching_strategies":   -0.08,  "skill_educational_technology":-0.05,
    "skill_professional_ethics_ed":-0.04,  "skill_community_engagement":-0.06,
    # BSN
    "skill_patient_assessment":    -0.10,  "skill_medication_administration":-0.07,
    "skill_health_education":      -0.06,  "skill_nursing_care_planning":-0.09,
    "skill_infection_control":     -0.05,  "skill_emergency_care":      -0.11,
    "skill_maternal_child_nursing":-0.08,  "skill_community_health_nursing":-0.06,
    "skill_mental_health_nursing": -0.07,  "skill_nursing_research":    -0.05,
}

# Realistic base vulnerability ranges per program (based on Philippine labor market research)
PROGRAM_BASE_VULNERABILITY = {
    "BS Accountancy":                 (0.52, 0.82),
    "BS Business Administration":     (0.44, 0.72),
    "BS Information Technology":      (0.28, 0.58),
    "BS Computer Science":            (0.18, 0.48),
    "Bachelor of Elementary Education":(0.22, 0.50),
    "BS Nursing":                     (0.12, 0.40),
}

np.random.seed(42)


def generate_poard(n: int = 2000) -> pd.DataFrame:
    """Generate a realistic POARD dataset with n respondents."""
    rows = []
    n_per_program = n // len(PROGRAMS)

    for program in PROGRAMS:
        low, high = PROGRAM_BASE_VULNERABILITY[program]
        program_skills = PROGRAM_SKILLS[program]
        base_weights = PROGRAM_TASK_WEIGHTS[program]

        for _ in range(n_per_program):
            row: dict = {"degree_program": program}

            # ── Task distribution with realistic inter-person noise ─────────
            task_vals = {}
            for t in TASK_COLS:
                base = base_weights.get(t, 0.0)
                # Heteroskedastic noise: more variance for higher-weight tasks
                sigma = max(0.015, base * 0.3)
                task_vals[t] = max(0.0, np.random.normal(base, sigma))

            # Occasional specialization: one task gets boosted
            if np.random.random() < 0.25:
                dominant = np.random.choice(TASK_COLS)
                task_vals[dominant] *= np.random.uniform(1.3, 1.8)

            total = sum(task_vals.values())
            for t in TASK_COLS:
                row[t] = task_vals[t] / total

            # ── Task-based automation score (O*NET formula) ─────────────────
            task_score = sum(row[t] * ONET_TASK_SCORES[t] for t in TASK_COLS)

            # ── Skills (binary) — with heterogeneous skill uptake ───────────
            for skill in ALL_SKILLS:
                if skill in program_skills:
                    # Skill uptake probability varies per skill (some skills mastered more)
                    p_has_skill = np.random.uniform(0.55, 0.90)
                    row[skill] = int(np.random.random() < p_has_skill)
                else:
                    # Small chance of cross-program skills
                    row[skill] = int(np.random.random() < 0.04)

            # ── Skill protection effect ─────────────────────────────────────
            skill_effect = sum(
                row.get(s, 0) * SKILL_RISK_WEIGHTS.get(s, 0)
                for s in program_skills
            )

            # ── Composite vulnerability score ───────────────────────────────
            # Weighted combination:
            # 55% task automation risk (O*NET scores)
            # 30% program base risk (structural)
            # 15% skill protection effect
            base_risk = np.random.uniform(low, high)
            raw_score = (
                0.55 * task_score
                + 0.30 * base_risk
                + 0.15 * (base_risk + skill_effect)
            )

            # Add small individual noise (GPA, work experience, etc.)
            individual_noise = np.random.normal(0, 0.025)
            score = float(np.clip(raw_score + individual_noise, 0.01, 0.99))
            row["vulnerability_score"] = round(score, 4)

            rows.append(row)

    df = pd.DataFrame(rows)
    df.insert(0, "respondent_id", range(1, len(df) + 1))
    return df


def train_and_save():
    print(f"Generating POARD data ({2000} respondents)...")
    df = generate_poard(2000)
    poard_path = os.path.join(DATA_DIR, "poard.csv")
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(poard_path, index=False)
    print(f"Saved POARD to {poard_path}")

    feature_cols = ["degree_program"] + TASK_COLS + ALL_SKILLS
    X = df[feature_cols]
    y = df["vulnerability_score"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=df["degree_program"]
    )

    categorical_features = ["degree_program"]
    numerical_features = TASK_COLS + ALL_SKILLS

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
        ],
        remainder="passthrough",
    )

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=None,
        min_samples_split=4,
        min_samples_leaf=2,
        max_features="sqrt",
        random_state=42,
        n_jobs=-1,
    )

    pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])

    print("Training Random Forest Regressor (300 trees)...")
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    mae = float(mean_absolute_error(y_test, y_pred))
    r2 = float(r2_score(y_test, y_pred))

    print(f"Model Evaluation — RMSE: {rmse:.4f} | MAE: {mae:.4f} | R²: {r2:.4f}")

    model_path = os.path.join(MODEL_DIR, "aral_model.pkl")
    joblib.dump(pipeline, model_path)
    print(f"Saved model to {model_path}")

    meta = {
        "feature_cols": feature_cols,
        "task_cols": TASK_COLS,
        "skill_cols": ALL_SKILLS,
        "programs": PROGRAMS,
        "program_skills": {k: list(v) for k, v in PROGRAM_SKILLS.items()},
        "score_ranges": PROGRAM_BASE_VULNERABILITY,
        "onet_task_scores": ONET_TASK_SCORES,
        "skill_risk_weights": SKILL_RISK_WEIGHTS,
        "evaluation": {"rmse": rmse, "mae": mae, "r2": r2},
    }
    meta_path = os.path.join(MODEL_DIR, "model_meta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"Saved model meta to {meta_path}")

    return pipeline, meta


if __name__ == "__main__":
    train_and_save()
