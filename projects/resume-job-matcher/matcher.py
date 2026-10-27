"""Transparent, dictionary-based resume and job description matcher."""

from __future__ import annotations

import re
from dataclasses import dataclass

MAX_TEXT_CHARS = 60_000


@dataclass(frozen=True)
class Skill:
    name: str
    category: str
    aliases: tuple[str, ...]


SKILLS = (
    Skill("Python", "Programming", ("python", "python3")),
    Skill("Java", "Programming", ("java",)),
    Skill("JavaScript", "Programming", ("javascript", r"(?<![\w.])js(?!\w)")),
    Skill("TypeScript", "Programming", ("typescript", "ts")),
    Skill("C++", "Programming", ("c\\+\\+",)),
    Skill("C#", "Programming", ("c\\#", "c sharp")),
    Skill("C", "Programming", (r"(?<![A-Za-z0-9_])c(?![A-Za-z0-9_+#])",)),
    Skill("Go", "Programming", ("golang",)),
    Skill("Rust", "Programming", ("rust",)),
    Skill("HTML", "Web development", ("html",)),
    Skill("CSS", "Web development", ("css",)),
    Skill("React", "Web development", ("react", "reactjs")),
    Skill("Node.js", "Web development", ("node\\.js", "nodejs")),
    Skill("REST APIs", "Web development", ("rest apis?", "restful apis?")),
    Skill("SQL", "Databases", ("sql", "structured query language")),
    Skill("MySQL", "Databases", ("mysql",)),
    Skill("PostgreSQL", "Databases", ("postgresql", "postgres")),
    Skill("MongoDB", "Databases", ("mongodb",)),
    Skill("Data Structures and Algorithms", "Computer science", (
        "data structures and algorithms", "dsa",
    )),
    Skill("Object-Oriented Programming", "Computer science", (
        "object[- ]oriented programming", "oop",
    )),
    Skill("Machine Learning", "Artificial intelligence", ("machine learning", "ml")),
    Skill("Deep Learning", "Artificial intelligence", ("deep learning",)),
    Skill("Natural Language Processing", "Artificial intelligence", (
        "natural language processing", "nlp",
    )),
    Skill("Generative AI", "Artificial intelligence", (
        "generative ai", "generative artificial intelligence", "genai",
    )),
    Skill("Large Language Models", "Artificial intelligence", (
        "large language models?", "llms?",
    )),
    Skill("Retrieval-Augmented Generation", "Artificial intelligence", (
        "retrieval[- ]augmented generation", "rag",
    )),
    Skill("Prompt Engineering", "Artificial intelligence", ("prompt engineering",)),
    Skill("TensorFlow", "Machine learning tools", ("tensorflow",)),
    Skill("Keras", "Machine learning tools", ("keras",)),
    Skill("PyTorch", "Machine learning tools", ("pytorch",)),
    Skill("scikit-learn", "Machine learning tools", (
        "scikit[- ]learn", "sklearn",
    )),
    Skill("pandas", "Data tools", ("pandas",)),
    Skill("NumPy", "Data tools", ("numpy",)),
    Skill("Matplotlib", "Data tools", ("matplotlib",)),
    Skill("Seaborn", "Data tools", ("seaborn",)),
    Skill("Data Analysis", "Data", ("data analysis", "data analytics")),
    Skill("Data Visualization", "Data", ("data visualization", "data visualisation")),
    Skill("Feature Engineering", "Data", ("feature engineering",)),
    Skill("Exploratory Data Analysis", "Data", (
        "exploratory data analysis", "eda",
    )),
    Skill("Classification", "Machine learning methods", ("classification",)),
    Skill("Regression", "Machine learning methods", ("regression",)),
    Skill("Model Evaluation", "Machine learning methods", ("model evaluation",)),
    Skill("Natural Language Toolkit", "NLP tools", ("nltk",)),
    Skill("spaCy", "NLP tools", ("spacy",)),
    Skill("Git", "Developer tools", ("git", "github")),
    Skill("Docker", "Developer tools", ("docker",)),
    Skill("Linux", "Developer tools", ("linux",)),
    Skill("Amazon Web Services", "Cloud", ("amazon web services", "aws")),
    Skill("Microsoft Azure", "Cloud", ("microsoft azure", "azure")),
    Skill("Google Cloud Platform", "Cloud", ("google cloud platform", "gcp")),
    Skill("Agile", "Ways of working", ("agile",)),
)


def _compile_patterns(skill: Skill) -> tuple[re.Pattern[str], ...]:
    return tuple(
        re.compile(r"(?<!\w)(?:" + alias + r")(?!\w)", re.IGNORECASE)
        for alias in skill.aliases
    )


SKILL_PATTERNS = tuple((skill, _compile_patterns(skill)) for skill in SKILLS)


def validate_text(text: object, label: str) -> str:
    if not isinstance(text, str):
        raise ValueError(f"{label} must be text.")
    if not text.strip():
        raise ValueError(f"{label} is required; paste or upload its text.")
    if len(text) > MAX_TEXT_CHARS:
        raise ValueError(f"{label} must be {MAX_TEXT_CHARS:,} characters or fewer.")
    return text


def extract_skills(text: str) -> list[dict[str, str]]:
    """Return unique, recognized resume/job skills in the catalog's stable order."""
    found = []
    for skill, patterns in SKILL_PATTERNS:
        if any(pattern.search(text) for pattern in patterns):
            found.append({"name": skill.name, "category": skill.category})
    return found


def compare_resume_to_job(resume_text: object, job_text: object) -> dict[str, object]:
    """Score only recognizable job-posting skills; never claim an employability score."""
    resume = validate_text(resume_text, "Resume")
    job = validate_text(job_text, "Job description")
    resume_skills = extract_skills(resume)
    required_skills = extract_skills(job)
    resume_names = {item["name"] for item in resume_skills}
    job_names = {item["name"] for item in required_skills}
    matched = [item for item in required_skills if item["name"] in resume_names]
    missing = [item for item in required_skills if item["name"] not in resume_names]
    additional = [item for item in resume_skills if item["name"] not in job_names]
    score = round(100 * len(matched) / len(required_skills)) if required_skills else None
    return {
        "score": score,
        "score_label": (
            f"{len(matched)} of {len(required_skills)} recognized job-description skills found"
            if required_skills
            else "No catalogued skills found in the job description"
        ),
        "matched": matched,
        "missing": missing,
        "additional": additional,
        "resume_skill_count": len(resume_skills),
        "job_skill_count": len(required_skills),
        "disclaimer": (
            "This is a transparent keyword-coverage estimate, not an AI judgment, "
            "hiring prediction, ATS score, or assessment of experience level. "
            "Review the full job description and tailor your resume truthfully."
        ),
    }
