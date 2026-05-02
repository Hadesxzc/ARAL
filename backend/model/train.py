"""
ARAL Mock Model Training Script
Generates synthetic POARD data and trains the Random Forest Regressor.
Run this once to produce aral_model.pkl and aral_encoder.pkl.
"""
import numpy as np
import pandas as pd
import joblib
import json
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
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

SCORE_RANGES = {
    "BS Accountancy": (0.55, 0.85),
    "BS Business Administration": (0.50, 0.80),
    "BS Information Technology": (0.30, 0.60),
    "BS Computer Science": (0.20, 0.50),
    "Bachelor of Elementary Education": (0.25, 0.55),
    "BS Nursing": (0.15, 0.45),
}

TASK_COLS = [
    "task_data_entry", "task_data_analysis", "task_decision_making",
    "task_computer_use", "task_client_comms", "task_internal_comms",
    "task_teaching", "task_managing", "task_documents", "task_physical",
    "task_creative", "task_caregiving", "task_other"
]

ONET_TASK_SCORES = {
    "task_data_entry": 0.92,
    "task_data_analysis": 0.48,
    "task_decision_making": 0.22,
    "task_computer_use": 0.65,
    "task_client_comms": 0.30,
    "task_internal_comms": 0.28,
    "task_teaching": 0.18,
    "task_managing": 0.25,
    "task_documents": 0.72,
    "task_physical": 0.35,
    "task_creative": 0.20,
    "task_caregiving": 0.15,
    "task_other": 0.50,
}

PROGRAM_TASK_WEIGHTS = {
    "BS Accountancy": {
        "task_data_entry": 0.30, "task_data_analysis": 0.15, "task_decision_making": 0.08,
        "task_computer_use": 0.18, "task_client_comms": 0.08, "task_internal_comms": 0.05,
        "task_teaching": 0.02, "task_managing": 0.03, "task_documents": 0.08,
        "task_physical": 0.00, "task_creative": 0.00, "task_caregiving": 0.00, "task_other": 0.03
    },
    "BS Business Administration": {
        "task_data_entry": 0.15, "task_data_analysis": 0.12, "task_decision_making": 0.15,
        "task_computer_use": 0.12, "task_client_comms": 0.15, "task_internal_comms": 0.10,
        "task_teaching": 0.02, "task_managing": 0.08, "task_documents": 0.08,
        "task_physical": 0.00, "task_creative": 0.02, "task_caregiving": 0.00, "task_other": 0.01
    },
    "BS Information Technology": {
        "task_data_entry": 0.10, "task_data_analysis": 0.15, "task_decision_making": 0.12,
        "task_computer_use": 0.30, "task_client_comms": 0.08, "task_internal_comms": 0.08,
        "task_teaching": 0.02, "task_managing": 0.03, "task_documents": 0.07,
        "task_physical": 0.01, "task_creative": 0.03, "task_caregiving": 0.00, "task_other": 0.01
    },
    "BS Computer Science": {
        "task_data_entry": 0.05, "task_data_analysis": 0.20, "task_decision_making": 0.15,
        "task_computer_use": 0.35, "task_client_comms": 0.05, "task_internal_comms": 0.07,
        "task_teaching": 0.02, "task_managing": 0.02, "task_documents": 0.05,
        "task_physical": 0.00, "task_creative": 0.03, "task_caregiving": 0.00, "task_other": 0.01
    },
    "Bachelor of Elementary Education": {
        "task_data_entry": 0.05, "task_data_analysis": 0.05, "task_decision_making": 0.10,
        "task_computer_use": 0.05, "task_client_comms": 0.15, "task_internal_comms": 0.10,
        "task_teaching": 0.30, "task_managing": 0.05, "task_documents": 0.05,
        "task_physical": 0.02, "task_creative": 0.05, "task_caregiving": 0.03, "task_other": 0.00
    },
    "BS Nursing": {
        "task_data_entry": 0.05, "task_data_analysis": 0.08, "task_decision_making": 0.12,
        "task_computer_use": 0.05, "task_client_comms": 0.15, "task_internal_comms": 0.10,
        "task_teaching": 0.05, "task_managing": 0.03, "task_documents": 0.05,
        "task_physical": 0.10, "task_creative": 0.02, "task_caregiving": 0.20, "task_other": 0.00
    },
}

ALL_SKILLS = [
    # BSA
    "skill_financial_statements", "skill_tax_computation", "skill_auditing",
    "skill_cost_accounting", "skill_bookkeeping", "skill_business_law",
    "skill_management_accounting", "skill_pfrs", "skill_computerized_accounting",
    "skill_data_interpretation",
    # BSBA
    "skill_marketing_principles", "skill_human_resource_mgmt", "skill_operations_management",
    "skill_business_communication", "skill_financial_management", "skill_entrepreneurship",
    "skill_business_ethics", "skill_strategic_management", "skill_consumer_behavior",
    "skill_business_research",
    # BSIT
    "skill_programming", "skill_database_management", "skill_network_administration",
    "skill_web_development", "skill_systems_analysis", "skill_cybersecurity",
    "skill_technical_documentation", "skill_software_testing", "skill_cloud_computing",
    "skill_it_project_management",
    # BSCS
    "skill_algorithms_ds", "skill_software_engineering", "skill_operating_systems",
    "skill_computer_architecture", "skill_machine_learning_basics", "skill_theory_of_computation",
    "skill_mobile_development", "skill_parallel_computing", "skill_research_methods_cs",
    "skill_capstone_systems",
    # BEED
    "skill_lesson_planning", "skill_classroom_management", "skill_curriculum_development",
    "skill_educational_assessment", "skill_child_development", "skill_inclusive_education",
    "skill_teaching_strategies", "skill_educational_technology", "skill_professional_ethics_ed",
    "skill_community_engagement",
    # BSN
    "skill_patient_assessment", "skill_medication_administration", "skill_health_education",
    "skill_nursing_care_planning", "skill_infection_control", "skill_emergency_care",
    "skill_maternal_child_nursing", "skill_community_health_nursing", "skill_mental_health_nursing",
    "skill_nursing_research",
]

