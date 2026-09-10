from typing import Optional
from models.exam_models import Syllabus, PYQAnalysis, ExamBlueprint, PracticePaperSet
from services.gemini_service import call_gemini_with_retry


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

    response_text = call_gemini_with_retry(
        prompt=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": PracticePaperSet.model_json_schema()
        }
    )

    paper_set = PracticePaperSet.model_validate_json(response_text)
    return paper_set
