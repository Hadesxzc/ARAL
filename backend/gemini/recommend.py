"""
ARAL Course Recommendations — comprehensive free + paid catalog for all 60 CMO skills.
Uses Gemini 2.5 Flash when GEMINI_API_KEY is available, otherwise falls back to curated catalog.
"""
import os
import json
import re

# -------------------------------------------------------------------
# Comprehensive course catalog — both FREE and PAID for all 60 skills
# -------------------------------------------------------------------
COURSE_CATALOG: dict[str, list[dict]] = {
    # ── BS ACCOUNTANCY ──────────────────────────────────────────────
    "skill_financial_statements": [
        {"course_title": "Intermediate Financial Accounting", "platform": "Coursera", "url": "https://www.coursera.org/learn/financial-accounting", "is_free": True, "reason": "Deepens PFRS-aligned financial statement preparation skills."},
        {"course_title": "Financial Accounting Fundamentals", "platform": "Udemy", "url": "https://www.udemy.com/course/financial-accounting/", "is_free": False, "reason": "Practical financial reporting for accounting graduates."},
    ],
    "skill_tax_computation": [
        {"course_title": "Taxation of Business Entities", "platform": "Coursera", "url": "https://www.coursera.org/learn/taxing-business", "is_free": True, "reason": "Reduces over-reliance on routine tax computation — focus on strategy."},
        {"course_title": "Philippine Taxation Masterclass", "platform": "Udemy", "url": "https://www.udemy.com/course/philippine-taxation/", "is_free": False, "reason": "PH-specific tax law and BIR procedures for accountants."},
    ],
    "skill_auditing": [
        {"course_title": "Auditing I: Conceptual Foundations", "platform": "Coursera", "url": "https://www.coursera.org/learn/auditing", "is_free": True, "reason": "Strengthens audit judgment — a high-complexity skill resistant to automation."},
        {"course_title": "Internal Audit Fundamentals", "platform": "edX", "url": "https://www.edx.org/learn/auditing", "is_free": True, "reason": "Internal audit skills require professional judgment that AI cannot fully replicate."},
    ],
    "skill_cost_accounting": [
        {"course_title": "Cost Accounting — Decision Tools", "platform": "edX", "url": "https://www.edx.org/learn/cost-accounting", "is_free": True, "reason": "Cost analysis skills reduce dependence on automatable routine entries."},
        {"course_title": "Managerial Accounting Bootcamp", "platform": "Udemy", "url": "https://www.udemy.com/course/managerial-accounting-complete-bootcamp/", "is_free": False, "reason": "Deep dive into cost-volume-profit and variance analysis."},
    ],
    "skill_bookkeeping": [
        {"course_title": "Bookkeeping for Small Business", "platform": "Coursera", "url": "https://www.coursera.org/learn/bookkeeping-basics", "is_free": True, "reason": "While basic bookkeeping is automatable, understanding the logic builds higher-order skills."},
        {"course_title": "Xero Accounting Software Training", "platform": "Udemy", "url": "https://www.udemy.com/course/xero-training/", "is_free": False, "reason": "Proficiency in cloud accounting software (QuickBooks/Xero) is essential."},
    ],
    "skill_business_law": [
        {"course_title": "Foundations of Business Law", "platform": "Coursera", "url": "https://www.coursera.org/learn/business-law", "is_free": True, "reason": "Legal judgment and interpretation resist automation — a key protective skill."},
        {"course_title": "Contract Law for Non-Lawyers", "platform": "edX", "url": "https://www.edx.org/learn/contracts", "is_free": True, "reason": "Understanding contracts is highly protective in accounting-adjacent roles."},
    ],
    "skill_management_accounting": [
        {"course_title": "Strategic Management Accounting", "platform": "Coursera", "url": "https://www.coursera.org/learn/managerial-accounting-fundamentals", "is_free": True, "reason": "Strategic costing decisions require human judgment and contextual insight."},
        {"course_title": "CMA Prep: Management Accounting", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/", "is_free": False, "reason": "Certified Management Accountant preparation — a high-value credential."},
    ],
    "skill_pfrs": [
        {"course_title": "IFRS Diploma — Corporate Reporting", "platform": "edX", "url": "https://www.edx.org/learn/ifrs", "is_free": True, "reason": "PFRS/IFRS expertise is a high-judgment skill that provides career protection."},
        {"course_title": "IFRS Masterclass", "platform": "Udemy", "url": "https://www.udemy.com/course/ifrs/", "is_free": False, "reason": "Comprehensive international financial reporting standards training."},
    ],
    "skill_computerized_accounting": [
        {"course_title": "QuickBooks Online — Complete Training", "platform": "Udemy", "url": "https://www.udemy.com/course/quickbooks-online/", "is_free": False, "reason": "Proficiency in accounting software is essential for modern accountants."},
        {"course_title": "Cloud Accounting with Xero", "platform": "Coursera", "url": "https://www.coursera.org/learn/accounting-technology", "is_free": True, "reason": "Cloud accounting skills complement traditional training and reduce manual-only risk."},
    ],
    "skill_data_interpretation": [
        {"course_title": "Data Analysis with Python", "platform": "Coursera", "url": "https://www.coursera.org/learn/data-analysis-python", "is_free": True, "reason": "Data analytics capability is the top protective skill for accounting careers."},
        {"course_title": "Excel for Accountants — Advanced", "platform": "Udemy", "url": "https://www.udemy.com/course/excel-for-accountants/", "is_free": False, "reason": "Advanced Excel analytics gives accountants a significant automation edge."},
    ],

    # ── BS BUSINESS ADMINISTRATION ────────────────────────────────
    "skill_marketing_principles": [
        {"course_title": "Marketing Analytics", "platform": "Coursera", "url": "https://www.coursera.org/learn/marketing-analytics", "is_free": True, "reason": "Marketing analytics combines human strategy with data — highly protective."},
        {"course_title": "Digital Marketing Masterclass", "platform": "Udemy", "url": "https://www.udemy.com/course/digital-marketing-masterclass/", "is_free": False, "reason": "Digital marketing skills are in high demand and resist automation."},
    ],
    "skill_human_resource_mgmt": [
        {"course_title": "Human Resource Management", "platform": "Coursera", "url": "https://www.coursera.org/learn/human-resource-management", "is_free": True, "reason": "People management requires emotional intelligence — a key automation barrier."},
        {"course_title": "SHRM HR Certification Prep", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/", "is_free": False, "reason": "HR certification significantly increases career resilience and mobility."},
    ],
    "skill_operations_management": [
        {"course_title": "Operations Management", "platform": "Coursera", "url": "https://www.coursera.org/learn/operations-management", "is_free": True, "reason": "Supply chain optimization thinking protects against routine task automation."},
        {"course_title": "Six Sigma Green Belt", "platform": "Udemy", "url": "https://www.udemy.com/course/six-sigma-green-belt/", "is_free": False, "reason": "Lean Six Sigma certifications are highly valued in operations roles."},
    ],
    "skill_business_communication": [
        {"course_title": "Business English Communication Skills", "platform": "Coursera", "url": "https://www.coursera.org/specializations/business-english", "is_free": True, "reason": "Advanced communication is a top protective skill against automation."},
        {"course_title": "Business Communication Mastery", "platform": "Udemy", "url": "https://www.udemy.com/course/business-communication/", "is_free": False, "reason": "Written and verbal communication skills are irreplaceable in professional settings."},
    ],
    "skill_financial_management": [
        {"course_title": "Introduction to Corporate Finance", "platform": "Coursera", "url": "https://www.coursera.org/learn/corporate-finance", "is_free": True, "reason": "Financial decision-making requires contextual judgment that AI cannot replicate."},
        {"course_title": "CFA Level 1 Prep", "platform": "Udemy", "url": "https://www.udemy.com/course/cfa-level-1/", "is_free": False, "reason": "CFA certification is the gold standard for financial management careers."},
    ],
    "skill_entrepreneurship": [
        {"course_title": "Entrepreneurship: Launching an Innovative Business", "platform": "Coursera", "url": "https://www.coursera.org/learn/startup", "is_free": True, "reason": "Entrepreneurial thinking is fundamentally human and automation-resistant."},
        {"course_title": "Startup School", "platform": "Y Combinator", "url": "https://www.startupschool.org/", "is_free": True, "reason": "Free YC program teaches startup fundamentals — highly practical."},
    ],
    "skill_business_ethics": [
        {"course_title": "Business Ethics for the Real World", "platform": "Coursera", "url": "https://www.coursera.org/learn/business-ethics", "is_free": True, "reason": "Ethical reasoning is a uniquely human capability that protects professional careers."},
        {"course_title": "Corporate Governance and Ethics", "platform": "edX", "url": "https://www.edx.org/learn/corporate-governance", "is_free": True, "reason": "Governance expertise adds a layer of career protection through specialization."},
    ],
    "skill_strategic_management": [
        {"course_title": "Strategic Management and Innovation", "platform": "Coursera", "url": "https://www.coursera.org/learn/strategic-management", "is_free": True, "reason": "Strategy formulation requires systemic human thinking AI cannot replicate."},
        {"course_title": "MBA Strategy: Complete Business Strategy", "platform": "Udemy", "url": "https://www.udemy.com/course/mba-strategy/", "is_free": False, "reason": "Comprehensive strategic management toolkit for business graduates."},
    ],
    "skill_consumer_behavior": [
        {"course_title": "Consumer Neuroscience and Neuromarketing", "platform": "Coursera", "url": "https://www.coursera.org/learn/neuromarketing", "is_free": True, "reason": "Deep consumer insight goes beyond data — it requires human empathy."},
        {"course_title": "Consumer Psychology and Behavior", "platform": "Udemy", "url": "https://www.udemy.com/course/consumer-psychology/", "is_free": False, "reason": "Understanding human purchasing decisions is a high-value soft skill."},
    ],
    "skill_business_research": [
        {"course_title": "Research Methods for Business", "platform": "Coursera", "url": "https://www.coursera.org/learn/research-methods", "is_free": True, "reason": "Research design and analysis skills signal high intellectual capability."},
        {"course_title": "Business Analysis Fundamentals", "platform": "Udemy", "url": "https://www.udemy.com/course/business-analysis-fundamentals/", "is_free": False, "reason": "Business analysis is a high-demand career path resistant to automation."},
    ],

    # ── BS INFORMATION TECHNOLOGY ─────────────────────────────────
    "skill_programming": [
        {"course_title": "Python for Everybody Specialization", "platform": "Coursera", "url": "https://www.coursera.org/specializations/python", "is_free": True, "reason": "Programming is the single strongest protection against career automation."},
        {"course_title": "The Complete Python Developer", "platform": "Udemy", "url": "https://www.udemy.com/course/complete-python-developer-zero-to-mastery/", "is_free": False, "reason": "Full-stack Python skills make you a builder, not just a user, of automation."},
    ],
    "skill_database_management": [
        {"course_title": "Databases and SQL for Data Science", "platform": "Coursera", "url": "https://www.coursera.org/learn/sql-data-science", "is_free": True, "reason": "SQL and database design skills remain in high demand across all industries."},
        {"course_title": "The Complete SQL Bootcamp", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-sql-bootcamp/", "is_free": False, "reason": "Advanced SQL and database management is an essential technical skill."},
    ],
    "skill_network_administration": [
        {"course_title": "Google IT Support Professional Certificate", "platform": "Coursera", "url": "https://www.coursera.org/professional-certificates/google-it-support", "is_free": True, "reason": "Network administration and IT support remain in demand in the Philippine market."},
        {"course_title": "CompTIA Network+ Certification Prep", "platform": "Udemy", "url": "https://www.udemy.com/course/comptia-network-cert/", "is_free": False, "reason": "Network+ certification is a valuable credential for IT careers."},
    ],
    "skill_web_development": [
        {"course_title": "Full-Stack Web Development", "platform": "The Odin Project", "url": "https://www.theodinproject.com/", "is_free": True, "reason": "Full-stack development is one of the most automation-resistant IT careers."},
        {"course_title": "The Complete Web Developer Bootcamp", "platform": "Udemy", "url": "https://www.udemy.com/course/the-web-developer-bootcamp/", "is_free": False, "reason": "Comprehensive web development training covering HTML, CSS, JS, Node, and more."},
    ],
    "skill_systems_analysis": [
        {"course_title": "Software Product Management", "platform": "Coursera", "url": "https://www.coursera.org/specializations/product-management", "is_free": True, "reason": "Systems thinking and requirements analysis are highly protective skills."},
        {"course_title": "Systems Analysis and Design", "platform": "Udemy", "url": "https://www.udemy.com/course/systems-analysis/", "is_free": False, "reason": "Business systems analysis is a growing career path in the Philippines."},
    ],
    "skill_cybersecurity": [
        {"course_title": "Google Cybersecurity Certificate", "platform": "Coursera", "url": "https://www.coursera.org/professional-certificates/google-cybersecurity", "is_free": True, "reason": "Cybersecurity is one of the fastest-growing and most automation-resistant IT fields."},
        {"course_title": "CompTIA Security+ Exam Prep", "platform": "Udemy", "url": "https://www.udemy.com/course/securityplus/", "is_free": False, "reason": "Security+ is a foundational cybersecurity certification recognized globally."},
    ],
    "skill_technical_documentation": [
        {"course_title": "Technical Writing Essentials", "platform": "Coursera", "url": "https://www.coursera.org/learn/technical-writing", "is_free": True, "reason": "Clear technical writing is a soft skill that complements technical expertise."},
        {"course_title": "Technical Writing: Master Your Writing Career", "platform": "Udemy", "url": "https://www.udemy.com/course/technical-writing/", "is_free": False, "reason": "Technical documentation skills open doors in software and engineering industries."},
    ],
    "skill_software_testing": [
        {"course_title": "Software Testing and Automation", "platform": "Coursera", "url": "https://www.coursera.org/learn/software-testing-automation", "is_free": True, "reason": "QA engineering is a growing IT career that supports automation pipelines."},
        {"course_title": "ISTQB Foundation Level Prep", "platform": "Udemy", "url": "https://www.udemy.com/course/istqb-software-testing/", "is_free": False, "reason": "ISTQB certification is internationally recognized in software quality assurance."},
    ],
    "skill_cloud_computing": [
        {"course_title": "Google Cloud Fundamentals: Core Infrastructure", "platform": "Coursera", "url": "https://www.coursera.org/learn/gcp-fundamentals", "is_free": True, "reason": "Cloud computing is the backbone of modern IT — highly protective skill."},
        {"course_title": "AWS Certified Solutions Architect", "platform": "Udemy", "url": "https://www.udemy.com/course/aws-certified-solutions-architect-associate/", "is_free": False, "reason": "AWS certification is one of the highest-value credentials in IT today."},
    ],
    "skill_it_project_management": [
        {"course_title": "Google Project Management Certificate", "platform": "Coursera", "url": "https://www.coursera.org/professional-certificates/google-project-management", "is_free": True, "reason": "Project management combines technical and soft skills — hard to automate."},
        {"course_title": "PMP Certification Exam Prep", "platform": "Udemy", "url": "https://www.udemy.com/course/pmp-pmbok6-exam/", "is_free": False, "reason": "PMP is the gold standard for IT project management certification."},
    ],

    # ── BS COMPUTER SCIENCE ──────────────────────────────────────
    "skill_algorithms_ds": [
        {"course_title": "Algorithms Specialization", "platform": "Coursera", "url": "https://www.coursera.org/specializations/algorithms", "is_free": True, "reason": "Algorithm design is a foundational skill that makes you a creator, not just a user of AI."},
        {"course_title": "Master the Coding Interview: DSA", "platform": "Udemy", "url": "https://www.udemy.com/course/master-the-coding-interview-data-structures-algorithms/", "is_free": False, "reason": "DSA mastery is essential for software engineering interviews and career growth."},
    ],
    "skill_software_engineering": [
        {"course_title": "Software Engineering: Introduction", "platform": "edX", "url": "https://www.edx.org/learn/software-engineering", "is_free": True, "reason": "Software engineering practices make you effective at building complex systems."},
        {"course_title": "Clean Code and Software Architecture", "platform": "Udemy", "url": "https://www.udemy.com/course/writing-clean-code/", "is_free": False, "reason": "Clean code practices are essential for professional software development."},
    ],
    "skill_operating_systems": [
        {"course_title": "Operating Systems and Virtualization Security", "platform": "Coursera", "url": "https://www.coursera.org/learn/os-virtualization-security", "is_free": True, "reason": "OS knowledge is foundational for systems programming and cloud infrastructure work."},
        {"course_title": "Linux Command Line and Shell Scripting", "platform": "Udemy", "url": "https://www.udemy.com/course/linux-command-line/", "is_free": False, "reason": "Linux proficiency is essential for server-side and DevOps careers."},
    ],
    "skill_computer_architecture": [
        {"course_title": "Computer Architecture", "platform": "Coursera", "url": "https://www.coursera.org/learn/comparch", "is_free": True, "reason": "Deep hardware knowledge differentiates CS graduates in systems and embedded roles."},
        {"course_title": "From NAND to Tetris", "platform": "Coursera", "url": "https://www.coursera.org/learn/build-a-computer", "is_free": True, "reason": "Build a computer from first principles — the most rigorous CS foundation course."},
    ],
    "skill_machine_learning_basics": [
        {"course_title": "Machine Learning Specialization", "platform": "Coursera", "url": "https://www.coursera.org/specializations/machine-learning-introduction", "is_free": True, "reason": "ML knowledge positions you to build and manage automation — not be replaced by it."},
        {"course_title": "Deep Learning A-Z", "platform": "Udemy", "url": "https://www.udemy.com/course/deeplearning/", "is_free": False, "reason": "Practical neural network implementation skills for AI/ML careers."},
    ],
    "skill_theory_of_computation": [
        {"course_title": "Automata Theory", "platform": "Coursera", "url": "https://www.coursera.org/learn/automata", "is_free": True, "reason": "Theory of computation builds formal reasoning skills valued in research and advanced development."},
        {"course_title": "Discrete Mathematics", "platform": "edX", "url": "https://www.edx.org/learn/discrete-mathematics", "is_free": True, "reason": "Mathematical foundations underpin algorithms and software engineering careers."},
    ],
    "skill_mobile_development": [
        {"course_title": "Android App Development with Kotlin", "platform": "Coursera", "url": "https://www.coursera.org/learn/android-development", "is_free": True, "reason": "Mobile development is a high-demand skill in the Philippine tech market."},
        {"course_title": "Flutter & Dart — The Complete Guide", "platform": "Udemy", "url": "https://www.udemy.com/course/flutter-dart-the-complete-guide/", "is_free": False, "reason": "Flutter enables cross-platform mobile development for both Android and iOS."},
    ],
    "skill_parallel_computing": [
        {"course_title": "High Performance Computing", "platform": "edX", "url": "https://www.edx.org/learn/high-performance-computing", "is_free": True, "reason": "Parallel computing expertise is valued in data science and ML engineering roles."},
        {"course_title": "CUDA Programming for GPU Computing", "platform": "Udemy", "url": "https://www.udemy.com/course/cuda-programming/", "is_free": False, "reason": "GPU programming skills are in high demand for AI infrastructure roles."},
    ],
    "skill_research_methods_cs": [
        {"course_title": "Research Methods", "platform": "Coursera", "url": "https://www.coursera.org/learn/research-methods", "is_free": True, "reason": "CS research skills open doors to graduate school and R&D roles."},
        {"course_title": "Academic Writing Made Easy", "platform": "edX", "url": "https://www.edx.org/learn/academic-writing", "is_free": True, "reason": "Strong research writing skills are essential for graduate studies and research careers."},
    ],
    "skill_capstone_systems": [
        {"course_title": "Full-Stack Development Capstone", "platform": "IBM via Coursera", "url": "https://www.coursera.org/learn/ibm-full-stack-cloud-developer", "is_free": True, "reason": "End-to-end system building demonstrates the integration of all CS skills."},
        {"course_title": "System Design Interview Prep", "platform": "Udemy", "url": "https://www.udemy.com/course/system-design-interview-prep/", "is_free": False, "reason": "System design skills are essential for senior software engineering careers."},
    ],

    # ── BACHELOR OF ELEMENTARY EDUCATION ─────────────────────────
    "skill_lesson_planning": [
        {"course_title": "Learning to Teach Online", "platform": "Coursera", "url": "https://www.coursera.org/learn/teach-online", "is_free": True, "reason": "Blended and online lesson design expands teaching impact beyond physical classrooms."},
        {"course_title": "Lesson Plan Design for Educators", "platform": "Udemy", "url": "https://www.udemy.com/course/lesson-plan-design/", "is_free": False, "reason": "Evidence-based lesson design techniques for modern classrooms."},
    ],
    "skill_classroom_management": [
        {"course_title": "Positive Behavior Support", "platform": "Coursera", "url": "https://www.coursera.org/learn/positive-behavior-support", "is_free": True, "reason": "Advanced behavior management skills protect teaching careers from routine task automation."},
        {"course_title": "The Science of Well-Being for Educators", "platform": "Coursera", "url": "https://www.coursera.org/learn/science-of-well-being", "is_free": True, "reason": "Teacher resilience and student well-being expertise makes educators irreplaceable."},
    ],
    "skill_curriculum_development": [
        {"course_title": "Curriculum Design and Assessment", "platform": "edX", "url": "https://www.edx.org/learn/curriculum-development", "is_free": True, "reason": "Curriculum design expertise positions educators as leaders, not just implementers."},
        {"course_title": "Instructional Design Masterclass", "platform": "Udemy", "url": "https://www.udemy.com/course/instructional-design/", "is_free": False, "reason": "Instructional design opens career pathways in corporate training and e-learning."},
    ],
    "skill_educational_assessment": [
        {"course_title": "Assessment in Higher Education", "platform": "Coursera", "url": "https://www.coursera.org/learn/assessment-higher-education", "is_free": True, "reason": "Assessment design and data-driven teaching reduces automation exposure."},
        {"course_title": "Learning Analytics", "platform": "edX", "url": "https://www.edx.org/learn/learning-analytics", "is_free": True, "reason": "Using data to improve learning outcomes is a high-value 21st century teaching skill."},
    ],
    "skill_child_development": [
        {"course_title": "Child Nutrition and Cooking", "platform": "Coursera", "url": "https://www.coursera.org/learn/childnutrition", "is_free": True, "reason": "Holistic child development expertise makes educators indispensable."},
        {"course_title": "Child Psychology", "platform": "Udemy", "url": "https://www.udemy.com/course/child-psychology/", "is_free": False, "reason": "Child psychology expertise deepens teacher effectiveness in early education."},
    ],
    "skill_inclusive_education": [
        {"course_title": "Inclusive Education: Learning from Each Other", "platform": "Coursera", "url": "https://www.coursera.org/learn/inclusive-education", "is_free": True, "reason": "Inclusive education is a specialized skill that AI and automation cannot replicate."},
        {"course_title": "Special Education Fundamentals", "platform": "edX", "url": "https://www.edx.org/learn/special-education", "is_free": True, "reason": "SpEd expertise is highly valued and deeply human-centered."},
    ],
    "skill_teaching_strategies": [
        {"course_title": "Powerful Tools for Teaching and Learning", "platform": "Coursera", "url": "https://www.coursera.org/learn/powerful-tools-for-teaching-learning", "is_free": True, "reason": "Innovative teaching methods make educators more effective and less replaceable."},
        {"course_title": "Project-Based Learning", "platform": "edX", "url": "https://www.edx.org/learn/project-based-learning", "is_free": True, "reason": "PBL facilitation requires human creativity and mentorship skills."},
    ],
    "skill_educational_technology": [
        {"course_title": "Technology for Teachers and Students", "platform": "Coursera", "url": "https://www.coursera.org/learn/technology-teachers-students", "is_free": True, "reason": "EdTech proficiency makes teachers more effective and positions them as innovators."},
        {"course_title": "Google Workspace for Education", "platform": "Google Digital Garage", "url": "https://learndigital.withgoogle.com/digitalgarage/courses", "is_free": True, "reason": "Google tools are widely used in Philippine public and private schools."},
    ],
    "skill_professional_ethics_ed": [
        {"course_title": "Ethics in Education", "platform": "Coursera", "url": "https://www.coursera.org/learn/ethics-education", "is_free": True, "reason": "Ethical leadership in education is a uniquely human capability."},
        {"course_title": "DepEd-aligned Professional Development", "platform": "DepEd Commons", "url": "https://commons.deped.gov.ph/", "is_free": True, "reason": "DepEd Commons provides Philippine-specific teacher professional development resources."},
    ],
    "skill_community_engagement": [
        {"course_title": "Community Engagement in Public Health", "platform": "Coursera", "url": "https://www.coursera.org/learn/community-engagement-public-health", "is_free": True, "reason": "Community engagement requires local knowledge and human relationship skills."},
        {"course_title": "Social Enterprise and Community Development", "platform": "edX", "url": "https://www.edx.org/learn/community-development", "is_free": True, "reason": "Community development expertise strengthens the social impact of educators."},
    ],

    # ── BS NURSING ────────────────────────────────────────────────
    "skill_patient_assessment": [
        {"course_title": "Patient Safety and Quality Improvement", "platform": "Coursera", "url": "https://www.coursera.org/learn/patient-safety", "is_free": True, "reason": "Advanced patient assessment integrates clinical judgment that AI cannot fully replicate."},
        {"course_title": "Advanced Physical Assessment", "platform": "Udemy", "url": "https://www.udemy.com/course/physical-assessment-nursing/", "is_free": False, "reason": "Advanced clinical assessment skills differentiate nurses in specialized care settings."},
    ],
    "skill_medication_administration": [
        {"course_title": "Pharmacology for Nurses", "platform": "Coursera", "url": "https://www.coursera.org/learn/pharmacology", "is_free": True, "reason": "Advanced pharmacology knowledge reduces routine medication error risk and adds clinical value."},
        {"course_title": "Clinical Pharmacology Masterclass", "platform": "Udemy", "url": "https://www.udemy.com/course/clinical-pharmacology/", "is_free": False, "reason": "Deep drug knowledge positions nurses for advanced practice roles."},
    ],
    "skill_health_education": [
        {"course_title": "Health Communication", "platform": "Coursera", "url": "https://www.coursera.org/learn/health-communication", "is_free": True, "reason": "Patient education and health promotion are uniquely human, empathy-driven skills."},
        {"course_title": "Public Health Fundamentals", "platform": "edX", "url": "https://www.edx.org/learn/public-health", "is_free": True, "reason": "Public health skills broaden nursing career pathways significantly."},
    ],
    "skill_nursing_care_planning": [
        {"course_title": "Evidence-Based Nursing Practice", "platform": "Coursera", "url": "https://www.coursera.org/learn/evidence-based-nursing", "is_free": True, "reason": "Evidence-based care planning integrates research, judgment, and patient context."},
        {"course_title": "NANDA Nursing Diagnoses", "platform": "Udemy", "url": "https://www.udemy.com/course/nursing-diagnoses/", "is_free": False, "reason": "Mastery of nursing diagnoses is fundamental to professional nursing practice."},
    ],
    "skill_infection_control": [
        {"course_title": "Infection Prevention and Control", "platform": "Coursera", "url": "https://www.coursera.org/learn/infection-prevention", "is_free": True, "reason": "IPC expertise became a premium skill post-pandemic — high protective value."},
        {"course_title": "WHO IPC Certificate", "platform": "WHO OpenWHO", "url": "https://openwho.org/courses", "is_free": True, "reason": "WHO-certified IPC training is globally recognized and opens international opportunities."},
    ],
    "skill_emergency_care": [
        {"course_title": "First Aid and Emergency Response", "platform": "FutureLearn", "url": "https://www.futurelearn.com/courses/first-aid", "is_free": True, "reason": "Emergency care requires split-second human judgment — highly resistant to automation."},
        {"course_title": "ACLS Certification Prep", "platform": "Udemy", "url": "https://www.udemy.com/course/acls-certification/", "is_free": False, "reason": "ACLS certification is highly valuable for nurses seeking ICU or ER careers."},
    ],
    "skill_maternal_child_nursing": [
        {"course_title": "Reproductive Health and Family Planning", "platform": "Coursera", "url": "https://www.coursera.org/learn/reproductive-health", "is_free": True, "reason": "Maternal-child nursing is a high-empathy, high-complexity specialty resistant to automation."},
        {"course_title": "Neonatal Nursing Essentials", "platform": "Udemy", "url": "https://www.udemy.com/course/neonatal-nursing/", "is_free": False, "reason": "Neonatal ICU (NICU) specialization is a premium nursing career pathway."},
    ],
    "skill_community_health_nursing": [
        {"course_title": "Community Health Nursing", "platform": "TESDA Online Program", "url": "https://top.tesda.gov.ph/", "is_free": True, "reason": "TESDA-aligned community health training is directly applicable in the Philippine setting."},
        {"course_title": "Public Health and Global Health", "platform": "Coursera", "url": "https://www.coursera.org/learn/public-health", "is_free": True, "reason": "Combining nursing with public health creates career opportunities in NGOs and government."},
    ],
    "skill_mental_health_nursing": [
        {"course_title": "Mental Health and Psychiatry", "platform": "Coursera", "url": "https://www.coursera.org/learn/mental-health-psychiatry", "is_free": True, "reason": "Mental health nursing requires deep human empathy — AI cannot replicate this specialty."},
        {"course_title": "Psychiatric-Mental Health Nursing", "platform": "Udemy", "url": "https://www.udemy.com/course/psychiatric-mental-health-nursing/", "is_free": False, "reason": "MH nursing specialization opens doors to psychiatric and behavioral health careers."},
    ],
    "skill_nursing_research": [
        {"course_title": "Nursing Research and Evidence-Based Practice", "platform": "Coursera", "url": "https://www.coursera.org/learn/nursing-research", "is_free": True, "reason": "Research skills position nurses as academic and clinical contributors, not just practitioners."},
        {"course_title": "Statistics for Nurses", "platform": "edX", "url": "https://www.edx.org/learn/statistics", "is_free": True, "reason": "Statistical competency enables nurses to critically evaluate clinical research."},
    ],

    # ── GENERAL FALLBACK ──────────────────────────────────────────
    "default": [
        {"course_title": "Fundamentals of Digital Marketing", "platform": "Google Digital Garage", "url": "https://learndigital.withgoogle.com/digitalgarage/course/digital-marketing", "is_free": True, "reason": "Digital literacy broadly reduces automation vulnerability across all career paths."},
        {"course_title": "LinkedIn Learning — Career Development", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/", "is_free": False, "reason": "LinkedIn Learning offers thousands of courses across all career domains."},
    ],
}


def generate_recommendations(skill_gaps: list, degree_program: str, job_title: str) -> list[dict]:
    """
    Generate free + paid course recommendations for identified skill gaps.
    Uses Gemini 2.5 Flash when GEMINI_API_KEY is available, otherwise uses curated catalog.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if api_key:
        try:
            return _gemini_recommendations(skill_gaps, degree_program, job_title, api_key)
        except Exception as e:
            print(f"Gemini API error, using fallback: {e}")

    return _fallback_recommendations(skill_gaps, degree_program, job_title)


def _gemini_recommendations(skill_gaps: list, degree_program: str, job_title: str, api_key: str) -> list[dict]:
    import google.generativeai as genai
    genai.configure(api_key=api_key)

    gap_text = "\n".join([
        f"- {g['skill_label']} (impact: {g['impact_score']:.2f}, gap type: {g['gap_type']})"
        for g in skill_gaps[:5]
    ])

    prompt = f"""You are a career advisor for Filipino graduates.

A {degree_program} graduate working as {job_title} has these automation-risk skill gaps:
{gap_text}

For each skill gap, recommend 2 courses: one FREE and one PAID.

FREE options (choose from): Coursera (free audit), edX (free audit), Google Digital Garage, 
FutureLearn (free), TESDA Online Program (TOP), DepEd Commons, OpenWHO, The Odin Project, freeCodeCamp.

PAID options (choose from): Udemy, LinkedIn Learning, Pluralsight, Skillshare, DataCamp.

For each course provide:
- skill: (exact skill name from gap)
- course_title: (specific course name)
- platform: (one of the platforms above)
- url: (valid URL)
- is_free: true or false
- reason: (one sentence explaining how this addresses their automation risk)

Return ONLY a valid JSON array. No markdown. No code blocks. No explanation.
Format: [{{"skill":"...","course_title":"...","platform":"...","url":"...","is_free":true,"reason":"..."}}]"""

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    text = response.text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    courses = json.loads(text)
    return courses[:len(skill_gaps) * 2]


def _fallback_recommendations(skill_gaps: list, degree_program: str, job_title: str) -> list[dict]:
    recommendations = []
    for gap in skill_gaps[:6]:
        skill_id = gap.get("skill_id", "")
        courses = COURSE_CATALOG.get(skill_id, COURSE_CATALOG["default"])
        for course in courses:
            rec = course.copy()
            rec["skill"] = gap.get("skill_label", skill_id)
            recommendations.append(rec)
    return recommendations
