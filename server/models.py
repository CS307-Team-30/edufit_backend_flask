from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

import jwt
import datetime

db = SQLAlchemy()

def get_uuid():
    return uuid4().hex


# Meal Model
class Meal(db.Model):
    __tablename__ = "meals"
    mealId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(345), nullable=False)
    # Nutrients will be stored as a JSON string
    nutrients = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'))

# NutritionGoals Model
class NutritionGoals(db.Model):
    __tablename__ = "nutrition_goals"
    id = db.Column(db.Integer, primary_key=True)
    macroRatio = db.Column(db.Float, nullable=False)
    # MicronutrientGoals will be stored as a JSON string
    micronutrientGoals = db.Column(db.JSON)
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'))

# Community Model
class Community(db.Model):
    __tablename__ = "communities"
    communityId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(345), nullable=False)
    # Relationship with User
    users = db.relationship('User', secondary='user_community', back_populates='communities')

# Association table for User-Community many-to-many relationship
user_community = db.Table('user_community',
    db.Column('user_id', db.String(32), db.ForeignKey('users.id'), primary_key=True),
    db.Column('community_id', db.Integer, db.ForeignKey('communities.communityId'), primary_key=True)
)

# Exercise Model
class Exercise(db.Model):
    __tablename__ = "exercises"
    exerciseId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(345), nullable=False)
    description = db.Column(db.Text, nullable=False)
    imageUrl = db.Column(db.String(345), nullable=False)

# Schedule Model
class Schedule(db.Model):
    __tablename__ = "schedules"
    id = db.Column(db.Integer, primary_key=True)
    # Relationship with UserEvent
    events = db.relationship('UserEvent', backref='schedule', lazy=True)

# UserEvent Model
class UserEvent(db.Model):
    __tablename__ = "user_events"
    eventId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(345), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    repeat = db.Column(db.String(100))
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'))

# WorkoutPlan Model
class WorkoutPlan(db.Model):
    __tablename__ = "workout_plans"
    planId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(345), nullable=False)
    # Relationship with Exercise
    exercises = db.relationship('Exercise', secondary='workout_plan_exercise', back_populates='workout_plans')
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'))
    schedule = db.relationship('Schedule', back_populates='workout_plans', uselist=False)
    goals = db.Column(db.String(345), nullable=False)
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'))

# Association table for WorkoutPlan-Exercise many-to-many relationship
workout_plan_exercise = db.Table('workout_plan_exercise',
    db.Column('plan_id', db.Integer, db.ForeignKey('workout_plans.planId'), primary_key=True),
    db.Column('exercise_id', db.Integer, db.ForeignKey('exercises.exerciseId'), primary_key=True)
)

# Metrics Model
class Metrics(db.Model):
    __tablename__ = "metrics"
    id = db.Column(db.Integer, primary_key=True)
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    bodyfat = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'))

# PrivacySettings Model
class PrivacySettings(db.Model):
    __tablename__ = "privacy_settings"
    id = db.Column(db.Integer, primary_key=True)
    profileVisibility = db.Column(db.Boolean, default=True)
    messagePrivacy = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'))

# Notification Model
class Notification(db.Model):
    __tablename__ = "notifications"
    notificationId = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'))

# Updated User Model
class User(db.Model):
    __tablename__ = "users"
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
    nutrition_goals = db.relationship('NutritionGoals', back_populates='user', uselist=False)
    communities = db.relationship('Community', secondary='user_community', back_populates='users')
    workout_plan = db.relationship('WorkoutPlan', back_populates='user', uselist=False)
    metrics = db.relationship('Metrics', back_populates='user', uselist=False)
    privacy_settings = db.relationship('PrivacySettings', back_populates='user', uselist=False)
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