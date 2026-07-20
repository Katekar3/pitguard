from app import app, db
from models import Worker

with app.app_context():
    print(Worker.query.all())