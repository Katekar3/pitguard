from app import app
from extensions import db
from models import User

with app.app_context():
    u = User(username='admin1', role='admin')
    u.set_password('test1234')
    db.session.add(u)
    db.session.commit()
    print("User created")