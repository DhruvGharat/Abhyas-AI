import os
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv

from services.gemini_service import ask_gemini
from services.tutor_service import answer_tutor_question

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "abhyas_ai_secret_key_2026")

# Global in-memory cache to store transcripts by video_id
TRANSCRIPT_STORE = {}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/learn")
def learn():
    return render_template("learning/learn.html")


@app.route("/process-youtube", methods=["POST"])
def process_youtube():
    from services.youtube_service import extract_video_id
    from services.transcript_service import get_transcript
    from services.quiz_service import generate_quiz

    # ---------------------------------
    # Get YouTube URL
    # ---------------------------------
    data = request.get_json() or {}
    youtube_url = data.get("url", "").strip()

    if not youtube_url:
        return jsonify({
            "success": False,
            "error": "Please enter a YouTube URL."
        }), 400

    # ---------------------------------
    # Extract Video ID
    # ---------------------------------
    video_id = extract_video_id(youtube_url)

    if not video_id:
        return jsonify({
            "success": False,
            "error": "Invalid YouTube URL."
        }), 400

    # ---------------------------------
    # Get Transcript
    # ---------------------------------
    transcript = get_transcript(video_id)

    if not transcript:
        return jsonify({
            "success": False,
            "error": "Could not retrieve the transcript for this video."
        }), 400

    # Save transcript in server cache and store current video_id in session
    TRANSCRIPT_STORE[video_id] = transcript
    session["video_id"] = video_id

    # ---------------------------------
    # Generate Quiz
    # ---------------------------------
    try:
        quiz = generate_quiz(transcript)
    except Exception as error:
        print(f"Quiz generation error: {error}")
        return jsonify({
            "success": False,
            "error": "Something went wrong while generating the quiz."
        }), 500

    # ---------------------------------
    # Convert Quiz to JSON
    # ---------------------------------
    return jsonify({
        "success": True,
        "video_id": video_id,
        "quiz": quiz.model_dump()
    })


@app.route("/ask-tutor", methods=["POST"])
def ask_tutor():
    data = request.get_json() or {}
    question = data.get("question", "").strip()
    video_id = data.get("video_id") or session.get("video_id")

    if not question:
        return jsonify({
            "success": False,
            "error": "Please enter a question for the AI Tutor."
        }), 400

    if not video_id or video_id not in TRANSCRIPT_STORE:
        return jsonify({
            "success": False,
            "error": "No active lecture found! Please paste a YouTube lecture link first."
        }), 400

    transcript = TRANSCRIPT_STORE[video_id]

    try:
        answer = answer_tutor_question(transcript, question)
        return jsonify({
            "success": True,
            "video_id": video_id,
            "answer": answer
        })
    except Exception as error:
        print(f"AI Tutor Error: {error}")
        return jsonify({
            "success": False,
            "error": "Something went wrong while consulting the AI Tutor."
        }), 500


@app.route("/test-gemini")
def test_gemini():
    answer = ask_gemini("Reply with exactly: ABHYAS AI GEMINI CONNECTED")
    return answer


if __name__ == "__main__":
    app.run(debug=True)