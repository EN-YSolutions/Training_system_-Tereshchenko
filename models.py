from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import ARRAY
import uuid
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(255), nullable=False)
    name = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(7))  # HEX color, e.g., #RRGGBB

    feedbacks = db.relationship('Course_Feedback', backref='user', lazy=True)

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    author_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(255), nullable=False)
    url = db.Column(db.Text, nullable=True)

    author = db.relationship('User', backref='courses', lazy=True)
    feedbacks = db.relationship('Course_Feedback', backref='course', lazy=True)
    tests = db.relationship('Test', backref='course', lazy=True)

class Course_Feedback(db.Model):
    __tablename__ = 'courses_feedbacks'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = db.Column(db.String(36), db.ForeignKey('courses.id'), nullable=False)
    author_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Test(db.Model):
    __tablename__ = 'tests'
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = db.Column(db.String(36), db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    questions = db.Column(db.String(256), nullable=True)
    time = db.Column(db.String(256), nullable=True)
    interval = db.Column(db.String(256), nullable=True)
    topics = db.Column(ARRAY(db.String), nullable=True, default=list)

class Group(db.Model):
    __tablename__ = 'groups'
    # Внешний ключ для таблицы Group_Members
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = db.Column(db.String(36), db.ForeignKey('courses.id'), nullable=False)
    curator_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    title = db.Column(db.String(256), nullable=False)

    # Связь с таблицей Group_Members
    members = db.relationship('Group_Members', back_populates='group')

class Group_Members(db.Model):
    __tablename__ = 'groups_members'
    group_id = db.Column(db.String(36), db.ForeignKey('groups.id'), primary_key=True, nullable=False)
    student_id = db.Column(db.String(36), db.ForeignKey('users.id'), primary_key=True, nullable=False)
    # Связь с таблицей Group
    group = db.relationship('Group', back_populates='members')

class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    status = db.Column(db.String(20), nullable=False, default='pending')

