from typing import List
from models.exam_models import Syllabus, PYQAnalysis
from services.gemini_service import call_gemini_with_retry


def analyze_pyqs(pyq_texts: List[str], syllabus: Syllabus) -> PYQAnalysis:
    """
    Analyze previous year question papers against the structured syllabus context
    to extract topics, question patterns, weightages, and difficulty levels.
    """
    if not pyq_texts:
        raise ValueError("At least one previous year paper text must be provided.")

    combined_pyqs = "\n\n=== NEXT QUESTION PAPER ===\n\n".join(pyq_texts)
    syllabus_summary = syllabus.model_dump_json(indent=2)

    prompt = f"""
You are an expert university examiner analyzing past year question papers (PYQs).

Your goal is to perform a detailed structural analysis of the past year papers using the provided Syllabus as reference.

Instructions:
1. Extract questions from the past papers.
2. For each question, map it to the exact Module and Topic from the provided Syllabus.
3. Identify question marks, question type (e.g. Short Answer, Descriptive, Numerical, Diagram-based), and difficulty (Easy, Medium, Hard).
4. Calculate estimated weightage (%) for each module based on marks assigned.
5. Identify recurring / frequently asked topics.
6. Identify key exam question patterns (e.g. "Explain with neat sketch", "Differentiate between X and Y", "Solve numerical on Z").

Syllabus Reference:
-------------------
{syllabus_summary}
-------------------

Past Year Question Papers (PYQs):
---------------------------------
{combined_pyqs}
---------------------------------
"""

    response_text = call_gemini_with_retry(
        prompt=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": PYQAnalysis.model_json_schema()
        }
    )

    pyq_analysis = PYQAnalysis.model_validate_json(response_text)
    return pyq_analysis
