import os
import re
import json
import pandas as pd
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import PyPDF2
from dotenv import load_dotenv
import google.generativeai as genai

# -----------------------------------------------------------
# 🌍 Load environment variables and configure Gemini
# -----------------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCna0ATJwFqlzklMihEhM-XRqhcLQoMXZs").strip()

# Initialize Gemini client safely
USE_AI = bool(GEMINI_API_KEY and not GEMINI_API_KEY.lower().startswith(("ai", "gemini")))
if USE_AI:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')

# -----------------------------------------------------------
# ⚙️ Flask app setup
# -----------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "change-me-in-prod")
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# -----------------------------------------------------------
# 🧮 Improved fallback grading (Length + Relevance + Feedback)
# -----------------------------------------------------------
def simple_grade_answer(question, answer):
    """
    Fallback grader when AI is unavailable.
    Grades based on both relevance (keyword overlap) and answer length.
    Provides only strengths and improvements (clean feedback).
    """
    q_words = set(re.findall(r"\w+", question.lower()))
    a_words = re.findall(r"\w+", answer.lower())
    word_count = len(a_words)

    if word_count == 0:
        return 1, "**Improvements:**\n- No answer detected. Please provide a response."

    # Relevance score
    overlap = len(q_words & set(a_words))
    relevance_ratio = overlap / max(1, len(q_words))
    relevance_score = relevance_ratio * 10

    # Length score
    length_score = 10 if word_count >= 100 else (word_count / 100) * 10

    # Weighted grade
    final_score = (0.6 * relevance_score) + (0.4 * length_score)
    grade = int(round(max(1, min(10, final_score))))

    # Generate strengths and improvements
    strengths = []
    improvements = []

    if relevance_ratio > 0.6:
        strengths.append("Answer is highly relevant to the question.")
    elif relevance_ratio > 0.3:
        strengths.append("Answer shows partial relevance to the question.")
    else:
        improvements.append("Answer lacks clear connection to the question topic.")

    if word_count >= 80:
        strengths.append("Good explanation length, showing sufficient detail.")
    elif word_count >= 40:
        strengths.append("Moderate explanation length.")
        improvements.append("Consider providing more elaboration or examples.")
    else:
        improvements.append("Answer is too short; lacks depth or reasoning.")

    # Clean feedback (only Strengths and Improvements)
    feedback = (
        f"**Strengths:**\n" +
        ("\n".join(f"- {s}" for s in strengths) if strengths else "- None listed") +
        "\n\n**Improvements:**\n" +
        ("\n".join(f"- {i}" for i in improvements) if improvements else "- None listed")
    )

    return grade, feedback


# -----------------------------------------------------------
# 🤖 AI-based grading using Gemini API
# -----------------------------------------------------------
def ai_grade_answer(question, answer):
    """
    Grade answer using Google's Gemini model with enhanced prompt engineering.
    Returns: (score: int, feedback: str)
    """
    if not USE_AI:
        return simple_grade_answer(question, answer)

    try:
        prompt = f"""You are an expert educator. Grade the student's answer based on accuracy, completeness, and clarity. 
        Provide a score (1-10) and specific feedback.

        Question: {question}

        Student Answer: {answer}

        Please provide:
        1. A score from 1-10
        2. Feedback in two sections only:
           - **Strengths:** What was done well
           - **Improvements:** What can be improved

        Format response as:
        Score: X/10
        **Strengths:**
        - ...
        **Improvements:**
        - ...
        """

        response = model.generate_content(prompt)
        feedback = response.text

        # Try to extract a numerical score from the feedback (1-10)
        score_match = re.search(r'(?i)(?:score|grade):?\s*(\d+(?:\.\d+)?)/?\s*10?', feedback)
        if score_match:
            score = min(10, max(1, float(score_match.group(1))))  # Clamp between 1-10
        else:
            return simple_grade_answer(question, answer)

        return score, feedback

    except Exception as e:
        return simple_grade_answer(question, answer)


# -----------------------------------------------------------
# 📄 Extract answers from PDF
# -----------------------------------------------------------
def extract_answers_from_pdf(pdf_path):
    answers = {}
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            try:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            except Exception:
                continue

    pattern = re.compile(
        r"(?:RegNo|Reg No|RegNo.)\s*[:\-]?\s*(\w+).*?(?:Section)\s*[:\-]?\s*([\w\-]+).*?(?:Answer)\s*[:\-]?\s*(.+?)(?=(?:RegNo|Reg No|$))",
        re.S | re.I
    )
    matches = pattern.findall(text)
    for regno, section, answer in matches:
        answers[regno.strip()] = {"section": section.strip(), "answer": answer.strip()}
    return answers


# -----------------------------------------------------------
# 🌐 Flask Routes
# -----------------------------------------------------------
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/grade', methods=['POST'])
def grade():
    question = request.form.get('question', '').strip()
    section = request.form.get('section', '').strip()
    file = request.files.get('pdf')

    if not question:
        flash("Please enter the question.", "danger")
        return redirect(url_for('index'))
    if not section:
        flash("Please enter/select a section.", "danger")
        return redirect(url_for('index'))
    if not file or not file.filename.lower().endswith('.pdf'):
        flash("Please upload a valid PDF file.", "danger")
        return redirect(url_for('index'))

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    student_data = extract_answers_from_pdf(filepath)
    results = []

    for regno, details in student_data.items():
        if details["section"].lower() == section.lower():
            try:
                grade_val, feedback_text = ai_grade_answer(question, details["answer"])
                results.append({
                    "RegNo": regno,
                    "Section": details["section"],
                    "Submission": details["answer"],
                    "Feedback": feedback_text,
                    "Grade": grade_val
                })
            except Exception as e:
                flash(f"Failed to grade RegNo {regno}: {e}", "danger")

    if not results:
        flash("No answers found for the chosen section.", "warning")
        return redirect(url_for('index'))

    df = pd.DataFrame(results)
    csv_path = "graded_feedback.csv"
    df.to_csv(csv_path, index=False)
    table_html = df.to_html(classes="table table-striped", index=False, justify='left')

    return render_template('index.html', tables=table_html, download=True)


@app.route('/download', methods=['GET'])
def download():
    path = "graded_feedback.csv"
    if not os.path.exists(path):
        flash("No graded_feedback.csv found. Please grade first.", "danger")
        return redirect(url_for('index'))
    return send_file(path, as_attachment=True)


# -----------------------------------------------------------
# 🚀 Run Flask app
# -----------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
