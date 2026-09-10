import os
from dotenv import load_dotenv
from google import genai
from models.exam_models import Syllabus

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing. Please add it to your .env file.")

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-3.6-flash"


def parse_syllabus(syllabus_text: str) -> Syllabus:
    """
    Parse raw syllabus text into a structured Syllabus Pydantic model using Gemini.
    """
    if not syllabus_text or not syllabus_text.strip():
        raise ValueError("Syllabus text cannot be empty.")

    prompt = f"""
You are an expert academic curriculum parser for university engineering and college subjects.

Analyze the raw syllabus content provided below and extract all modules and subtopics into a structured format.

Instructions:
1. Identify the subject name if present.
2. Group content clearly into modules (e.g. "Module 1", "Module 2", etc.).
3. Under each module, list all core concepts, topics, and subtopics.
4. Ensure no important topics from the raw text are missed.

Raw Syllabus Content:
---------------------
{syllabus_text}
---------------------
"""

    interaction = client.interactions.create(
        model=MODEL_NAME,
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": Syllabus.model_json_schema()
        }
    )

    syllabus = Syllabus.model_validate_json(interaction.output_text)
    return syllabus
