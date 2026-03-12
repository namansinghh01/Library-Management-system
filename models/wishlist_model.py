from db import db
from datetime import datetime

class Wishlist(db.Model):
    __tablename__ = 'wishlists'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    added_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    student = db.relationship('Student', backref=db.backref('wishlists', lazy=True, cascade="all, delete-orphan"))
    book = db.relationship('Book', backref=db.backref('wishlisted_by', lazy=True, cascade="all, delete-orphan"))
