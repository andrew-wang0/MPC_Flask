from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime


# Database
db = SQLAlchemy()

user_course = db.Table('user_course',
                       db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column('course_id', db.Integer, db.ForeignKey('course.id')))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    courses = db.relationship('Course', secondary=user_course, backref='users')
    question_attempts = db.relationship('QuestionAttempt', backref='user')

    def __repr__(self):
        return f'User({self.email})'

    def __init__(self, email, password, is_admin=False):
        self.email = email
        self.password = password
        self.is_admin = is_admin


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    is_published = db.Column(db.Boolean, default=False, nullable=False)

    assessments = db.relationship('Assessment', backref='course')

    def __repr__(self):
        return f'Course({self.name})'


class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_published = db.Column(db.Boolean, default=False, nullable=False)

    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    questions = db.relationship('Question', backref='assessment')

    def __repr__(self):
        return f'Assessment({self.number} {self.name})'


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_number = db.Column(db.Integer, nullable=False)
    question_text = db.Column(db.Text(2000), nullable=False)
    correct_answer = db.Column(db.String(200), nullable=False)
    guesses_allowed = db.Column(db.Integer, default=10, nullable=False)

    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'))

    question_attempts = db.relationship('QuestionAttempt', backref='question')

    def __repr__(self):
        return f'Question({self.question_number} {self.assessment_id})'


class QuestionAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'QuestionAttempt({self.id} {self.answer} {self.question_id} {self.user_id})'
