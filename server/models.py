from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

db = SQLAlchemy()

def get_uuid():
    return uuid4().hex

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

class PrivacySettings(db.Model):
    __tablename__ = "privacy_settings"
    profile_visibility = db.Column(
        db.Boolean
    )
    message_privacy = db.Column(
        db.Boolean
    )

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