PROGRAM_SKILLS = {
    "BS Accountancy": ALL_SKILLS[:10],
    "BS Business Administration": ALL_SKILLS[10:20],
    "BS Information Technology": ALL_SKILLS[20:30],
    "BS Computer Science": ALL_SKILLS[30:40],
    "Bachelor of Elementary Education": ALL_SKILLS[40:50],
    "BS Nursing": ALL_SKILLS[50:60],
}

SKILL_RISK_WEIGHTS = {
    "skill_financial_statements": 0.08, "skill_tax_computation": 0.10, "skill_auditing": -0.05,
    "skill_cost_accounting": 0.07, "skill_bookkeeping": 0.12, "skill_business_law": -0.03,
    "skill_management_accounting": -0.04, "skill_pfrs": -0.02, "skill_computerized_accounting": -0.06,
    "skill_data_interpretation": -0.09,
    "skill_marketing_principles": 0.03, "skill_human_resource_mgmt": -0.02, "skill_operations_management": 0.04,
    "skill_business_communication": -0.05, "skill_financial_management": -0.03, "skill_entrepreneurship": -0.07,
    "skill_business_ethics": -0.02, "skill_strategic_management": -0.06, "skill_consumer_behavior": 0.02,
    "skill_business_research": -0.05,
    "skill_programming": -0.10, "skill_database_management": -0.06, "skill_network_administration": -0.04,
    "skill_web_development": -0.08, "skill_systems_analysis": -0.05, "skill_cybersecurity": -0.09,
    "skill_technical_documentation": -0.03, "skill_software_testing": -0.04, "skill_cloud_computing": -0.08,
    "skill_it_project_management": -0.05,
    "skill_algorithms_ds": -0.10, "skill_software_engineering": -0.08, "skill_operating_systems": -0.06,
    "skill_computer_architecture": -0.05, "skill_machine_learning_basics": -0.12, "skill_theory_of_computation": -0.07,
    "skill_mobile_development": -0.07, "skill_parallel_computing": -0.05, "skill_research_methods_cs": -0.06,
    "skill_capstone_systems": -0.08,
    "skill_lesson_planning": -0.05, "skill_classroom_management": -0.04, "skill_curriculum_development": -0.06,
    "skill_educational_assessment": -0.04, "skill_child_development": -0.03, "skill_inclusive_education": -0.05,
    "skill_teaching_strategies": -0.06, "skill_educational_technology": -0.04, "skill_professional_ethics_ed": -0.03,
    "skill_community_engagement": -0.05,
    "skill_patient_assessment": -0.08, "skill_medication_administration": -0.06, "skill_health_education": -0.05,
    "skill_nursing_care_planning": -0.07, "skill_infection_control": -0.04, "skill_emergency_care": -0.09,
    "skill_maternal_child_nursing": -0.06, "skill_community_health_nursing": -0.05, "skill_mental_health_nursing": -0.05,
    "skill_nursing_research": -0.04,
}

np.random.seed(42)


def generate_mock_poard(n=1000):
    rows = []
    n_per_program = n // len(PROGRAMS)

    for program in PROGRAMS:
        low, high = SCORE_RANGES[program]
        program_skills = PROGRAM_SKILLS[program]
        base_weights = PROGRAM_TASK_WEIGHTS[program]

        for i in range(n_per_program):
            row = {"degree_program": program}

            # Task distribution with noise
            task_vals = {}
            for t in TASK_COLS:
                base = base_weights.get(t, 0.0)
                noise = np.random.normal(0, 0.03)
                task_vals[t] = max(0.0, base + noise)

            # Normalize to sum to 1
            total = sum(task_vals.values())
            for t in TASK_COLS:
                row[t] = task_vals[t] / total

            # Skills (binary) — active for this program
            for skill in ALL_SKILLS:
                if skill in program_skills:
                    # 60–90% of students in this program have the skill
                    row[skill] = int(np.random.random() < 0.75)
                else:
                    row[skill] = 0

            # Compute vulnerability score
            task_score = sum(row[t] * ONET_TASK_SCORES[t] for t in TASK_COLS)
            skill_effect = sum(
                row.get(s, 0) * SKILL_RISK_WEIGHTS.get(s, 0)
                for s in program_skills
            )
            base_score = np.random.uniform(low, high)
            score = 0.5 * task_score + 0.3 * base_score + 0.2 * (base_score + skill_effect)
            score = float(np.clip(score, 0.0, 1.0))
            row["vulnerability_score"] = round(score, 4)

            rows.append(row)

    df = pd.DataFrame(rows)
    df.insert(0, "respondent_id", range(1, len(df) + 1))
    return df


def train_and_save():
    print("Generating mock POARD data (1000 respondents)...")
    df = generate_mock_poard(1000)
    poard_path = os.path.join(DATA_DIR, "poard.csv")
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

    preprocessor = ColumnTransformer(transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
    ], remainder="passthrough")

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=None,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", model),
    ])

    print("Training Random Forest Regressor...")
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
        "program_skills": PROGRAM_SKILLS,
        "score_ranges": SCORE_RANGES,
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
