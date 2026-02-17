# 🧠 AI Resume Analyzer – Smart CV Screening System

> **Built by Hassan Ahmed**  
> A full-stack, AI-powered resume analysis web app with a modern glassmorphism UI, Flask backend, scikit-learn NLP engine, and Neon PostgreSQL database — deployable to Vercel in minutes.

---

## ✨ Live Demo

> Deploy to Vercel (see below) and share your URL here.

---

## 🎯 Features

| Feature | Description |
|---|---|
| 📄 Resume Upload | PDF & DOCX support with drag-and-drop |
| 🤖 AI Scoring | TF-IDF cosine similarity weighted score (keyword 60% + skills 20% + format 20%) |
| 🔑 Keyword Analysis | Matched vs missing JD keywords |
| 🛠 Skills Gap | 150+ skills across 8 categories |
| 📊 ATS Check | Detects formatting issues that block ATS parsers |
| 💡 AI Suggestions | Personalised improvement recommendations |
| 📥 PDF Report | Download full analysis as a styled PDF |
| 📈 Admin Dashboard | Charts, analytics, and history of all analyses |
| 🌐 Neon DB | Cloud PostgreSQL — persists data between serverless calls |

---

## 🎨 UI Design

- **Color Palette**: Dark Navy `#0F172A` · Neon Aqua `#00F5D4` · Pink `#F72585`
- **Style**: Glassmorphism cards · Animated particle background · Floating hero cards
- **Font**: Inter / Poppins (Google Fonts)
- **Animations**: Score circle counter · Confetti on high scores · Slide-in cards · Progress bars
- **Responsive**: Mobile + Desktop

---

## 🗂 Project Structure

```
ai-resume-analyzer/
│
├── app.py                  # Flask app + routes + DB models
├── requirements.txt        # Python dependencies
├── vercel.json             # Vercel deployment config
├── Procfile                # Gunicorn for Heroku/Render
├── .env.example            # Environment variable template
├── .gitignore
│
├── utils/
│   ├── __init__.py
│   ├── parser.py           # PDF/DOCX text extractor
│   ├── analyzer.py         # AI analysis engine (TF-IDF, skills, ATS)
│   └── report.py           # PDF report generator (ReportLab)
│
├── templates/
│   ├── base.html           # Shared layout (navbar, footer, particles)
│   ├── index.html          # Home page with upload form
│   ├── result.html         # Analysis results page
│   ├── dashboard.html      # Admin analytics dashboard
│   └── 404.html            # Error page
│
├── static/
│   ├── css/
│   │   └── style.css       # Full dark/glassmorphism stylesheet
│   ├── js/
│   │   ├── particles.js    # Animated particle canvas
│   │   ├── main.js         # Global utilities
│   │   ├── upload.js       # Drag-drop, validation, loading animation
│   │   ├── result.js       # Score animation, confetti
│   │   └── dashboard.js    # Chart.js charts, table search & delete
│   └── images/
│       └── favicon.svg
│
├── uploads/                # Temp upload directory (gitignored)
└── instance/               # SQLite DB for local dev (gitignored)
```

---

## ⚙️ Local Development Setup

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/ai-resume-analyzer.git
cd ai-resume-analyzer
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=true
DATABASE_URL=sqlite:///instance/resume_analyzer.db  # local SQLite
```

### 5. Run the app

```bash
python app.py
```

Open **http://localhost:5000** 🎉

---

## 🗄 Neon Database Setup (Production)

[Neon](https://neon.tech) is a serverless PostgreSQL — perfect for Vercel deployments.

1. Go to [neon.tech](https://neon.tech) → **Create a free account**
2. Click **New Project** → choose a region
3. On the **Dashboard** → **Connection Details** → copy the **Connection string**

```
postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

4. Set this as your `DATABASE_URL` in Vercel environment variables (see below)

> Tables are created automatically on first run via `db.create_all()`.

---

