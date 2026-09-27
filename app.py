from flask import Flask, render_template, request
from PyPDF2 import PdfReader
import os
import re
from database import get_connection

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, email, ats_score, created_at
        FROM candidates
        ORDER BY id DESC
    """)

    candidates = cursor.fetchall()

    total_candidates = len(candidates)

    if total_candidates > 0:

        total_score = sum(
            candidate[3] for candidate in candidates
        )

        average_score = round(
            total_score / total_candidates
        )

    else:
        average_score = 0

    cursor.close()
    connection.close()

    return render_template(
        "dashboard.html",
        candidates=candidates,
        total_candidates=total_candidates,
        average_score=average_score
    )


# =========================
# RESUME ANALYSIS
# =========================

@app.route("/analyze", methods=["POST"])
def analyze():

    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    job_description = request.form.get(
        "job_description",
        ""
    )

    resume = request.files.get("resume")

    if not resume:
        return "Please upload a PDF resume."

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        resume.filename
    )

    resume.save(file_path)

    # =========================
    # READ PDF
    # =========================

    reader = PdfReader(file_path)

    resume_text = ""

    for page in reader.pages:

        text = page.extract_text()

        if text:
            resume_text += text + " "

    # Convert to lowercase
    resume_text = resume_text.lower()
    job_description = job_description.lower()

    # =========================
    # EXTRACT KEYWORDS
    # =========================

    words = re.findall(
        r"\b[a-zA-Z][a-zA-Z+#.-]{1,}\b",
        job_description
    )

    stop_words = {
        "the", "and", "for", "with",
        "that", "this", "from", "are",
        "you", "your", "our", "will",
        "have", "has", "job", "work",
        "using", "looking", "about",
        "their", "they", "who"
    }

    keywords = []

    for word in words:

        word = word.lower()

        if (
            word not in stop_words
            and word not in keywords
        ):
            keywords.append(word)

    # =========================
    # COMPARE KEYWORDS
    # =========================

    matched_skills = []
    missing_skills = []

    for keyword in keywords:

        if keyword in resume_text:
            matched_skills.append(keyword)

        else:
            missing_skills.append(keyword)

    # =========================
    # ATS SCORE
    # =========================

    if len(keywords) > 0:

        score = round(
            (len(matched_skills) / len(keywords))
            * 100
        )

    else:
        score = 0

    # =========================
    # SAVE RESULT TO MYSQL
    # =========================

    connection = get_connection()
    cursor = connection.cursor()

    sql = """
    INSERT INTO candidates
    (
        name,
        email,
        phone,
        resume,
        job_description,
        ats_score,
        matched_skills,
        missing_skills
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        name,
        email,
        phone,
        resume.filename,
        job_description,
        score,
        ", ".join(matched_skills),
        ", ".join(missing_skills)
    )

    cursor.execute(sql, values)

    connection.commit()

    cursor.close()
    connection.close()

    # =========================
    # TERMINAL OUTPUT
    # =========================

    print("\n========== ATS RESULT ==========")
    print("Name:", name)
    print("Email:", email)
    print("Phone:", phone)
    print("ATS Score:", score)
    print("Matched Skills:", matched_skills)
    print("Missing Skills:", missing_skills)

    # =========================
    # RESULT PAGE
    # =========================

    return f"""
    <html>

    <head>

        <title>ATS Result</title>

        <style>

            body {{
                font-family: Arial, sans-serif;
                background: #020617;
                color: white;
                padding: 40px;
            }}

            .result {{
                max-width: 700px;
                margin: auto;
                padding: 30px;
                background: #0f172a;
                border-radius: 15px;
            }}

            h1 {{
                color: #60a5fa;
            }}

            .score {{
                font-size: 40px;
                color: #22c55e;
                margin: 20px 0;
            }}

            .skills {{
                padding: 15px;
                background: #1e293b;
                border-radius: 10px;
                margin-top: 15px;
            }}

            a {{
                display: inline-block;
                margin-top: 20px;
                color: white;
                background: #2563eb;
                padding: 12px 20px;
                border-radius: 8px;
                text-decoration: none;
            }}

        </style>

    </head>

    <body>

        <div class="result">

            <h1>ATS Resume Analysis</h1>

            <p>
                <strong>Name:</strong> {name}
            </p>

            <p>
                <strong>Email:</strong> {email}
            </p>

            <p>
                <strong>Phone:</strong> {phone}
            </p>

            <div class="score">
                ATS Score: {score}%
            </div>

            <div class="skills">

                <h2>Matched Skills</h2>

                <p>
                    {", ".join(matched_skills)
                    if matched_skills
                    else "No matching keywords found"}
                </p>

            </div>

            <div class="skills">

                <h2>Missing Skills</h2>

                <p>
                    {", ".join(missing_skills)
                    if missing_skills
                    else "No missing keywords"}
                </p>

            </div>

            <a href="/">
                Analyze Another Resume
            </a>

        </div>

    </body>

    </html>
    """


# =========================
# START FLASK
# =========================

if __name__ == "__main__":
    app.run(
        debug=True,
        use_reloader=False,
        port=5001
    )
    