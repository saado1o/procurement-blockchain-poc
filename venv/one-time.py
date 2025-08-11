from app import db
from models import User
from werkzeug.security import generate_password_hash

admin = User(name="Admin", email="admin@example.com", password=generate_password_hash("admin123"), is_admin=True)
db.session.add(admin)
db.session.commit()
