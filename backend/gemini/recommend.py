"""
ARAL Gemini AI integration — generates free course recommendations.
Falls back to predefined courses when GEMINI_API_KEY is unavailable.
"""
import os
import json
import re
from typing import Optional

FALLBACK_COURSES = {
    "skill_data_interpretation": {
        "course_title": "Data Analysis with Python",
        "platform": "Coursera",
        "url": "https://www.coursera.org/learn/data-analysis-python",
        "is_free": True,
        "reason": "Strengthens data analysis skills that protect against automation in accounting and business roles.",
    },
    "skill_computerized_accounting": {
        "course_title": "Accounting Fundamentals with QuickBooks",
        "platform": "edX",
        "url": "https://www.edx.org/learn/accounting",
        "is_free": True,
        "reason": "Computerized accounting proficiency significantly reduces automation vulnerability for BSA graduates.",
    },
    "skill_financial_management": {
        "course_title": "Introduction to Corporate Finance",
        "platform": "Coursera",
        "url": "https://www.coursera.org/learn/corporate-finance",
        "is_free": True,
        "reason": "Financial management skills provide human judgment that is hard to automate.",
    },
    "skill_entrepreneurship": {
        "course_title": "Entrepreneurship: Launching an Innovative Business",
        "platform": "Coursera",
        "url": "https://www.coursera.org/learn/startup",
        "is_free": True,
        "reason": "Entrepreneurial thinking is a key protective skill against automation.",
    },
    "skill_strategic_management": {
        "course_title": "Strategic Management and Innovation",
        "platform": "Coursera",
        "url": "https://www.coursera.org/learn/strategic-management",
        "is_free": True,
        "reason": "Strategic thinking requires human judgment that AI cannot replicate.",
    },
    "skill_programming": {
        "course_title": "Python for Everybody",
        "platform": "Coursera",
        "url": "https://www.coursera.org/specializations/python",
        "is_free": True,
        "reason": "Programming skills dramatically reduce automation vulnerability.",
    },
    "skill_cybersecurity": {
        "course_title": "Google Cybersecurity Certificate",
        "platform": "Coursera",
        "url": "https://www.coursera.org/professional-certificates/google-cybersecurity",
        "is_free": True,
        "reason": "Cybersecurity expertise is in high demand and strongly resists automation.",
    },
    "skill_cloud_computing": {
        "course_title": "Google Cloud Fundamentals",
        "platform": "Google Digital Garage",
        "url": "https://learndigital.withgoogle.com/digitalgarage/courses",
        "is_free": True,
        "reason": "Cloud computing skills are highly protective and increasingly demanded.",
    },
    "skill_machine_learning_basics": {
        "course_title": "Machine Learning Specialization",
        "platform": "Coursera",
        "url": "https://www.coursera.org/specializations/machine-learning-introduction",
        "is_free": True,
        "reason": "ML knowledge positions graduates to work with AI, not be replaced by it.",
    },
    "skill_educational_technology": {
        "course_title": "Technology in Early Childhood Education",
        "platform": "Coursera",
        "url": "https://www.coursera.org/learn/education-technology",
        "is_free": True,
        "reason": "Educational technology integration future-proofs teaching careers.",
    },
    "skill_nursing_research": {
        "course_title": "Research Methods and Analysis",
        "platform": "edX",
        "url": "https://www.edx.org/learn/research-methods",
        "is_free": True,
        "reason": "Research skills make nursing professionals irreplaceable contributors to healthcare.",
    },
    "skill_emergency_care": {
        "course_title": "First Aid and Emergency Medical Response",
        "platform": "FutureLearn",
        "url": "https://www.futurelearn.com/courses/first-aid",
        "is_free": True,
        "reason": "Emergency care is a high-empathy, high-complexity skill that AI cannot replicate.",
    },
    "skill_business_communication": {
        "course_title": "Business English Communication Skills",
        "platform": "Coursera",
        "url": "https://www.coursera.org/specializations/business-english",
        "is_free": True,
        "reason": "Strong communication skills are among the most protective against automation.",
    },
    "default": {
        "course_title": "Fundamentals of Digital Marketing",
        "platform": "Google Digital Garage",
        "url": "https://learndigital.withgoogle.com/digitalgarage/course/digital-marketing",
        "is_free": True,
        "reason": "Digital skills broadly reduce automation vulnerability across all career paths.",
    },
}


def generate_recommendations(skill_gaps: list, degree_program: str, job_title: str) -> list[dict]:
    """
    Generate free online course recommendations for identified skill gaps.
    Uses Gemini 2.5 Flash when GEMINI_API_KEY is available, otherwise falls back.
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

A {degree_program} graduate working as {job_title} has the following skill gaps that make them vulnerable to automation:
{gap_text}

Recommend specific FREE online courses from these platforms only:
- Coursera (free audit)
- edX (free audit)
- Google Digital Garage
- LinkedIn Learning (free trial)
- FutureLearn (free)
- TESDA Online Program (TOP)
- DepEd Commons

For each gap, provide:
1. course_title (string)
2. platform (string)
3. url (valid URL string)
4. is_free (true)
5. reason (1 sentence explaining why this course addresses the automation risk)
6. skill (the skill_id from the gap)

Return ONLY a JSON array. No preamble. No markdown. No code blocks.
Example format: [{{"skill": "skill_id", "course_title": "...", "platform": "...", "url": "...", "is_free": true, "reason": "..."}}]"""

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    text = response.text.strip()

    # Strip markdown code blocks if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    courses = json.loads(text)
    return courses[:len(skill_gaps)]


def _fallback_recommendations(skill_gaps: list, degree_program: str, job_title: str) -> list[dict]:
    recommendations = []
    for gap in skill_gaps[:5]:
        skill_id = gap.get("skill_id", "")
        course = FALLBACK_COURSES.get(skill_id, FALLBACK_COURSES["default"]).copy()
        course["skill"] = gap.get("skill_label", skill_id)
        recommendations.append(course)
    return recommendations
