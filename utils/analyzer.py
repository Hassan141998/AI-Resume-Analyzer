"""
AI Resume Analyzer – Core Analysis Engine (Pure Python, Zero Heavy Deps)
=========================================================================
Implements TF-IDF + cosine similarity entirely in standard Python so that
scikit-learn and numpy are NOT required. This keeps the Vercel bundle well
under the 250 MB serverless limit.
"""

import re
import math
import random
import logging
from collections import Counter
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# ── Comprehensive Skill Taxonomy (150+ skills) ─────────────────────────────────
SKILLS_DB = {
    "programming_languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "c",
        "ruby", "php", "swift", "kotlin", "go", "rust", "scala", "r",
        "matlab", "perl", "shell", "bash", "powershell", "dart", "lua",
    ],
    "web_frontend": [
        "html", "css", "react", "reactjs", "vue", "vuejs", "angular",
        "nextjs", "nuxtjs", "svelte", "jquery", "bootstrap", "tailwind",
        "sass", "scss", "webpack", "vite", "graphql",
    ],
    "web_backend": [
        "flask", "django", "fastapi", "express", "nodejs", "spring",
        "laravel", "rails", "asp.net", "nestjs", "gin", "fiber",
    ],
    "databases": [
        "sql", "mysql", "postgresql", "postgres", "mongodb", "redis",
        "sqlite", "oracle", "cassandra", "dynamodb", "elasticsearch",
        "neo4j", "mariadb", "firebase",
    ],
    "cloud_devops": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
        "terraform", "ansible", "jenkins", "github actions", "circleci",
        "linux", "nginx", "apache", "helm", "prometheus", "grafana",
    ],
    "data_ml": [
        "machine learning", "deep learning", "nlp", "computer vision",
        "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
        "pandas", "numpy", "matplotlib", "seaborn", "spark", "hadoop",
        "tableau", "power bi", "data analysis", "data science",
        "statistics", "regression", "classification", "neural network",
    ],
    "tools_practices": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence",
        "agile", "scrum", "kanban", "ci/cd", "rest api", "microservices",
        "unit testing", "pytest", "jest", "selenium", "postman",
        "figma", "adobe xd", "linux", "vim",
    ],
    "soft_skills": [
        "leadership", "communication", "teamwork", "problem solving",
        "critical thinking", "time management", "adaptability",
        "project management", "collaboration", "presentation",
    ],
}

ALL_SKILLS: List[str] = [s for group in SKILLS_DB.values() for s in group]

SUGGESTIONS_BANK = [
    "Add quantifiable achievements (e.g., 'Increased sales by 30%').",
    "Use strong action verbs: led, built, designed, optimized, reduced.",
    "Include a concise professional summary at the top.",
    "Tailor the Skills section to match the job description keywords.",
    "Ensure consistent date formatting throughout (e.g., Jan 2022 – Mar 2024).",
    "Keep your resume to 1–2 pages for most roles.",
    "Spell out acronyms at least once (e.g., 'Natural Language Processing (NLP)').",
    "Add links to your GitHub, LinkedIn, or portfolio.",
    "Use a clean single-column layout for better ATS compatibility.",
    "Proofread carefully — typos can cost you the interview.",
    "Highlight the impact of your work, not just the tasks performed.",
    "List your most relevant experience first.",
]

# ── Pure-Python Text Utilities ─────────────────────────────────────────────────

# Common English stop words
_STOP_WORDS = {
    "a","an","the","and","or","but","in","on","at","to","for","of","with",
    "by","from","up","about","into","through","during","is","are","was",
    "were","be","been","being","have","has","had","do","does","did","will",
    "would","could","should","may","might","shall","can","need","dare",
    "ought","used","it","its","this","that","these","those","i","you","he",
    "she","we","they","what","which","who","whom","when","where","why","how",
    "all","each","every","both","few","more","most","other","some","such",
    "no","not","only","same","so","than","too","very","just","as","if",
    "then","because","while","although","though","unless","until","since",
    "after","before","above","below","between","under","over","again",
    "further","once","here","there","own","s","t","re","ve","ll","d",
}


