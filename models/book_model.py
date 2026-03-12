from db import db

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    isbn = db.Column(db.String(50), nullable=False, unique=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    total_copies = db.Column(db.Integer, nullable=False, default=1)
    available_copies = db.Column(db.Integer, nullable=False, default=1)
    category = db.Column(db.String(100), nullable=True)

    # Relationships
    transactions = db.relationship('Transaction', backref='book', lazy=True, cascade="all, delete-orphan")
