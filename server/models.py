from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

import jwt
import datetime

db = SQLAlchemy()

def get_uuid():
    return uuid4().hex

class User(db.Model):
    __tablename__ = "users"
    # Basic credentials (NOT NULLABLE)
    id = db.Column(
        db.String(32),
        primary_key=True,
        unique=True,
        default=get_uuid
    )
    username = db.Column(
        db.String(345),
        unique=True,
        nullable=False
    )
    email = db.Column(
        db.String(345),
        unique=True,
        nullable=False
    )
    password = db.Column(
        db.Text,
        nullable=False
    )
    privilege = db.Column(
        db.Integer,
        default=0
    )
    # Additional fields to match the TypeScript interface
    meals = db.relationship('Meal', backref='user', lazy=True)
    nutrition_goals = db.relationship('NutritionGoals', back_populates='users', uselist=False)
    communities = db.relationship('Community', secondary='user_community', back_populates='users')
    workout_plan = db.relationship('WorkoutPlan', back_populates='users', uselist=False)
    metrics = db.relationship('Metrics', back_populates='users', uselist=False)
    privacy_settings = db.relationship('PrivacySettings', back_populates='users', uselist=False)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    moderator = db.Column(
        db.Boolean,
        default=False
    )
    authentication_token = db.Column(
        db.String(345)
    )
    exp = db.Column(
        db.Integer,
        default=0
    )

class Meal(db.Model):
    __tablename__ = "meals"
    mealId = db.Column(db.String(32), primary_key=True, unique=True)
    name = db.Column(db.String(345), nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    fats = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'))


class Message (db.Model):
    __tablename__ = "messages"
    msg_id = db.Column(
        db.String(32),
        primary_key=True,
        unique=True,
        default=get_uuid
    )
    sender_id = db.Column(
        db.String(32),
        db.ForeignKey('users.id'),
        nullable=False
    )
    recipient_id = db.Column(
        db.String(32),
        db.ForeignKey('users.id'),
        nullable=False
    )
    title = db.Column(
        db.Text
    )
    content = db.Column(
        db.Text
    )
    read = db.Column(
        db.Boolean,
        default=False
    )


'''
class Metrics(db.Model):
    __tablename__ = "metrics"
    height = db.Column(
        db.Integer
    )
    weight = db.Column(
        db.Integer
    )
    bodyfat = db.Column(
        db.Integer
    )

class Community(db.Model):
    __tablename__ = "communities"
    id = db.Column(
        db.String(32),
        primary_key=True,
        unique=True,
        default=get_uuid
    )
    name = db.Column(
        db.String(345), 
        unique=True,
        nullable=False
    )

class Thread(db.Model):
    __tablename__ = "threads"
    id = db.Column(
        db.String(32),
        primary_key=True,
        unique=True,
        default=get_uuid
    )
    title = db.Column(
        db.String(345), 
        unique=True,
        nullable=False
    )
    content = db.Column(
        db.Text,
        nullable=False
    )

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(
        db.String(32),
        primary_key=True,
        unique=True,
        default=get_uuid
    )
    content = db.Column(
        db.String(345), 
        nullable=False
    )
    timestamp = db.Column(
        db.DateTime
    )
'''
