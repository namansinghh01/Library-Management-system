from db import db
from datetime import datetime, timedelta

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    issue_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), nullable=False, default='issued') # "issued" or "returned"

    @property
    def due_date_calc(self):
        if self.issue_date:
            return self.issue_date + timedelta(days=7)
        return None

    @property
    def is_overdue(self):
        if self.status == 'returned' or not self.issue_date:
            return False
        # Calculate due date: 7 days after issue date
        due_date = self.due_date_calc
        return datetime.utcnow() > due_date

    @property
    def calculate_fine(self):
        # 10 rupees per day if late
        if not self.is_overdue or not self.issue_date:
            return 0
        due_date = self.due_date_calc
        if self.status == 'returned' and self.return_date:
            overdue_days = (self.return_date - due_date).days
        else:
            overdue_days = (datetime.utcnow() - due_date).days
        return max(0, overdue_days * 10)
        return max(0, overdue_days * 10)
