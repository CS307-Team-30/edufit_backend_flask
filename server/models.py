from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

import jwt
import datetime

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
    privilege = db.Column(
        db.Integer,
        default=0
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