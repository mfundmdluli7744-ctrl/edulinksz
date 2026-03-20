from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import ClassStream, Subject, Student, Result, SchoolProfile
from extensions import db
import os
from werkzeug.utils import secure_filename

teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.before_request
@login_required
def require_teacher():
    if current_user.role != 'Teacher':
        return "Unauthorized", 403

@teacher_bp.route('/')
@teacher_bp.route('/dashboard')
def dashboard():
    from models import TeacherSubjectAssignment
    # Classes where this teacher is a class teacher
    managed_classes = ClassStream.query.filter_by(class_teacher_id=current_user.id).all()
    managed_class_ids = [c.id for c in managed_classes]
    
    # Subjects assigned to this teacher
    assignments = TeacherSubjectAssignment.query.filter_by(teacher_id=current_user.id).all()
    assigned_class_ids = list(set([a.class_stream_id for a in assignments]))
    
    # All unique class IDs relevant to this teacher
    all_class_ids = list(set(managed_class_ids + assigned_class_ids))
    
    student_count = Student.query.filter(Student.class_stream_id.in_(all_class_ids)).count() if all_class_ids else 0
    subject_count = len(assignments)
    
    return render_template('teacher/dashboard.html', 
                           student_count=student_count, 
                           subject_count=subject_count,
                           managed_classes=managed_classes)

@teacher_bp.route('/classes')
def my_classes():
    classes = ClassStream.query.order_by(ClassStream.form_level, ClassStream.stream).all()
    subjects = Subject.query.order_by(Subject.name).all()
    school = SchoolProfile.query.first()
    return render_template('teacher/classes.html', classes=classes, subjects=subjects, school=school)

@teacher_bp.route('/enter_marks/<int:class_id>/<int:subject_id>', methods=['GET', 'POST'])
def enter_marks(class_id, subject_id):
    c_stream = ClassStream.query.get_or_404(class_id)
    subject = Subject.query.get_or_404(subject_id)
    school = SchoolProfile.query.first()
    
    term = school.current_term if school else 'Term 1'
    year = school.academic_year if school else '2026'
    
    students = Student.query.filter_by(class_stream_id=c_stream.id).order_by(Student.last_name).all()
    
    if request.method == 'POST':
        for student in students:
            marks_t1_str = request.form.get(f'test1_{student.id}')
            marks_t2_str = request.form.get(f'test2_{student.id}')
            grade = request.form.get(f'grade_{student.id}')
            comment = request.form.get(f'comment_{student.id}')
            
            if marks_t1_str or marks_t2_str:
                try:
                    t1 = float(marks_t1_str) if marks_t1_str else 0.0
                    t2 = float(marks_t2_str) if marks_t2_str else 0.0
                    marks = (t1 + t2) / 2
                    
                    res = Result.query.filter_by(student_id=student.id, subject_id=subject.id, term=term, academic_year=year).first()
                    if res:
                        res.test1_marks = t1
                        res.test2_marks = t2
                        res.marks = marks
                        res.grade = grade
                        res.teacher_comment = comment
                        res.teacher_id = current_user.id
                    else:
                        new_res = Result(
                            student_id=student.id,
                            subject_id=subject.id,
                            teacher_id=current_user.id,
                            term=term,
                            academic_year=year,
                            test1_marks=t1,
                            test2_marks=t2,
                            marks=marks,
                            grade=grade,
                            teacher_comment=comment
                        )
                        db.session.add(new_res)
                except ValueError:
                    pass
                    
        db.session.commit()
        flash(f'Marks saved successfully for {subject.name}, Form {c_stream.form_level}{c_stream.stream} ({term}, {year}).', 'success')
        return redirect(url_for('teacher.enter_marks', class_id=class_id, subject_id=subject_id))

    existing_results = {r.student_id: r for r in Result.query.filter_by(subject_id=subject.id, term=term, academic_year=year).all()}
    
    existing_results = {r.student_id: r for r in Result.query.filter_by(subject_id=subject.id, term=term, academic_year=year).all()}
    
    return render_template('teacher/enter_marks.html', c_stream=c_stream, subject=subject, students=students, existing_results=existing_results, term=term, year=year)

