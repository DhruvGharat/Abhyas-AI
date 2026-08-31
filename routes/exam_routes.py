from flask import Blueprint, render_template

exam_bp = Blueprint('exam', __name__, url_prefix='/exam')

@exam_bp.route('/')
def exam_index():
    return render_template('exam/exam.html')

@exam_bp.route('/upload')
def upload_pyq():
    return render_template('exam/upload.html')

@exam_bp.route('/papers')
def papers():
    return render_template('exam/papers.html')
