from app import create_app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    principal = User.query.filter_by(username='principal').first()
    if not principal:
        principal = User(
            username='principal',
            password_hash=generate_password_hash('principal123'),
            role='Principal',
            name='Demo Principal'
        )
        db.session.add(principal)
        db.session.commit()
        print("Principal user created successfully.")
    else:
        print("Principal user already exists.")
    
    # Also verify existing demo users
    print(f"Total Users: {User.query.count()}")
    for u in User.query.all():
        print(f"- {u.username} ({u.role})")