@teacher_bp.route('/class_remarks/<int:class_id>', methods=['GET', 'POST'])
def class_remarks(class_id):
    from models import TermReport
    c_stream = ClassStream.query.get_or_404(class_id)
    
    # Check if current user is the class teacher
    managed_classes = ClassStream.query.filter_by(class_teacher_id=current_user.id).all()
    if c_stream.class_teacher_id != current_user.id:
        flash("Unauthorized: You are not assigned as the class teacher for this class.", "danger")
        return redirect(url_for('teacher.my_classes'))
        
    school = SchoolProfile.query.first()
    term = school.current_term if school else 'Term 1'
    year = school.academic_year if school else '2026'
    
    students = Student.query.filter_by(class_stream_id=c_stream.id).order_by(Student.last_name).all()
    
    if request.method == 'POST':
        for student in students:
            remark = request.form.get(f'remark_{student.id}')
            
            # Calculate overall average for performance logic
            results = Result.query.filter_by(student_id=student.id, term=term, academic_year=year).all()
            if results:
                avg = sum(r.marks for r in results) / len(results)
                
                # Logic: 50+ Pass, 45-49 Promoted, <45 Fail
                if avg >= 50:
                    status = "Pass"
                elif 45 <= avg < 50:
                    status = "Promoted"
                else:
                    status = "Fail"
                    
                report = TermReport.query.filter_by(student_id=student.id, term=term, academic_year=year).first()
                if not report:
                    report = TermReport(student_id=student.id, term=term, academic_year=year)
                    db.session.add(report)
                
                report.class_teacher_remark = remark
                report.overall_performance = status
                report.total_marks = round(avg, 2)
            else:
                # If no marks, we can still save the remark
                report = TermReport.query.filter_by(student_id=student.id, term=term, academic_year=year).first()
                if not report:
                    report = TermReport(student_id=student.id, term=term, academic_year=year)
                    db.session.add(report)
                report.class_teacher_remark = remark
                
        db.session.commit()
        flash(f'Class Teacher Remarks for Form {c_stream.form_level}{c_stream.stream} saved.', 'success')
        return redirect(url_for('teacher.class_remarks', class_id=class_id))
        
    status_data = {}
    for student in students:
        results = Result.query.filter_by(student_id=student.id, term=term, academic_year=year).all()
        report = TermReport.query.filter_by(student_id=student.id, term=term, academic_year=year).first()
        
        avg_display = 'N/A'
        calc_status = 'No Results'
        
        if results:
            avg = sum(r.marks for r in results) / len(results)
            avg_display = round(avg, 2)
            if avg >= 50:
                calc_status = "Pass"
            elif 45 <= avg < 50:
                calc_status = "Promoted"
            else:
                calc_status = "Fail"
                
        from utils import get_student_ranking
        rank, total_students = get_student_ranking(student.id, term, year)
        
        status_data[student.id] = {
            'avg': avg_display,
            'calc_status': calc_status,
            'remark': report.class_teacher_remark if report else '',
            'rank': rank,
            'total_students': total_students
        }
        
    return render_template('teacher/class_remarks.html', c_stream=c_stream, students=students, status_data=status_data, term=term, year=year)

@teacher_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        # Update Name
        new_name = request.form.get('name')
        if new_name:
            current_user.name = new_name
            
        # Update Signature
        file = request.files.get('signature')
        if file and file.filename:
            filename = secure_filename(f"sig_teacher_{current_user.id}_{file.filename}")
            upload_folder = os.path.join('static', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            current_user.signature_url = f'uploads/{filename}'
            
        current_user.is_profile_approved = False
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('teacher.profile'))
        
    return render_template('teacher/profile.html')

