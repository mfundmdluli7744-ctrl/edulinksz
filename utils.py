from models import TermReport, Student

def get_student_ranking(student_id, term, academic_year):
    """
    Calculates the rank of a student in their class based on total marks.
    Returns (rank, total_students_in_class)
    """
    student = Student.query.get(student_id)
    if not student:
        return None, 0
    
    # Total students in class
    total_in_class = Student.query.filter_by(class_stream_id=student.class_stream_id).count()
    
    # Get all reports for the same class, term, and year, sorted by total_marks
    reports = TermReport.query.join(Student).filter(
        Student.class_stream_id == student.class_stream_id,
        TermReport.term == term,
        TermReport.academic_year == academic_year,
        TermReport.total_marks != None
    ).order_by(TermReport.total_marks.desc()).all()
    
    # Find position
    rank = None
    for i, r in enumerate(reports):
        if r.student_id == student_id:
            rank = i + 1
            break
            
    return rank, total_in_class
