from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from models import Student, Result, TermReport, SchoolProfile

parent_bp = Blueprint('parent', __name__)

@parent_bp.before_request
@login_required
def require_parent():
    if current_user.role != 'Parent':
        return "Unauthorized", 403

@parent_bp.route('/')
@parent_bp.route('/dashboard')
def dashboard():
    students = Student.query.filter_by(parent_id=current_user.id).all()
    return render_template('parent/dashboard.html', students=students)

@parent_bp.route('/report/<int:student_id>')
def view_report(student_id):
    student = Student.query.get_or_404(student_id)
    if student.parent_id != current_user.id:
        abort(403)
        
    school = SchoolProfile.query.first()
    
    term_report = None
    results = []
    
    if school:
        term_report = TermReport.query.filter_by(student_id=student.id, term=school.current_term, academic_year=school.academic_year).first()
        results = Result.query.filter_by(student_id=student.id, term=school.current_term, academic_year=school.academic_year).all()
        
    from datetime import datetime
    from utils import get_student_ranking
    rank, total_students = get_student_ranking(student.id, school.current_term, school.academic_year)
    
    return render_template('parent/report.html', student=student, results=results, term_report=term_report, school=school, datetime=datetime, rank=rank, total_students=total_students)
