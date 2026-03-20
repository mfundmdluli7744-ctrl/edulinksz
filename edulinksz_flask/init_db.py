from app import create_app
from extensions import db
from models import User, SchoolProfile, ClassStream, Subject, Student, Result, TermReport
from werkzeug.security import generate_password_hash

def init_db():
    app = create_app()
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        # Create initial admin if not exists
        if not User.query.filter_by(username='admin').first():
            print("Seeding initial admin user...")
            initial_admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                role='Admin',
                name='System Administrator'
            )
            db.session.add(initial_admin)
            db.session.commit()
            
            
            # --- Cleanup of old demo data ---
            demo_usernames = ['teacher', 'parent', 'principal']
            for d_uname in demo_usernames:
                d_user = User.query.filter_by(username=d_uname).first()
                if d_user:
                    print(f"Removing legacy demo user: {d_uname}")
                    db.session.delete(d_user)
            db.session.commit()
            
            # --- Seeding of demo data removed as per user request ---
            pass
            
        # Create initial school profile if not exists
        if not SchoolProfile.query.first():
            print("Seeding initial school profile...")
            profile = SchoolProfile(
                name='EduLinkSZ Secondary School',
                academic_year='2026',
                current_term='Term 1',
                address='Mbabane, Eswatini'
            )
            db.session.add(profile)
            db.session.commit()
            
        print("Database initialization complete.")

if __name__ == '__main__':
    try:
        init_db()
    except Exception as e:
        print(f"Error during database initialization: {e}")
        # We don't exit with non-zero here so that Gunicorn can still try to start
