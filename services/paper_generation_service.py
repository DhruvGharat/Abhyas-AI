import os
from typing import Optional
from dotenv import load_dotenv
from google import genai
from models.exam_models import Syllabus, PYQAnalysis, ExamBlueprint, PracticePaperSet

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing. Please add it to your .env file.")

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-3.6-flash"


def generate_practice_papers(
    syllabus: Syllabus,
    pyq_analysis: PYQAnalysis,
    blueprint: ExamBlueprint,
    custom_instructions: Optional[str] = ""
) -> PracticePaperSet:
    """
    Generate two distinct, high-quality practice examination papers (Practice Paper 1 and Practice Paper 2)
    following the Exam Blueprint, Syllabus, and PYQ analysis patterns.
    """
    syllabus_summary = syllabus.model_dump_json(indent=2)
    pyq_summary = pyq_analysis.model_dump_json(indent=2)
    blueprint_summary = blueprint.model_dump_json(indent=2)

    prompt = f"""
You are an experienced university examination paper setter.

Your task is to draft TWO COMPLETE AND DISTINCT practice examination papers (Practice Paper 1 - Set A, and Practice Paper 2 - Set B) based on the provided Exam Blueprint, Syllabus, and PYQ Analysis.

STRICT RULES & REQUIREMENTS:
1. BOTH papers must strictly follow the Exam Blueprint:
   - Total Marks for Paper 1 MUST be exactly {blueprint.total_marks}.
   - Total Marks for Paper 2 MUST be exactly {blueprint.total_marks}.
   - Questions MUST cover ONLY the selected modules: {blueprint.selected_modules}.
2. PAPER 1 AND PAPER 2 MUST BE DISTINCT:
   - Do NOT duplicate questions between Paper 1 and Paper 2.
   - Use different subtopics, scenarios, and question formulations.
3. FOLLOW HISTORICAL PATTERNS:
   - Incorporate real exam phrasing (e.g. "Explain with neat diagram", "Compare and contrast", "Derive", "Solve").
4. STRUCTURE:
   - Organize into clean sections (e.g. Section A: Short Answer Questions, Section B: Descriptive / Analytical Questions).
   - Ensure every question has explicit marks and a brief solution hint.

Syllabus Reference:
-------------------
{syllabus_summary}

PYQ Analysis & Question Patterns:
---------------------------------
{pyq_summary}

Exam Blueprint:
---------------
{blueprint_summary}

Additional User Instructions:
{custom_instructions if custom_instructions else "None"}
"""

    interaction = client.interactions.create(
        model=MODEL_NAME,
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": PracticePaperSet.model_json_schema()
        }
    )

    paper_set = PracticePaperSet.model_validate_json(interaction.output_text)
    return paper_set
