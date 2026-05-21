from app import create_app
from extensions import db
from models import Student, TermReport, SchoolProfile
from utils import get_student_ranking
import json

app = create_app()

with app.app_context():
    school = SchoolProfile.query.first()
    if not school:
        print("No school profile found.")
    else:
        term = school.current_term
        year = school.academic_year
        print(f"DEBUG: School={school.name}, Term={term}, Year={year}")
        
        results_data = []
        students = Student.query.all()
        for s in students:
            rank, total = get_student_ranking(s.id, term, year)
            report = TermReport.query.filter_by(student_id=s.id, term=term, academic_year=year).first()
            avg = report.total_marks if report else None
            results_data.append({
                'id': s.id,
                'name': f"{s.first_name} {s.last_name}",
                'class': s.class_stream_id,
                'avg': avg,
                'rank': rank,
                'total': total
            })
            
        print(json.dumps(results_data, indent=4))