## 🚀 Vercel Deployment

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit – AI Resume Analyzer"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-resume-analyzer.git
git push -u origin main
```

### 2. Import to Vercel

1. Go to [vercel.com](https://vercel.com) → **Add New Project**
2. Import your GitHub repository
3. Framework: **Other** (Vercel detects `vercel.json` automatically)
4. Click **Environment Variables** → add:

| Key | Value |
|---|---|
| `SECRET_KEY` | `your-strong-random-secret` |
| `DATABASE_URL` | Your Neon connection string |
| `FLASK_DEBUG` | `false` |

5. Click **Deploy** 🚀

> **Note on file uploads with Vercel**: Vercel's serverless functions have ephemeral filesystems. The `uploads/` directory is used only temporarily during the request — files are processed and then deleted. This is already handled in `app.py`.

---

## 🔑 Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | Flask session secret — use a random 32-char hex string |
| `DATABASE_URL` | ✅ | Neon PostgreSQL connection string (or `sqlite:///...` for local) |
| `FLASK_DEBUG` | ❌ | Set to `true` in dev, `false` in prod |
| `OPENAI_API_KEY` | ❌ | Optional — for GPT-4 enhanced suggestions |

---

## 📡 API Endpoints

| Method | Route | Description |
|---|---|---|
| `GET` | `/` | Home page |
| `POST` | `/upload` | Upload resume + JD → analyze → redirect |
| `GET` | `/result/<uid>` | View analysis result |
| `GET` | `/download-report/<uid>` | Download PDF report |
| `GET` | `/dashboard` | Admin analytics dashboard |
| `GET` | `/api/analyses` | JSON list of all analyses |
| `DELETE` | `/api/delete/<id>` | Delete a single analysis |

---

## 🧪 Database Schema

```sql
CREATE TABLE resume_analysis (
  id                INTEGER PRIMARY KEY,
  uid               VARCHAR(36) UNIQUE NOT NULL,
  filename          VARCHAR(255),
  job_title         VARCHAR(255),
  job_description   TEXT,
  resume_text       TEXT,
  score             INTEGER,
  keyword_score     INTEGER,
  skills_score      INTEGER,
  format_score      INTEGER,
  matched_keywords  TEXT,   -- JSON array
  missing_keywords  TEXT,   -- JSON array
  matched_skills    TEXT,   -- JSON array
  missing_skills    TEXT,   -- JSON array
  suggestions       TEXT,   -- JSON array
  ats_issues        TEXT,   -- JSON array
  created_at        DATETIME
);
```

---

## 🧠 AI Scoring Formula

```
Final Score = (Keyword Match × 60%) + (Skills Match × 20%) + (Format Score × 20%)
```

- **Keyword Match**: TF-IDF vectorisation + cosine similarity between resume and JD
- **Skills Match**: Exact/pattern matching against 150+ skills across 8 taxonomy categories
- **Format Score**: Heuristic checks — contact info, section headings, word count, action verbs, dates

---

## 📦 Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.11 · Flask 3 · SQLAlchemy 2 |
| AI/NLP | scikit-learn (TF-IDF + cosine similarity) |
| Resume Parsing | pdfplumber · PyPDF2 · python-docx |
| Database | Neon PostgreSQL (prod) · SQLite (local) |
| Frontend | HTML5 · CSS3 (Glassmorphism) · Vanilla JS |
| Charts | Chart.js 4 |
| PDF Reports | ReportLab |
| Deployment | Vercel (serverless) |
| Version Control | Git + GitHub |

---

## 🛠 Extending the Project

### Add OpenAI GPT suggestions

In `utils/analyzer.py`, replace `_generate_suggestions()` with:

```python
import openai, os
client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def _gpt_suggestions(resume_text, job_description):
    prompt = f"""Analyze resume vs job description.
Provide:
1. Overall match assessment
2. Top 5 missing skills
3. 5 specific improvement suggestions
4. ATS compatibility feedback

Resume: {resume_text[:2000]}
Job Description: {job_description[:1000]}

Respond in JSON: {{"suggestions": [...], "ats_feedback": [...]}}"""
    
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(resp.choices[0].message.content)
```

### Add User Authentication

Install Flask-Login and add `User` model with bcrypt password hashing.

---

## 📄 License

MIT License – feel free to use, modify, and deploy.

---

## 👨‍💻 Author

**Hassan Ahmed** – AI Resume Analyzer  
Built with ❤️ using Flask, scikit-learn, and Neon DB.
