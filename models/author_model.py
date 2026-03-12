from db import db

class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    profile_pic = db.Column(db.String(255), nullable=True, default='default.jpg')

    # Relationships
    books = db.relationship('Book', backref='author', lazy=True, cascade="all, delete-orphan")
