"""
ARAL Model Training — 30 Philippine degree programs, CHED CMO-aligned skills,
1-5 proficiency scale, 9,000 respondents.
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

# O*NET-calibrated task automation scores
ONET_TASK_SCORES = {
    "task_data_entry": 0.92, "task_documents": 0.71, "task_computer_use": 0.55,
    "task_data_analysis": 0.44, "task_physical": 0.38, "task_other": 0.48,
    "task_client_comms": 0.29, "task_internal_comms": 0.27,
    "task_managing": 0.23, "task_decision_making": 0.21,
    "task_creative": 0.18, "task_teaching": 0.16, "task_caregiving": 0.12,
}
TASK_COLS = list(ONET_TASK_SCORES.keys())

# Task distribution per program (mean profile)
PROGRAM_TASK_WEIGHTS = {
    "BS Accountancy":                   {"task_data_entry":0.28,"task_documents":0.14,"task_computer_use":0.17,"task_data_analysis":0.14,"task_physical":0.00,"task_other":0.02,"task_client_comms":0.09,"task_internal_comms":0.06,"task_managing":0.04,"task_decision_making":0.04,"task_creative":0.01,"task_teaching":0.01,"task_caregiving":0.00},
    "BS Business Administration":        {"task_data_entry":0.13,"task_documents":0.12,"task_computer_use":0.11,"task_data_analysis":0.13,"task_physical":0.00,"task_other":0.00,"task_client_comms":0.16,"task_internal_comms":0.11,"task_managing":0.09,"task_decision_making":0.16,"task_creative":0.02,"task_teaching":0.02,"task_caregiving":0.00},
    "BS Information Technology":         {"task_data_entry":0.08,"task_documents":0.08,"task_computer_use":0.34,"task_data_analysis":0.16,"task_physical":0.01,"task_other":0.00,"task_client_comms":0.07,"task_internal_comms":0.09,"task_managing":0.03,"task_decision_making":0.10,"task_creative":0.03,"task_teaching":0.01,"task_caregiving":0.00},
    "BS Computer Science":               {"task_data_entry":0.04,"task_documents":0.07,"task_computer_use":0.38,"task_data_analysis":0.22,"task_physical":0.00,"task_other":0.00,"task_client_comms":0.04,"task_internal_comms":0.10,"task_managing":0.03,"task_decision_making":0.08,"task_creative":0.02,"task_teaching":0.02,"task_caregiving":0.00},
    "Bachelor of Elementary Education":  {"task_data_entry":0.05,"task_documents":0.08,"task_computer_use":0.07,"task_data_analysis":0.06,"task_physical":0.02,"task_other":0.00,"task_client_comms":0.13,"task_internal_comms":0.09,"task_managing":0.05,"task_decision_making":0.10,"task_creative":0.05,"task_teaching":0.29,"task_caregiving":0.01},
    "Bachelor of Secondary Education":   {"task_data_entry":0.06,"task_documents":0.10,"task_computer_use":0.09,"task_data_analysis":0.07,"task_physical":0.01,"task_other":0.00,"task_client_comms":0.12,"task_internal_comms":0.09,"task_managing":0.05,"task_decision_making":0.10,"task_creative":0.04,"task_teaching":0.26,"task_caregiving":0.01},
    "BS Nursing":                         {"task_data_entry":0.06,"task_documents":0.10,"task_computer_use":0.05,"task_data_analysis":0.09,"task_physical":0.12,"task_other":0.00,"task_client_comms":0.13,"task_internal_comms":0.10,"task_managing":0.03,"task_decision_making":0.13,"task_creative":0.01,"task_teaching":0.05,"task_caregiving":0.13},
    "BS Psychology":                      {"task_data_entry":0.09,"task_documents":0.12,"task_computer_use":0.08,"task_data_analysis":0.12,"task_physical":0.00,"task_other":0.03,"task_client_comms":0.18,"task_internal_comms":0.10,"task_managing":0.04,"task_decision_making":0.13,"task_creative":0.02,"task_teaching":0.05,"task_caregiving":0.04},
    "BS Tourism Management":              {"task_data_entry":0.12,"task_documents":0.10,"task_computer_use":0.13,"task_data_analysis":0.08,"task_physical":0.02,"task_other":0.01,"task_client_comms":0.24,"task_internal_comms":0.10,"task_managing":0.06,"task_decision_making":0.08,"task_creative":0.04,"task_teaching":0.01,"task_caregiving":0.01},
    "BS Hospitality Management":          {"task_data_entry":0.09,"task_documents":0.09,"task_computer_use":0.10,"task_data_analysis":0.06,"task_physical":0.14,"task_other":0.00,"task_client_comms":0.22,"task_internal_comms":0.11,"task_managing":0.09,"task_decision_making":0.06,"task_creative":0.03,"task_teaching":0.01,"task_caregiving":0.00},
    "BS Civil Engineering":               {"task_data_entry":0.07,"task_documents":0.15,"task_computer_use":0.18,"task_data_analysis":0.16,"task_physical":0.06,"task_other":0.00,"task_client_comms":0.08,"task_internal_comms":0.11,"task_managing":0.07,"task_decision_making":0.10,"task_creative":0.01,"task_teaching":0.01,"task_caregiving":0.00},
    "BS Electrical Engineering":          {"task_data_entry":0.05,"task_documents":0.13,"task_computer_use":0.25,"task_data_analysis":0.17,"task_physical":0.06,"task_other":0.00,"task_client_comms":0.08,"task_internal_comms":0.10,"task_managing":0.04,"task_decision_making":0.10,"task_creative":0.01,"task_teaching":0.01,"task_caregiving":0.00},
    "BS Mechanical Engineering":          {"task_data_entry":0.05,"task_documents":0.13,"task_computer_use":0.22,"task_data_analysis":0.16,"task_physical":0.10,"task_other":0.00,"task_client_comms":0.06,"task_internal_comms":0.11,"task_managing":0.06,"task_decision_making":0.10,"task_creative":0.02,"task_teaching":0.01,"task_caregiving":0.00},
    "BS Electronics Engineering":         {"task_data_entry":0.05,"task_documents":0.11,"task_computer_use":0.32,"task_data_analysis":0.16,"task_physical":0.05,"task_other":0.00,"task_client_comms":0.07,"task_internal_comms":0.10,"task_managing":0.03,"task_decision_making":0.10,"task_creative":0.01,"task_teaching":0.00,"task_caregiving":0.00},
    "BS Industrial Engineering":          {"task_data_entry":0.09,"task_documents":0.13,"task_computer_use":0.18,"task_data_analysis":0.20,"task_physical":0.04,"task_other":0.01,"task_client_comms":0.07,"task_internal_comms":0.12,"task_managing":0.07,"task_decision_making":0.09,"task_creative":0.00,"task_teaching":0.00,"task_caregiving":0.00},
    "BS Architecture":                    {"task_data_entry":0.03,"task_documents":0.14,"task_computer_use":0.28,"task_data_analysis":0.10,"task_physical":0.02,"task_other":0.00,"task_client_comms":0.12,"task_internal_comms":0.11,"task_managing":0.05,"task_decision_making":0.08,"task_creative":0.07,"task_teaching":0.00,"task_caregiving":0.00},
    "BS Criminology":                     {"task_data_entry":0.08,"task_documents":0.13,"task_computer_use":0.11,"task_data_analysis":0.12,"task_physical":0.10,"task_other":0.00,"task_client_comms":0.14,"task_internal_comms":0.11,"task_managing":0.07,"task_decision_making":0.13,"task_creative":0.00,"task_teaching":0.01,"task_caregiving":0.00},
    "AB Communication":                   {"task_data_entry":0.05,"task_documents":0.12,"task_computer_use":0.17,"task_data_analysis":0.09,"task_physical":0.01,"task_other":0.01,"task_client_comms":0.18,"task_internal_comms":0.12,"task_managing":0.03,"task_decision_making":0.10,"task_creative":0.11,"task_teaching":0.01,"task_caregiving":0.00},
    "BS Social Work":                     {"task_data_entry":0.09,"task_documents":0.13,"task_computer_use":0.07,"task_data_analysis":0.09,"task_physical":0.01,"task_other":0.00,"task_client_comms":0.20,"task_internal_comms":0.11,"task_managing":0.04,"task_decision_making":0.12,"task_creative":0.01,"task_teaching":0.04,"task_caregiving":0.09},
    "BS Pharmacy":                        {"task_data_entry":0.11,"task_documents":0.13,"task_computer_use":0.14,"task_data_analysis":0.12,"task_physical":0.06,"task_other":0.01,"task_client_comms":0.20,"task_internal_comms":0.10,"task_managing":0.03,"task_decision_making":0.08,"task_creative":0.00,"task_teaching":0.02,"task_caregiving":0.00},
    "BS Medical Technology":              {"task_data_entry":0.11,"task_documents":0.11,"task_computer_use":0.13,"task_data_analysis":0.20,"task_physical":0.14,"task_other":0.00,"task_client_comms":0.07,"task_internal_comms":0.10,"task_managing":0.03,"task_decision_making":0.09,"task_creative":0.00,"task_teaching":0.01,"task_caregiving":0.01},
    "BS Physical Therapy":                {"task_data_entry":0.04,"task_documents":0.10,"task_computer_use":0.05,"task_data_analysis":0.10,"task_physical":0.24,"task_other":0.00,"task_client_comms":0.16,"task_internal_comms":0.08,"task_managing":0.02,"task_decision_making":0.14,"task_creative":0.00,"task_teaching":0.06,"task_caregiving":0.01},
    "BS Agriculture":                     {"task_data_entry":0.07,"task_documents":0.11,"task_computer_use":0.08,"task_data_analysis":0.13,"task_physical":0.18,"task_other":0.00,"task_client_comms":0.10,"task_internal_comms":0.09,"task_managing":0.06,"task_decision_making":0.12,"task_creative":0.00,"task_teaching":0.04,"task_caregiving":0.02},
    "BS Environmental Science":           {"task_data_entry":0.07,"task_documents":0.14,"task_computer_use":0.16,"task_data_analysis":0.18,"task_physical":0.10,"task_other":0.00,"task_client_comms":0.09,"task_internal_comms":0.10,"task_managing":0.03,"task_decision_making":0.11,"task_creative":0.00,"task_teaching":0.02,"task_caregiving":0.00},
    "BS Legal Management":                {"task_data_entry":0.09,"task_documents":0.20,"task_computer_use":0.12,"task_data_analysis":0.13,"task_physical":0.00,"task_other":0.04,"task_client_comms":0.13,"task_internal_comms":0.11,"task_managing":0.03,"task_decision_making":0.12,"task_creative":0.00,"task_teaching":0.01,"task_caregiving":0.00},
    "BS Food Technology":                 {"task_data_entry":0.09,"task_documents":0.14,"task_computer_use":0.12,"task_data_analysis":0.18,"task_physical":0.10,"task_other":0.01,"task_client_comms":0.07,"task_internal_comms":0.11,"task_managing":0.04,"task_decision_making":0.11,"task_creative":0.03,"task_teaching":0.00,"task_caregiving":0.00},
    "BS Computer Engineering":            {"task_data_entry":0.03,"task_documents":0.09,"task_computer_use":0.38,"task_data_analysis":0.15,"task_physical":0.02,"task_other":0.00,"task_client_comms":0.06,"task_internal_comms":0.10,"task_managing":0.02,"task_decision_making":0.12,"task_creative":0.02,"task_teaching":0.01,"task_caregiving":0.00},
    "BS Chemical Engineering":            {"task_data_entry":0.05,"task_documents":0.14,"task_computer_use":0.18,"task_data_analysis":0.20,"task_physical":0.08,"task_other":0.00,"task_client_comms":0.07,"task_internal_comms":0.11,"task_managing":0.04,"task_decision_making":0.13,"task_creative":0.00,"task_teaching":0.00,"task_caregiving":0.00},
    "BS Biology":                         {"task_data_entry":0.07,"task_documents":0.12,"task_computer_use":0.13,"task_data_analysis":0.22,"task_physical":0.14,"task_other":0.00,"task_client_comms":0.07,"task_internal_comms":0.09,"task_managing":0.02,"task_decision_making":0.10,"task_creative":0.01,"task_teaching":0.03,"task_caregiving":0.00},
    "BS Marketing Management":            {"task_data_entry":0.08,"task_documents":0.10,"task_computer_use":0.18,"task_data_analysis":0.16,"task_physical":0.00,"task_other":0.01,"task_client_comms":0.18,"task_internal_comms":0.11,"task_managing":0.03,"task_decision_making":0.10,"task_creative":0.05,"task_teaching":0.00,"task_caregiving":0.00},
}

# Skill risk weights — negative = protective, positive = increases risk
# Using 1-5 proficiency scale: contribution = (proficiency/5) * weight
SKILL_RISK_WEIGHTS = {
    # BS Accountancy
    "skill_fin_accounting":+0.06,"skill_taxation":+0.08,"skill_auditing":-0.07,
    "skill_cost_mgmt_acctg":-0.04,"skill_bookkeeping":+0.11,"skill_business_law":-0.05,
    "skill_pfrs_gaap":-0.03,"skill_data_analytics_acctg":-0.12,
    # BS Business Administration
    "skill_marketing":+0.02,"skill_hrm":-0.05,"skill_operations_mgmt":+0.02,
    "skill_business_comm":-0.07,"skill_financial_mgmt":-0.05,"skill_entrepreneurship":-0.11,
    "skill_strategic_mgmt":-0.10,"skill_biz_research":-0.07,
    # BS IT
    "skill_programming_it":-0.13,"skill_database":-0.08,"skill_networking":-0.06,
    "skill_web_dev":-0.11,"skill_cybersecurity_it":-0.12,"skill_cloud":-0.10,
    "skill_systems_analysis":-0.07,"skill_it_project_mgmt":-0.07,
    # BS CS
    "skill_algorithms":-0.13,"skill_software_eng":-0.10,"skill_ml_ai":-0.15,
    "skill_mobile_dev":-0.09,"skill_os":-0.08,"skill_computer_arch":-0.07,
    "skill_research_cs":-0.08,"skill_fullstack":-0.11,
    # BEEd
    "skill_lesson_plan":-0.06,"skill_classroom_mgmt":-0.05,"skill_curriculum_dev":-0.08,
    "skill_educ_assessment":-0.05,"skill_child_dev":-0.04,"skill_inclusive_educ":-0.08,
    "skill_edtech":-0.06,"skill_comm_engagement":-0.05,
    # BSEd
    "skill_subject_spec":-0.06,"skill_curriculum_sec":-0.07,"skill_adolescent_psych":-0.05,
    "skill_classroom_mgmt_sec":-0.05,"skill_edtech_sec":-0.06,"skill_assessment_eval":-0.05,
    "skill_research_educ":-0.08,"skill_inclusive_educ_sec":-0.07,
    # BS Nursing
    "skill_patient_assess":-0.10,"skill_medication_admin":-0.07,"skill_nursing_care_plan":-0.09,
    "skill_infection_ctrl":-0.05,"skill_emergency_nursing":-0.12,"skill_community_nursing":-0.06,
    "skill_health_educ":-0.05,"skill_nursing_research":-0.06,
    # BS Psychology
    "skill_psych_assessment":-0.09,"skill_counseling":-0.13,"skill_research_psych":-0.08,
    "skill_behavioral_analysis":-0.07,"skill_psychopathology":-0.09,"skill_group_dynamics":-0.06,
    "skill_dev_psychology":-0.05,"skill_io_psychology":-0.08,
    # BS Tourism
    "skill_tourism_planning":-0.06,"skill_tour_operations":+0.03,"skill_cultural_heritage":-0.08,
    "skill_ecotourism":-0.06,"skill_travel_agency":+0.09,"skill_destination_mktg":-0.07,
    "skill_tourism_law":-0.05,"skill_hospitality_ops":-0.04,
    # BS Hospitality
    "skill_fnb_service":-0.02,"skill_rooms_division":+0.04,"skill_events_mgmt":-0.08,
    "skill_front_office":+0.05,"skill_kitchen_ops":-0.04,"skill_customer_service":-0.09,
    "skill_revenue_mgmt":-0.07,"skill_hospitality_mktg":-0.06,
    # BS Civil Engineering
    "skill_structural_analysis":-0.07,"skill_construction_mgmt":-0.07,"skill_hydraulics":-0.05,
    "skill_surveying":+0.04,"skill_geotechnical":-0.08,"skill_transportation_eng":-0.05,
    "skill_project_planning":-0.06,"skill_construction_materials":-0.03,
    # BS EE
    "skill_circuit_analysis":-0.04,"skill_power_systems":-0.08,"skill_electrical_machines":-0.05,
    "skill_control_systems":-0.10,"skill_power_electronics":-0.08,"skill_electrical_design":-0.08,
    "skill_automation_elec":-0.11,"skill_electrical_safety":-0.05,
    # BS ME
    "skill_thermodynamics":-0.05,"skill_fluid_mechanics":-0.05,"skill_machine_design":-0.08,
    "skill_manufacturing":+0.03,"skill_materials_science":-0.06,"skill_mechatronics":-0.11,
    "skill_cad_cam":-0.08,"skill_engineering_mgmt":-0.07,
    # BS ECE
    "skill_digital_electronics":-0.06,"skill_analog_circuits":-0.08,"skill_signal_processing":-0.09,
    "skill_telecommunications":-0.08,"skill_embedded_systems":-0.10,"skill_microelectronics":-0.09,
    "skill_pcb_design":-0.07,"skill_electronics_manuf":+0.02,
    # BS IE
    "skill_operations_research":-0.08,"skill_work_study":+0.04,"skill_quality_mgmt":-0.07,
    "skill_production_planning":+0.02,"skill_ergonomics":-0.06,"skill_supply_chain":-0.07,
    "skill_simulation":-0.09,"skill_lean_manufacturing":-0.08,
    # BS Architecture
    "skill_arch_design":-0.11,"skill_construction_docs":+0.03,"skill_building_systems":-0.06,
    "skill_urban_planning":-0.10,"skill_sustainable_design":-0.09,"skill_digital_modeling":-0.08,
    "skill_project_mgmt_arch":-0.07,"skill_arch_history":-0.03,
    # BS Criminology
    "skill_criminal_law":-0.07,"skill_csi":-0.08,"skill_law_enforcement_admin":+0.02,
    "skill_forensic_science":-0.09,"skill_criminal_behavior":-0.08,"skill_police_admin":+0.02,
    "skill_juvenile_delinquency":-0.06,"skill_police_photography":+0.04,
    # AB Communication
    "skill_media_writing":-0.05,"skill_broadcast_journalism":-0.08,"skill_public_relations":-0.09,
    "skill_advertising":-0.05,"skill_social_media_mgmt":-0.07,"skill_video_production":-0.08,
    "skill_comm_research":-0.07,"skill_digital_media":-0.06,
    # BS Social Work
    "skill_social_casework":-0.11,"skill_community_organizing":-0.10,"skill_group_work":-0.07,
    "skill_social_welfare_policy":-0.06,"skill_child_protection":-0.12,"skill_counseling_sw":-0.11,
    "skill_social_research":-0.07,"skill_mental_health_sw":-0.10,
    # BS Pharmacy
    "skill_pharmacology_pharm":-0.09,"skill_pharma_calculations":+0.07,"skill_dispensing":+0.09,
    "skill_clinical_pharmacy":-0.11,"skill_pharmacy_law":-0.06,"skill_compounding":-0.06,
    "skill_pharmacovigilance":-0.08,"skill_drug_info":-0.07,
    # BS Medical Technology
    "skill_clin_lab":+0.04,"skill_hematology":+0.02,"skill_microbiology_mt":-0.08,
    "skill_clin_chemistry":+0.03,"skill_blood_banking":-0.09,"skill_histopathology":-0.08,
    "skill_lab_quality":-0.07,"skill_lab_safety":-0.05,
    # BS Physical Therapy
    "skill_physical_assessment_pt":-0.09,"skill_therapeutic_exercise":-0.08,"skill_neurological_rehab":-0.12,
    "skill_orthopedic_rehab":-0.09,"skill_electrotherapy":-0.05,"skill_pt_documentation":+0.04,
    "skill_sports_pt":-0.08,"skill_manual_therapy":-0.11,
    # BS Agriculture
    "skill_crop_production":+0.05,"skill_soil_science":-0.06,"skill_animal_science":-0.07,
    "skill_agri_economics":-0.08,"skill_farm_management":-0.07,"skill_plant_pathology":-0.07,
    "skill_agri_technology":-0.10,"skill_food_production":+0.03,
    # BS Environmental Science
    "skill_env_monitoring":-0.05,"skill_ecology":-0.07,"skill_eia":-0.09,
    "skill_pollution_control":-0.07,"skill_gis":-0.10,"skill_climate_adaptation":-0.08,
    "skill_waste_mgmt":+0.02,"skill_env_law":-0.07,
    # BS Legal Management
    "skill_ph_legal_system":-0.05,"skill_contracts":-0.08,"skill_legal_research":-0.09,
    "skill_corporate_law":-0.08,"skill_constitutional_law":-0.06,"skill_labor_law":-0.08,
    "skill_criminal_procedure":-0.07,"skill_legal_ethics":-0.05,
    # BS Food Technology
    "skill_food_processing":+0.05,"skill_food_safety":-0.08,"skill_food_chemistry":-0.07,
    "skill_sensory_eval":-0.09,"skill_product_dev_food":-0.11,"skill_food_microbiology":-0.07,
    "skill_packaging":+0.03,"skill_nutrition_labeling":+0.05,
    # BS Computer Engineering
    "skill_computer_org":-0.07,"skill_embedded_ce":-0.10,"skill_dsp":-0.09,
    "skill_vlsi":-0.11,"skill_computer_networks":-0.08,"skill_real_time_systems":-0.10,
    "skill_firmware":-0.10,"skill_hardware_testing":-0.07,
    # BS Chemical Engineering
    "skill_chem_process":-0.09,"skill_thermodynamics_chem":-0.07,"skill_mass_transfer":-0.07,
    "skill_reaction_eng":-0.08,"skill_process_control":-0.10,"skill_plant_design":-0.09,
    "skill_chem_safety":-0.07,"skill_env_chem_eng":-0.07,
    # BS Biology
    "skill_molecular_bio":-0.09,"skill_ecology_bio":-0.07,"skill_genetics":-0.09,
    "skill_biochemistry":-0.08,"skill_microbiology_bio":-0.08,"skill_cell_biology":-0.08,
    "skill_research_bio":-0.10,"skill_biodiversity":-0.07,
    # BS Marketing Management
    "skill_market_research":-0.07,"skill_digital_mktg":-0.07,"skill_brand_mgmt":-0.10,
    "skill_consumer_behavior_mktg":-0.07,"skill_sales_mgmt":-0.08,"skill_mktg_analytics":-0.11,
    "skill_integrated_mktg_comm":-0.08,"skill_ecommerce":-0.09,

    # Task-based skills (for custom jobs)
    # These are protective (negative weights) - higher proficiency reduces vulnerability
    "skill_data_entry":+0.08,"skill_document_mgmt":+0.05,"skill_digital_literacy":-0.08,
    "skill_data_analysis":-0.10,"skill_analytics":-0.09,"skill_communication":-0.08,
    "skill_client_relations":-0.07,"skill_teamwork":-0.06,"skill_interpersonal":-0.07,
    "skill_critical_thinking":-0.10,"skill_problem_solving":-0.09,"skill_management":-0.08,
    "skill_leadership":-0.12,"skill_creativity":-0.08,"skill_teaching":-0.09,
    "skill_mentoring":-0.10,"skill_physical":+0.05,"skill_caregiving":-0.07,
    "skill_empathy":-0.08,
}

# Base vulnerability ranges per program (calibrated to Philippine labor market)
PROGRAM_BASE_VULNERABILITY = {
    "BS Accountancy":(0.52,0.82),"BS Business Administration":(0.42,0.70),
    "BS Information Technology":(0.28,0.56),"BS Computer Science":(0.18,0.46),
    "Bachelor of Elementary Education":(0.22,0.50),"Bachelor of Secondary Education":(0.20,0.48),
    "BS Nursing":(0.14,0.42),"BS Psychology":(0.18,0.46),
    "BS Tourism Management":(0.44,0.72),"BS Hospitality Management":(0.34,0.62),
    "BS Civil Engineering":(0.24,0.52),"BS Electrical Engineering":(0.22,0.50),
    "BS Mechanical Engineering":(0.22,0.50),"BS Electronics Engineering":(0.20,0.48),
    "BS Industrial Engineering":(0.28,0.55),"BS Architecture":(0.20,0.48),
    "BS Criminology":(0.30,0.58),"AB Communication":(0.28,0.54),
    "BS Social Work":(0.16,0.44),"BS Pharmacy":(0.30,0.58),
    "BS Medical Technology":(0.28,0.55),"BS Physical Therapy":(0.16,0.44),
    "BS Agriculture":(0.32,0.60),"BS Environmental Science":(0.24,0.52),
    "BS Legal Management":(0.24,0.52),"BS Food Technology":(0.30,0.58),
    "BS Computer Engineering":(0.18,0.46),"BS Chemical Engineering":(0.20,0.48),
    "BS Biology":(0.22,0.50),"BS Marketing Management":(0.38,0.65),
}

np.random.seed(42)


def _load_program_skills() -> dict[str, list[str]]:
    """Load skill IDs per program from ched_cmos.json."""
    cmos_path = os.path.join(DATA_DIR, "ched_cmos.json")
    with open(cmos_path) as f:
        cmos = json.load(f)
    return {prog: [s["id"] for s in data["skills"]] for prog, data in cmos.items()}


def generate_poard(n: int = 9000) -> pd.DataFrame:
    program_skills = _load_program_skills()
    all_skills = list(SKILL_RISK_WEIGHTS.keys())
    n_per_program = n // len(PROGRAMS)
    rows = []

    for program in PROGRAMS:
        low, high = PROGRAM_BASE_VULNERABILITY[program]
        prog_skills = program_skills.get(program, [])
        base_weights = PROGRAM_TASK_WEIGHTS[program]

        for _ in range(n_per_program):
            row: dict = {"degree_program": program}

            # Task distribution
            task_vals = {}
            for t in TASK_COLS:
                base = base_weights.get(t, 0.0)
                sigma = max(0.012, base * 0.28)
                task_vals[t] = max(0.0, np.random.normal(base, sigma))
            if np.random.random() < 0.20:
                dominant = np.random.choice(TASK_COLS)
                task_vals[dominant] *= np.random.uniform(1.2, 1.6)
            total = sum(task_vals.values())
            for t in TASK_COLS:
                row[t] = task_vals[t] / max(total, 1e-9)

            # Task-based automation score
            task_score = sum(row[t] * ONET_TASK_SCORES[t] for t in TASK_COLS)

            # Skills — 1-5 proficiency scale (1=none, 5=expert)
            for skill in all_skills:
                if skill in prog_skills:
                    # Profile: skewed toward intermediate-to-proficient (mean ~3.0)
                    proficiency = int(np.clip(round(np.random.normal(3.0, 1.0)), 1, 5))
                    row[skill] = proficiency
                else:
                    # Cross-program skills: mostly 1, occasionally 2
                    row[skill] = 1 if np.random.random() < 0.85 else 2

            # Skill protection effect (normalized proficiency contribution)
            skill_effect = sum(
                (row.get(s, 1) / 5.0) * SKILL_RISK_WEIGHTS.get(s, 0.0)
                for s in prog_skills
            )

            base_risk = np.random.uniform(low, high)
            raw_score = (
                0.55 * task_score
                + 0.28 * base_risk
                + 0.17 * (base_risk + skill_effect)
            )
            individual_noise = np.random.normal(0, 0.022)
            row["vulnerability_score"] = round(float(np.clip(raw_score + individual_noise, 0.01, 0.99)), 4)
            rows.append(row)

    df = pd.DataFrame(rows)
    df.insert(0, "respondent_id", range(1, len(df) + 1))
    return df


def train_and_save():
    print(f"Generating POARD dataset (30 programs × 300 respondents = 9,000 rows)...")
    df = generate_poard(9000)
    poard_path = os.path.join(DATA_DIR, "poard.csv")
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(poard_path, index=False)
    print(f"Saved POARD to {poard_path}")

    all_skills = list(SKILL_RISK_WEIGHTS.keys())
    feature_cols = ["degree_program"] + TASK_COLS + all_skills
    X = df[feature_cols]
    y = df["vulnerability_score"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=df["degree_program"]
    )

    preprocessor = ColumnTransformer(
        transformers=[("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), ["degree_program"])],
        remainder="passthrough",
    )

    model = RandomForestRegressor(
        n_estimators=300, max_depth=None, min_samples_split=4,
        min_samples_leaf=2, max_features="sqrt", random_state=42, n_jobs=-1,
    )

    pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])
    print("Training Random Forest Regressor (300 trees, 30 programs, 240 skills)...")
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    mae = float(mean_absolute_error(y_test, y_pred))
    r2 = float(r2_score(y_test, y_pred))
    print(f"Model Evaluation — RMSE: {rmse:.4f} | MAE: {mae:.4f} | R²: {r2:.4f}")

    joblib.dump(pipeline, os.path.join(MODEL_DIR, "aral_model.pkl"))

    program_skills = _load_program_skills()
    meta = {
        "feature_cols": feature_cols,
        "task_cols": TASK_COLS,
        "skill_cols": all_skills,
        "programs": PROGRAMS,
        "program_skills": program_skills,
        "score_ranges": {k: list(v) for k, v in PROGRAM_BASE_VULNERABILITY.items()},
        "onet_task_scores": ONET_TASK_SCORES,
        "skill_risk_weights": SKILL_RISK_WEIGHTS,
        "evaluation": {"rmse": rmse, "mae": mae, "r2": r2},
    }
    with open(os.path.join(MODEL_DIR, "model_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    print("Done.")
    return pipeline, meta


if __name__ == "__main__":
    train_and_save()
