"""
AI Resume Analyzer - Main Flask Application
Built by Hassan Ahmed
"""

import os
import json
import uuid
import logging
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify, send_file
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

from utils.parser import extract_text_from_file
from utils.analyzer import analyze_resume
from utils.report import generate_pdf_report

# ── App ───────────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# ── Database ──────────────────────────────────────────────────────────────────
BASE_DIR     = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "uploads"), exist_ok=True)

_default_db  = "sqlite:///" + os.path.join(INSTANCE_DIR, "resume_analyzer.db")
DATABASE_URL = os.environ.get("DATABASE_URL", _default_db)

# Fix Heroku/Neon "postgres://" → "postgresql+pg8000://"
# pg8000 is the pure-Python Postgres driver (no binary, tiny size)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+pg8000://", 1)
elif DATABASE_URL.startswith("postgresql://") and "+pg8000" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+pg8000://", 1)

# pg8000 doesn't support sslmode in the URL; strip it and use connect_args
ssl_required = "sslmode=require" in DATABASE_URL
if ssl_required:
    DATABASE_URL = DATABASE_URL.split("?")[0]

engine_options = {"pool_pre_ping": True, "pool_recycle": 300}
if ssl_required:
    import ssl as _ssl
    _ssl_ctx = _ssl.create_default_context()
    _ssl_ctx.check_hostname = False
    _ssl_ctx.verify_mode    = _ssl.CERT_NONE
    engine_options["connect_args"] = {"ssl_context": _ssl_ctx}

app.config["SQLALCHEMY_DATABASE_URI"]    = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"]  = engine_options

# ── Upload ────────────────────────────────────────────────────────────────────
UPLOAD_FOLDER      = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"pdf", "docx", "doc"}

app.config["UPLOAD_FOLDER"]    = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB

db = SQLAlchemy(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.jinja_env.filters["enumerate"] = enumerate


# ── Model ─────────────────────────────────────────────────────────────────────
class ResumeAnalysis(db.Model):
    __tablename__ = "resume_analysis"

    id              = db.Column(db.Integer, primary_key=True)
    uid             = db.Column(db.String(36), unique=True, nullable=False,
                                default=lambda: str(uuid.uuid4()))
    filename        = db.Column(db.String(255), nullable=False)
    job_title       = db.Column(db.String(255), nullable=True)
    job_description = db.Column(db.Text, nullable=False)
    resume_text     = db.Column(db.Text, nullable=True)
    score           = db.Column(db.Integer, nullable=False, default=0)
    keyword_score   = db.Column(db.Integer, nullable=True)
    skills_score    = db.Column(db.Integer, nullable=True)
    format_score    = db.Column(db.Integer, nullable=True)
    matched_keywords = db.Column(db.Text, nullable=True)
    missing_keywords = db.Column(db.Text, nullable=True)
    matched_skills   = db.Column(db.Text, nullable=True)
    missing_skills   = db.Column(db.Text, nullable=True)
    suggestions      = db.Column(db.Text, nullable=True)
    ats_issues       = db.Column(db.Text, nullable=True)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":               self.id,
            "uid":              self.uid,
            "filename":         self.filename,
            "job_title":        self.job_title,
            "score":            self.score,
            "keyword_score":    self.keyword_score,
            "skills_score":     self.skills_score,
            "format_score":     self.format_score,
            "matched_keywords": json.loads(self.matched_keywords or "[]"),
            "missing_keywords": json.loads(self.missing_keywords or "[]"),
            "matched_skills":   json.loads(self.matched_skills   or "[]"),
            "missing_skills":   json.loads(self.missing_skills   or "[]"),
            "suggestions":      json.loads(self.suggestions      or "[]"),
            "ats_issues":       json.loads(self.ats_issues       or "[]"),
            "created_at":       self.created_at.strftime("%Y-%m-%d %H:%M"),
        }


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "resume" not in request.files:
        flash("No file part in request.", "error")
        return redirect(url_for("index"))

    file            = request.files["resume"]
    job_description = request.form.get("job_description", "").strip()
    job_title       = request.form.get("job_title", "").strip()

    if file.filename == "":
        flash("Please select a resume file.", "error")
        return redirect(url_for("index"))
    if not allowed_file(file.filename):
        flash("Only PDF and DOCX files are supported.", "error")
        return redirect(url_for("index"))
    if not job_description:
        flash("Please enter a job description.", "error")
        return redirect(url_for("index"))

    try:
        filename  = secure_filename(file.filename)
        unique_fn = f"{uuid.uuid4().hex}_{filename}"
        filepath  = os.path.join(app.config["UPLOAD_FOLDER"], unique_fn)
        file.save(filepath)

        resume_text = extract_text_from_file(filepath)
        if not resume_text or len(resume_text.strip()) < 50:
            flash("Could not extract readable text. Please check the file.", "error")
            os.remove(filepath)
            return redirect(url_for("index"))

        result = analyze_resume(resume_text, job_description)

        analysis = ResumeAnalysis(
            filename         = filename,
            job_title        = job_title,
            job_description  = job_description,
            resume_text      = resume_text[:5000],
            score            = result["score"],
            keyword_score    = result["keyword_score"],
            skills_score     = result["skills_score"],
            format_score     = result["format_score"],
            matched_keywords = json.dumps(result["matched_keywords"]),
            missing_keywords = json.dumps(result["missing_keywords"]),
            matched_skills   = json.dumps(result["matched_skills"]),
            missing_skills   = json.dumps(result["missing_skills"]),
            suggestions      = json.dumps(result["suggestions"]),
            ats_issues       = json.dumps(result["ats_issues"]),
        )
        db.session.add(analysis)
        db.session.commit()
        try:
            os.remove(filepath)
        except Exception:
            pass
        return redirect(url_for("result", uid=analysis.uid))

    except Exception as exc:
        logger.exception("Upload/analysis error: %s", exc)
        flash(f"An error occurred: {exc}", "error")
        return redirect(url_for("index"))


