from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import SchoolProfile, ClassStream, Student, TermReport, Result, User
from extensions import db

principal_bp = Blueprint('principal', __name__)

@principal_bp.before_request
@login_required
def require_principal():
    # Admin is allowed to act as Principal for convenience
    if current_user.role != 'Principal' and current_user.role != 'Admin':
        return "Unauthorized", 403

@principal_bp.route('/')
@principal_bp.route('/dashboard')
def dashboard():
    classes = ClassStream.query.order_by(ClassStream.form_level, ClassStream.stream).all()
    school = SchoolProfile.query.first()
    return render_template('principal/dashboard.html', classes=classes, school=school)

@principal_bp.route('/class/<int:class_id>')
def class_view(class_id):
    c_stream = ClassStream.query.get_or_404(class_id)
    students = Student.query.filter_by(class_stream_id=class_id).all()
    school = SchoolProfile.query.first()
    term = school.current_term if school else 'Term 1'
    year = school.academic_year if school else '2026'
    
    # Get reports for these students
    reports = {r.student_id: r for r in TermReport.query.filter_by(term=term, academic_year=year).all()}
    
    return render_template('principal/class_view.html', c_stream=c_stream, students=students, reports=reports, term=term, year=year)

@principal_bp.route('/approve/<int:student_id>', methods=['GET', 'POST'])
def approve_report(student_id):
    student = Student.query.get_or_404(student_id)
    school = SchoolProfile.query.first()
    term = school.current_term if school else 'Term 1'
    year = school.academic_year if school else '2026'
    
    report = TermReport.query.filter_by(student_id=student_id, term=term, academic_year=year).first()
    if not report:
        report = TermReport(student_id=student_id, term=term, academic_year=year)
        db.session.add(report)
        
    results = Result.query.filter_by(student_id=student_id, term=term, academic_year=year).all()
    
    if request.method == 'POST':
        remark = request.form.get('principal_remark')
        is_approved = 'is_approved' in request.form
        
        report.principal_remark = remark
        report.is_approved = is_approved
        db.session.commit()
        flash(f"Report for {student.first_name} {student.last_name} has been {'approved' if is_approved else 'updated'}.", "success")
        return redirect(url_for('principal.class_view', class_id=student.class_stream_id))
        
    from utils import get_student_ranking
    rank, total_students = get_student_ranking(student_id, term, year)
    
    return render_template('principal/approve.html', student=student, report=report, results=results, school=school, term=term, year=year, rank=rank, total_students=total_students)