def _tokenize(text: str) -> List[str]:
    """Lowercase, strip punctuation, split, remove stop words & short tokens."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return [t for t in text.split() if len(t) > 2 and t not in _STOP_WORDS]


def _term_freq(tokens: List[str]) -> Dict[str, float]:
    """Compute term frequency (normalised by document length)."""
    if not tokens:
        return {}
    counts = Counter(tokens)
    total = len(tokens)
    return {t: c / total for t, c in counts.items()}


def _idf(term: str, docs: List[List[str]]) -> float:
    """Compute inverse document frequency for a term across a corpus."""
    df = sum(1 for doc in docs if term in doc)
    if df == 0:
        return 0.0
    return math.log((1 + len(docs)) / (1 + df)) + 1.0


def _tfidf_vector(tokens: List[str], vocab: List[str],
                  idf_map: Dict[str, float]) -> List[float]:
    """Build a TF-IDF vector for given tokens over the vocab."""
    tf = _term_freq(tokens)
    return [tf.get(term, 0.0) * idf_map.get(term, 0.0) for term in vocab]


def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Cosine similarity between two equal-length vectors."""
    dot   = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def _similarity(text_a: str, text_b: str) -> float:
    """
    Compute TF-IDF cosine similarity between two texts.
    Pure Python — no numpy/sklearn required.
    """
    tok_a = _tokenize(text_a)
    tok_b = _tokenize(text_b)

    if not tok_a or not tok_b:
        return 0.0

    # Build shared vocabulary
    vocab = list(dict.fromkeys(tok_a + tok_b))  # preserve order, dedup
    docs  = [tok_a, tok_b]

    # Pre-compute IDF for each vocab term
    idf_map = {term: _idf(term, docs) for term in vocab}

    vec_a = _tfidf_vector(tok_a, vocab, idf_map)
    vec_b = _tfidf_vector(tok_b, vocab, idf_map)

    return _cosine_similarity(vec_a, vec_b)


def _top_keywords(text: str, n: int = 40) -> List[str]:
    """Return top-n keywords by TF-IDF score (unigrams)."""
    tokens = _tokenize(text)
    if not tokens:
        return []
    tf = _term_freq(tokens)
    # IDF relative to a single document — use log(1/tf) as a proxy
    scored = {t: score * (1 + math.log(1 / score)) for t, score in tf.items()}
    return sorted(scored, key=scored.get, reverse=True)[:n]


# ── Skill & Keyword Matching ───────────────────────────────────────────────────

def _match_skills(resume_text: str, jd_text: str) -> Dict[str, List[str]]:
    """Return matched / missing skills based on the job description."""
    resume_lower = resume_text.lower()
    jd_lower     = jd_text.lower()

    jd_skills: List[str] = []
    for skill in ALL_SKILLS:
        # Use word-boundary matching for short tokens to avoid false positives
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, jd_lower):
            jd_skills.append(skill)

    matched: List[str] = []
    missing: List[str] = []
    for skill in jd_skills:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, resume_lower):
            matched.append(skill)
        else:
            missing.append(skill)

    return {
        "matched": list(dict.fromkeys(matched)),
        "missing": list(dict.fromkeys(missing)),
    }


def _keyword_overlap(resume_text: str, jd_text: str) -> Dict[str, List[str]]:
    """Find keywords present in JD that are / aren't in the resume."""
    jd_kws     = set(_top_keywords(jd_text,     n=40))
    resume_kws = set(_top_keywords(resume_text, n=60))
    matched    = sorted(jd_kws & resume_kws)[:20]
    missing    = sorted(jd_kws - resume_kws)[:20]
    return {"matched": matched, "missing": missing}


# ── Format Score (heuristic) ───────────────────────────────────────────────────

def _format_score(resume_text: str) -> int:
    score = 0
    lower = resume_text.lower()
    words = resume_text.split()

    # Length
    if 300 <= len(words) <= 1200:
        score += 25
    elif len(words) > 100:
        score += 12

    # Contact info
    if re.search(r"\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b", lower):
        score += 15
    if re.search(r"\+?[\d\s()\-]{7,15}", resume_text):
        score += 10

    # Section headings
    headings = ["experience", "education", "skills", "summary", "objective",
                "projects", "certifications", "achievements"]
    found = sum(1 for h in headings if h in lower)
    score += min(found * 5, 30)

    # Dates
    if re.search(r"\b(20\d{2}|19\d{2})\b", resume_text):
        score += 10

    # Action verbs
    verbs = ["led", "built", "designed", "managed", "developed", "implemented",
             "improved", "reduced", "increased", "achieved", "created", "delivered"]
    if any(v in lower for v in verbs):
        score += 10

    return min(score, 100)


