from db import db

class Student(db.Model):
  __tablename__ = "students"
  id = db.Column(db.Integer,primary_key = True)
  stu_name = db.Column(db.String(100),nullable=False)
  stu_age = db.Column(db.Integer,nullable=False)
  stu_email = db.Column(db.String(100),unique=True)
  stu_phone = db.Column(db.String(100),nullable=False,unique=True)
  password_hash = db.Column(db.String(255), nullable=False)
  profile_pic = db.Column(db.String(255), nullable=True, default='default.jpg')

  # Relationships
  transactions = db.relationship('Transaction', backref='student', lazy=True, cascade="all, delete-orphan")
