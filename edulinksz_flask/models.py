from extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'Admin', 'Teacher', 'Parent'
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=True)
    is_profile_approved = db.Column(db.Boolean, default=True)
    signature_url = db.Column(db.String(255), nullable=True)

class SchoolProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, default="EduLinkSZ School")
    logo_url = db.Column(db.String(255), nullable=True)
    letterhead_url = db.Column(db.String(255), nullable=True)
    signature_url = db.Column(db.String(255), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(150), nullable=True)
    tel = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    academic_year = db.Column(db.String(50), nullable=True)
    current_term = db.Column(db.String(50), nullable=True)  # Term 1, Term 2, Term 3
    principal_name = db.Column(db.String(150), nullable=True)

class ClassStream(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_level = db.Column(db.Integer, nullable=False)  # 1, 2, 3, 4, 5
    stream = db.Column(db.String(10), nullable=False)  # A, B, C
    class_teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    class_teacher = db.relationship('User', foreign_keys=[class_teacher_id])
    
    def __repr__(self):
        return f"Form {self.form_level}{self.stream}"

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_number = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    class_stream_id = db.Column(db.Integer, db.ForeignKey('class_stream.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    class_stream = db.relationship('ClassStream')
    parent = db.relationship('User', foreign_keys=[parent_id])

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class TeacherSubjectAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    class_stream_id = db.Column(db.Integer, db.ForeignKey('class_stream.id'), nullable=False)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    term = db.Column(db.String(50), nullable=False)
    academic_year = db.Column(db.String(50), nullable=False)
    marks = db.Column(db.Float, nullable=False)
    test1_marks = db.Column(db.Float, nullable=True)
    test2_marks = db.Column(db.Float, nullable=True)
    grade = db.Column(db.String(5), nullable=True)
    teacher_comment = db.Column(db.Text, nullable=True)
    
    student = db.relationship('Student')
    subject = db.relationship('Subject')

class TermReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    term = db.Column(db.String(50), nullable=False)
    academic_year = db.Column(db.String(50), nullable=False)
    class_teacher_remark = db.Column(db.Text, nullable=True)
    principal_remark = db.Column(db.Text, nullable=True)
    overall_performance = db.Column(db.String(100), nullable=True)
    total_marks = db.Column(db.Float, nullable=True)
    is_approved = db.Column(db.Boolean, default=False)
    
    student = db.relationship('Student')

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # e.g., Parent
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
