from db import db
from datetime import datetime

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False) # 1 to 5
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    student = db.relationship('Student', backref=db.backref('reviews', lazy=True, cascade="all, delete-orphan"))
    book = db.relationship('Book', backref=db.backref('reviews', lazy=True, cascade="all, delete-orphan"))