@app.route("/result/<uid>")
def result(uid):
    analysis = ResumeAnalysis.query.filter_by(uid=uid).first_or_404()
    return render_template("result.html", data=analysis.to_dict())


@app.route("/download-report/<uid>")
def download_report(uid):
    analysis = ResumeAnalysis.query.filter_by(uid=uid).first_or_404()
    try:
        pdf_path = generate_pdf_report(analysis.to_dict())
        return send_file(pdf_path, as_attachment=True,
                         download_name=f"resume_analysis_{uid[:8]}.pdf",
                         mimetype="application/pdf")
    except Exception as exc:
        logger.exception("PDF error: %s", exc)
        flash("PDF generation failed.", "error")
        return redirect(url_for("result", uid=uid))


@app.route("/dashboard")
def dashboard():
    analyses   = ResumeAnalysis.query.order_by(ResumeAnalysis.created_at.desc()).all()
    total      = len(analyses)
    avg_score  = int(sum(a.score for a in analyses) / total) if total else 0
    high_score = len([a for a in analyses if a.score >= 80])
    mid_score  = len([a for a in analyses if 50 <= a.score < 80])
    low_score  = len([a for a in analyses if a.score < 50])
    recent_scores = [
        {"filename": a.filename[:20], "score": a.score,
         "date": a.created_at.strftime("%b %d")}
        for a in analyses[:10]
    ]
    return render_template("dashboard.html",
                           analyses=analyses, total=total, avg_score=avg_score,
                           high_score=high_score, mid_score=mid_score, low_score=low_score,
                           recent_scores=json.dumps(recent_scores))


@app.route("/api/analyses")
def api_analyses():
    analyses = ResumeAnalysis.query.order_by(
        ResumeAnalysis.created_at.desc()).limit(50).all()
    return jsonify([a.to_dict() for a in analyses])


@app.route("/api/delete/<int:analysis_id>", methods=["DELETE"])
def api_delete(analysis_id):
    analysis = db.session.get(ResumeAnalysis, analysis_id)
    if not analysis:
        return jsonify({"error": "Not found"}), 404
    db.session.delete(analysis)
    db.session.commit()
    return jsonify({"success": True})


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(413)
def too_large(e):
    flash("File too large. Max 10 MB.", "error")
    return redirect(url_for("index"))


# ── Init DB ───────────────────────────────────────────────────────────────────
with app.app_context():
    db.create_all()
    logger.info("Database ready.")

if __name__ == "__main__":
    PORT  = int(os.environ.get("PORT", 5000))
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

    print("\n")
    print("  \033[96m╔══════════════════════════════════════════════╗\033[0m")
    print("  \033[96m║        🧠  AI Resume Analyzer  🧠            ║\033[0m")
    print("  \033[96m║        Built by Hassan Ahmed                 ║\033[0m")
    print("  \033[96m╚══════════════════════════════════════════════╝\033[0m")
    print()
    print(f"  \033[92m✔  Server running!\033[0m")
    print(f"  \033[93m➜  Local:     \033[4mhttp://127.0.0.1:{PORT}\033[0m")
    print(f"  \033[93m➜  Network:   \033[4mhttp://localhost:{PORT}\033[0m")
    print(f"  \033[93m➜  Dashboard: \033[4mhttp://127.0.0.1:{PORT}/dashboard\033[0m")
    print()
    print(f"  \033[90mDebug : {'ON' if DEBUG else 'OFF'}\033[0m")
    print(f"  \033[90mDB    : {DATABASE_URL.split('?')[0]}\033[0m")
    print("  \033[90mPress Ctrl+C to stop.\033[0m\n")

    app.run(debug=DEBUG, port=PORT, host="0.0.0.0")