# ── ATS Check ─────────────────────────────────────────────────────────────────

def _ats_check(resume_text: str) -> List[str]:
    issues: List[str] = []
    lower = resume_text.lower()

    if re.search(r"\|.+\|", resume_text):
        issues.append("Avoid tables – ATS parsers may skip content inside them.")
    if re.search(r"[★✓✔➤►●▪▸]", resume_text):
        issues.append("Replace special bullet characters with plain hyphens or asterisks.")
    if not re.search(r"\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b", resume_text):
        issues.append("No email address detected – make sure your contact info is in plain text.")
    if not re.search(r"\+?[\d\s()\-]{7,14}", resume_text):
        issues.append("No phone number detected – ensure contact details are ATS-readable.")
    if len(resume_text.split()) < 150:
        issues.append("Resume seems very short. Consider adding more detail to relevant sections.")
    if not re.search(r"\b(experience|work|project|skill)\b", lower):
        issues.append("Key sections (Experience, Skills, Projects) not detected. Use standard headings.")

    return issues


# ── Suggestions ───────────────────────────────────────────────────────────────

def _generate_suggestions(score: int, missing_skills: List[str],
                           missing_keywords: List[str]) -> List[str]:
    suggestions: List[str] = []

    if missing_skills:
        top = ", ".join(missing_skills[:5])
        suggestions.append(f"Add these missing skills if you have them: {top}.")
    if missing_keywords:
        top = ", ".join(missing_keywords[:5])
        suggestions.append(f"Incorporate these job-description keywords naturally: {top}.")

    if score < 50:
        suggestions.append("Your resume needs significant tailoring for this role. Review the JD carefully.")
    elif score < 70:
        suggestions.append("Good foundation! Focus on keyword alignment and quantified achievements.")
    else:
        suggestions.append("Strong match! Fine-tune language to mirror the exact phrasing in the JD.")

    random.seed(score)
    suggestions += random.sample(SUGGESTIONS_BANK, k=min(3, len(SUGGESTIONS_BANK)))
    return suggestions[:8]


# ── Public API ─────────────────────────────────────────────────────────────────

def analyze_resume(resume_text: str, job_description: str) -> Dict[str, Any]:
    """
    Full analysis pipeline — pure Python, no heavy ML libraries.
    Returns score, keyword data, skills data, suggestions, ATS issues.
    """
    # 1. Keyword similarity → 60 % weight
    raw_sim       = _similarity(resume_text, job_description)
    # Scale: raw cosine for well-matched docs is ~0.25–0.65; map to 0-100
    keyword_score = min(int(raw_sim * 200), 100)

    # 2. Keyword overlap lists
    kw_data = _keyword_overlap(resume_text, job_description)

    # 3. Skills matching → 20 % weight
    skills_data    = _match_skills(resume_text, job_description)
    jd_skill_count = len(skills_data["matched"]) + len(skills_data["missing"])
    if jd_skill_count > 0:
        skills_score = int(len(skills_data["matched"]) / jd_skill_count * 100)
    else:
        skills_score = 70

    # 4. Formatting score → 20 % weight
    format_score = _format_score(resume_text)

    # 5. Weighted composite score
    final_score = int(
        keyword_score * 0.60 +
        skills_score  * 0.20 +
        format_score  * 0.20
    )
    final_score = max(10, min(final_score, 100))

    # 6. ATS issues
    ats_issues = _ats_check(resume_text)

    # 7. Suggestions
    suggestions = _generate_suggestions(
        final_score, skills_data["missing"], kw_data["missing"]
    )

    return {
        "score":            final_score,
        "keyword_score":    keyword_score,
        "skills_score":     skills_score,
        "format_score":     format_score,
        "matched_keywords": kw_data["matched"],
        "missing_keywords": kw_data["missing"],
        "matched_skills":   skills_data["matched"],
        "missing_skills":   skills_data["missing"],
        "suggestions":      suggestions,
        "ats_issues":       ats_issues,
    }
