from typing import List, Optional
from models.exam_models import Syllabus, PYQAnalysis, ExamBlueprint
from services.gemini_service import call_gemini_with_retry


def create_exam_blueprint(
    syllabus: Syllabus,
    pyq_analysis: PYQAnalysis,
    paper_type: str,
    total_marks: int,
    selected_modules: List[str],
    custom_instructions: Optional[str] = ""
) -> ExamBlueprint:
    """
    Construct an Exam Blueprint mapping out question specifications, target modules,
    marks per question, and difficulty levels based on Syllabus, PYQ analysis, and user constraints.
    """
    syllabus_summary = syllabus.model_dump_json(indent=2)
    pyq_summary = pyq_analysis.model_dump_json(indent=2)

    prompt = f"""
You are an examination controller creating an official EXAM BLUEPRINT for a university paper.

User Requirements:
- Paper Type: {paper_type}
- Total Marks: {total_marks}
- Selected Modules: {", ".join(selected_modules) if selected_modules else "All Modules"}
- Custom Instructions: {custom_instructions if custom_instructions else "None"}

Context Data:
Syllabus:
{syllabus_summary}

PYQ Analysis & Historical Patterns:
{pyq_summary}

Instructions:
1. Create a question specification list where the SUM OF ALL MARKS EXACTLY EQUALS {total_marks}.
2. Ensure questions ONLY cover the selected modules: {selected_modules}.
3. Balance question types (e.g. short 2-5 mark questions, long 10 mark analytical questions as appropriate for a {total_marks}-mark paper).
4. Allocate question weights based on historical topic importance from the PYQ analysis.
5. Create a realistic balance of Easy, Medium, and Hard difficulty questions.

Generate the blueprint adhering strictly to the schema.
"""

    response_text = call_gemini_with_retry(
        prompt=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": ExamBlueprint.model_json_schema()
        }
    )

    blueprint = ExamBlueprint.model_validate_json(response_text)
    return blueprint
