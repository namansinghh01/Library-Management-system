from db import db
from datetime import datetime

class BookRequest(db.Model):
    __tablename__ = 'book_requests'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=True) # If requesting an existing out of stock book
    title = db.Column(db.String(255), nullable=True) # Custom title
    author = db.Column(db.String(255), nullable=True) # Custom author
    request_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False, default='pending') # pending, approved, rejected

    # Relationships
    student = db.relationship('Student', backref=db.backref('requests', lazy=True))
    book = db.relationship('Book', backref=db.backref('book_requests', lazy=True))
