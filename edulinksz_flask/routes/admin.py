from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from models import SchoolProfile, ClassStream, Subject, User, Student, Result, TermReport, TeacherSubjectAssignment, Notification
from extensions import db
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import os

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@login_required
def require_admin():
    if current_user.role != 'Admin':
        return "Unauthorized", 403

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_bp.route('/dashboard')
def dashboard():
    student_count = Student.query.count()
    teacher_count = User.query.filter_by(role='Teacher').count()
    class_count = ClassStream.query.count()
    subject_count = Subject.query.count()
    school = SchoolProfile.query.first()
    pending_approvals = User.query.filter_by(role='Teacher', is_profile_approved=False).count()
    return render_template('admin/dashboard.html', 
                           student_count=student_count, 
                           teacher_count=teacher_count,
                           class_count=class_count,
                           subject_count=subject_count,
                           school=school,
                           pending_approvals=pending_approvals)

@admin_bp.route('/classes', methods=['GET', 'POST'])
def manage_classes():
    if request.method == 'POST':
        form_level = request.form.get('form_level')
        stream = request.form.get('stream').upper().strip()
        
        existing = ClassStream.query.filter_by(form_level=form_level, stream=stream).first()
        if existing:
            flash(f"Form {form_level}{stream} already exists!", "danger")
        else:
            new_class = ClassStream(form_level=int(form_level), stream=stream)
            db.session.add(new_class)
            db.session.commit()
            flash(f"Class Form {form_level}{stream} created successfully.", "success")
        return redirect(url_for('admin.manage_classes'))
        
    classes = ClassStream.query.order_by(ClassStream.form_level, ClassStream.stream).all()
    teachers = User.query.filter_by(role='Teacher').order_by(User.name).all()
    return render_template('admin/classes.html', classes=classes, teachers=teachers)

@admin_bp.route('/assign_class_teacher/<int:class_id>', methods=['POST'])
def assign_class_teacher(class_id):
    c_stream = ClassStream.query.get_or_404(class_id)
    teacher_id = request.form.get('teacher_id')
    
    if teacher_id:
        c_stream.class_teacher_id = int(teacher_id)
    else:
        c_stream.class_teacher_id = None
        
    db.session.commit()
    flash(f"Class teacher updated for Form {c_stream.form_level}{c_stream.stream}.", "success")
    return redirect(url_for('admin.manage_classes'))

@admin_bp.route('/subjects', methods=['GET', 'POST'])
def manage_subjects():
    if request.method == 'POST':
        name = request.form.get('name').strip()
        
        existing = Subject.query.filter_by(name=name).first()
        if existing:
            flash(f"Subject '{name}' already exists!", "danger")
        else:
            new_subject = Subject(name=name)
            db.session.add(new_subject)
            db.session.commit()
            flash(f"Subject '{name}' added successfully.", "success")
        return redirect(url_for('admin.manage_subjects'))
        
    subjects = Subject.query.order_by(Subject.name).all()
    return render_template('admin/subjects.html', subjects=subjects)

@admin_bp.route('/teachers', methods=['GET', 'POST'])
def manage_teachers():
    if request.method == 'POST':
        name = request.form.get('name').strip()
        username = request.form.get('username').strip()
        password = request.form.get('password')
        email = request.form.get('email').strip()
        
        if User.query.filter_by(username=username).first():
            flash(f"Username '{username}' is already taken.", "danger")
        else:
            new_teacher = User(name=name, username=username, password_hash=generate_password_hash(password), role='Teacher', email=email)
            db.session.add(new_teacher)
            db.session.commit()
            flash(f"Teacher '{name}' registered successfully.", "success")
        return redirect(url_for('admin.manage_teachers'))
        
    teachers = User.query.filter_by(role='Teacher').order_by(User.name).all()
    return render_template('admin/teachers.html', teachers=teachers)

@admin_bp.route('/parents', methods=['GET', 'POST'])
def manage_parents():
    if request.method == 'POST':
        name = request.form.get('name').strip()
        username = request.form.get('username').strip()
        password = request.form.get('password')
        email = request.form.get('email').strip()
        
        if User.query.filter_by(username=username).first():
            flash(f"Username '{username}' is already taken.", "danger")
        else:
            new_parent = User(name=name, username=username, password_hash=generate_password_hash(password), role='Parent', email=email)
            db.session.add(new_parent)
            db.session.commit()
            flash(f"Parent '{name}' registered successfully.", "success")
        return redirect(url_for('admin.manage_parents'))
        
    parents = User.query.filter_by(role='Parent').order_by(User.name).all()
    return render_template('admin/parents.html', parents=parents)

@admin_bp.route('/students', methods=['GET', 'POST'])
def manage_students():
    if request.method == 'POST':
        student_number = request.form.get('student_number').strip().upper()
        first_name = request.form.get('first_name').strip()
        last_name = request.form.get('last_name').strip()
        class_stream_id = request.form.get('class_stream_id')
        parent_id = request.form.get('parent_id') or None
        
        if Student.query.filter_by(student_number=student_number).first():
            flash(f"Student ID '{student_number}' already exists.", "danger")
        else:
            new_student = Student(
                student_number=student_number,
                first_name=first_name,
                last_name=last_name,
                class_stream_id=class_stream_id,
                parent_id=parent_id
            )
            db.session.add(new_student)
            db.session.commit()
            flash(f"Student '{first_name} {last_name}' enrolled successfully.", "success")
        return redirect(url_for('admin.manage_students'))
        
    students = Student.query.order_by(Student.last_name, Student.first_name).all()
    classes = ClassStream.query.order_by(ClassStream.form_level, ClassStream.stream).all()
    parents = User.query.filter_by(role='Parent').order_by(User.name).all()
    return render_template('admin/students.html', students=students, classes=classes, parents=parents)

