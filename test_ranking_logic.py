from app import create_app
from extensions import db
from models import Student, Result, TermReport, SchoolProfile, Subject
from utils import get_student_ranking

app = create_app()

with app.app_context():
    school = SchoolProfile.query.first()
    term = school.current_term
    year = school.academic_year
    
    # Get a student to copy their class
    original_s = Student.query.first()
    
    # Create test student 2 (should be rank 2)
    test_s2 = Student(
        student_number="TEST-002",
        first_name="Lower",
        last_name="Student",
        class_stream_id=original_s.class_stream_id
    )
    db.session.add(test_s2)
    db.session.flush()
    
    report2 = TermReport(
        student_id=test_s2.id,
        term=term,
        academic_year=year,
        total_marks=50.0  # Lower than original's ~67
    )
    db.session.add(report2)
    
    # Create test student 3 (should be rank 1 if I give them 90)
    test_s3 = Student(
        student_number="TEST-003",
        first_name="Higher",
        last_name="Student",
        class_stream_id=original_s.class_stream_id
    )
    db.session.add(test_s3)
    db.session.flush()
    
    report3 = TermReport(
        student_id=test_s3.id,
        term=term,
        academic_year=year,
        total_marks=90.0
    )
    db.session.add(report3)
    
    db.session.commit()
    
    print(f"Original Student Rank: {get_student_ranking(original_s.id, term, year)}")
    print(f"Higher Student Rank: {get_student_ranking(test_s3.id, term, year)}")
    print(f"Lower Student Rank: {get_student_ranking(test_s2.id, term, year)}")
    
    # Cleanup
    db.session.delete(report2)
    db.session.delete(report3)
    db.session.delete(test_s2)
    db.session.delete(test_s3)
    db.session.commit()
