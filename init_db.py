from app import app
from models import db

def init_db():
    with app.app_context():
        print("Initializing database...")
        db.create_all()
        print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