@admin_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    profile = SchoolProfile.query.first()
    if not profile:
        profile = SchoolProfile(name="EduLinkSZ School", current_term="Term 1", academic_year="2026")
        db.session.add(profile)
        db.session.commit()
        
    if request.method == 'POST':
        profile.name = request.form.get('name')
        profile.address = request.form.get('address')
        profile.email = request.form.get('email')
        profile.tel = request.form.get('tel')
        profile.phone = request.form.get('phone')
        profile.academic_year = request.form.get('academic_year')
        profile.current_term = request.form.get('current_term')
        profile.principal_name = request.form.get('principal_name')
        
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        letterhead = request.files.get('letterhead')
        if letterhead and letterhead.filename:
            filename = secure_filename(letterhead.filename)
            letterhead.save(os.path.join(upload_folder, filename))
            profile.letterhead_url = f'uploads/{filename}'
            
        signature = request.files.get('signature')
        if signature and signature.filename:
            filename = secure_filename(signature.filename)
            signature.save(os.path.join(upload_folder, filename))
            profile.signature_url = f'uploads/{filename}'
        
        db.session.commit()
        flash('School profile successfully updated!', 'success')
        return redirect(url_for('admin.settings'))
        
    return render_template('admin/settings.html', profile=profile)

@admin_bp.route('/broadcast_results', methods=['POST'])
def broadcast_results():
    parents = User.query.filter_by(role='Parent').all()
    parents_with_email = [p for p in parents if p.email]
    
    if not parents_with_email:
        flash("No parents with email addresses found.", "warning")
        return redirect(url_for('admin.dashboard'))
        
    # Logic to send email
    # For now, we simulate sending and log it
    import datetime
    log_dir = os.path.join(current_app.root_path, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, 'email_broadcasts.log')
    
    message = "Dear Parent, academic results for the current term have been published on the EduLinkSZ Portal. Please log in to view your child's report card."
    
    with open(log_path, 'a') as f:
        f.write(f"\n--- {datetime.datetime.now()} ---\n")
        f.write(f"Subject: Academic Results Published\n")
        f.write(f"Message: {message}\n")
        f.write(f"Recipients: {', '.join([p.email for p in parents_with_email])}\n")
        
    flash(f"Broadcast message sent successfully to {len(parents_with_email)} parents.", "success")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/approve_teacher/<int:teacher_id>', methods=['POST'])
def approve_teacher(teacher_id):
    teacher = User.query.get_or_404(teacher_id)
    if teacher.role != 'Teacher':
        flash("Invalid user role.", "danger")
        return redirect(url_for('admin.manage_teachers'))
        
    teacher.is_profile_approved = True
    db.session.commit()
    flash(f"Profile for {teacher.name} has been approved.", "success")
    return redirect(request.referrer or url_for('admin.manage_teachers'))

@admin_bp.route('/users/change-password/<int:user_id>', methods=['POST'])
def change_user_password(user_id):
    user = User.query.get_or_404(user_id)
    new_password = request.form.get('new_password')
    
    if not new_password:
        flash("Password cannot be empty.", "danger")
    else:
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash(f"Password for {user.name} has been updated successfully.", "success")
        
    return redirect(request.referrer or url_for('admin.dashboard'))

@admin_bp.route('/profile/change-password', methods=['GET', 'POST'])
def change_own_password():
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not new_password:
            flash("Password cannot be empty.", "danger")
        elif new_password != confirm_password:
            flash("Passwords do not match.", "danger")
        else:
            current_user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            flash("Your password has been updated successfully.", "success")
            return redirect(url_for('admin.dashboard'))
            
    return render_template('admin/change_password.html')

@admin_bp.route('/delete_teacher/<int:teacher_id>', methods=['POST'])
def delete_teacher(teacher_id):
    teacher = User.query.get_or_404(teacher_id)
    if teacher.role != 'Teacher':
        flash("Invalid user role.", "danger")
        return redirect(url_for('admin.manage_teachers'))
    
    # Unlink from classes
    classes = ClassStream.query.filter_by(class_teacher_id=teacher_id).all()
    for c in classes:
        c.class_teacher_id = None
        
    # Delete subject assignments
    TeacherSubjectAssignment.query.filter_by(teacher_id=teacher_id).delete()
    
    # Unlink from results
    Result.query.filter_by(teacher_id=teacher_id).update({Result.teacher_id: None})
    
    db.session.delete(teacher)
    db.session.commit()
    flash(f"Teacher {teacher.name} has been deleted.", "success")
    return redirect(url_for('admin.manage_teachers'))

@admin_bp.route('/delete_parent/<int:parent_id>', methods=['POST'])
def delete_parent(parent_id):
    parent = User.query.get_or_404(parent_id)
    if parent.role != 'Parent':
        flash("Invalid user role.", "danger")
        return redirect(url_for('admin.manage_parents'))
        
    # Unlink from students
    Student.query.filter_by(parent_id=parent_id).update({Student.parent_id: None})
    
    # Delete notifications
    Notification.query.filter_by(user_id=parent_id).delete()
    
    db.session.delete(parent)
    db.session.commit()
    flash(f"Parent {parent.name} has been deleted.", "success")
    return redirect(url_for('admin.manage_parents'))

@admin_bp.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    
    # Delete results
    Result.query.filter_by(student_id=student_id).delete()
    
    # Delete term reports
    TermReport.query.filter_by(student_id=student_id).delete()
    
    db.session.delete(student)
    db.session.commit()
    flash(f"Student {student.first_name} {student.last_name} has been deleted.", "success")
    return redirect(url_for('admin.manage_students'))
