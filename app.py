from flask import Flask, render_template

from services.gemini_service import ask_gemini


app = Flask(__name__)


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/learn")
def learn():

    return render_template("learning/learn.html")


@app.route("/process-youtube", methods=["POST"])
def process_youtube():

    from flask import request, jsonify

    from services.youtube_service import extract_video_id
    from services.transcript_service import get_transcript
    from services.quiz_service import generate_quiz


    # ---------------------------------
    # Get YouTube URL
    # ---------------------------------

    data = request.get_json()

    youtube_url = data.get("url", "").strip()


    if not youtube_url:

        return jsonify({
            "success": False,
            "error": "Please enter a YouTube URL."
        }), 400


    # ---------------------------------
    # Extract Video ID
    # ---------------------------------

    video_id = extract_video_id(
        youtube_url
    )


    if not video_id:

        return jsonify({
            "success": False,
            "error": "Invalid YouTube URL."
        }), 400


    # ---------------------------------
    # Get Transcript
    # ---------------------------------

    transcript = get_transcript(
        video_id
    )


    if not transcript:

        return jsonify({
            "success": False,
            "error": (
                "Could not retrieve the transcript "
                "for this video."
            )
        }), 400


    # ---------------------------------
    # Generate Quiz
    # ---------------------------------

    try:

        quiz = generate_quiz(
            transcript
        )

    except Exception as error:

        print(
            f"Quiz generation error: {error}"
        )

        return jsonify({
            "success": False,
            "error": (
                "Something went wrong while "
                "generating the quiz."
            )
        }), 500


    # ---------------------------------
    # Convert Quiz to JSON
    # ---------------------------------

    return jsonify({

        "success": True,

        "video_id": video_id,

        "quiz": quiz.model_dump()

    })

@app.route("/test-gemini")
def test_gemini():

    answer = ask_gemini(
        "Reply with exactly: ABHYAS AI GEMINI CONNECTED"
    )

    return answer


if __name__ == "__main__":
    app.run(debug=True)