from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from sqlalchemy import Table, create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

import jwt
import datetime

Base = declarative_base()

db = SQLAlchemy()

def get_uuid():
    return uuid4().hex


user_community_association = Table('user_community', db.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('community_id', Integer, ForeignKey('communities.id'))
)


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = relationship("User", back_populates="posts")

    # Foreign key for the many-to-one relationship with Community
    community_id = db.Column(db.Integer, db.ForeignKey('communities.id'))
    community = relationship("Community", back_populates="posts")

    # One-to-many relationship with Comment
    # comments = relationship("Comment", back_populates="post")



class Community(db.Model):
    __tablename__ = "communities"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)   

    users = relationship("User", secondary=user_community_association, back_populates='communities')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    posts = relationship("Post", back_populates="community")

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
        db.String(345),
        default=0
    )
    communities = relationship("Community", secondary=user_community_association, back_populates="users")
    moderator = db.Column(
        db.Boolean,
        default=False
    )
    authentication_token = db.Column(
        db.String(345)
    )
    posts = relationship("Post", back_populates="user")

class Profile(db.Model):
    __tablename__ = "profiles"
    id = db.Column(
        db.String(32),
        primary_key=True,
        unique=True,
        default=get_uuid
    )
    user_id = db.Column(
        db.String(32),
        db.ForeignKey('users.id'),
        nullable=False
    )
    nickname = db.Column(
        db.String(345),
        nullable=False
    )
    bio = db.Column(
        db.Text,
        default="Hello, I am proud member of EduFit!"
    )
    profile_pic = db.Column(
        db.Text,
        nullable=True
    )
    visibility = db.Column(
        db.Boolean,
        default=True
    )
    last_changed = db.Column(
        db.DateTime
    )

class Goal(db.Model):
    __tablename__ = "goals"
    goal_id = db.Column(
        db.String(32),
        primary_key=True,
        unique=True,
        default=get_uuid
    )
    goal_type = db.Column(
        db.String(32),
        nullable=False,
        default="Goal"
    )
    name = db.Column(
        db.String(350),
        nullable=False,
        default="Unnamed Goal / Milestone"
    )
    pounds = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )
    date = db.Column(
        db.DateTime
    )
    description = db.Column(
        db.String(350),
        nullable=False,
        default="Good luck!"
    )

class Message(db.Model):
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





    

# cs_59300 = Community(id=1, name="CS 59300 - Special Topics")
# cs_59799 = Community(id=2, name="CS 59799 - Graduate Professional Practice")
# cs_15900 = Community(id=3, name="CS 15900 - C Programming")
# cs_18000 = Community(id=4, name="CS 18000 - Problem Solving And Object-Oriented Programming")
# cs_18200 = Community(id=5, name="CS 18200 - Foundations Of Computer Science")
# cs_18300 = Community(id=6, name="CS 18300 - Professional Practice I")
# cs_18400 = Community(id=7, name="CS 18400 - Professional Practice II")
# cs_19000 = Community(id=8, name="CS 19000 - Topics In Computer Sciences")
# cs_50011 = Community(id=9, name="CS 50011 - Introduction To Systems For Information Security")
# cs_17600 = Community(id=10, name="CS 17600 - Data Engineering In Python")
# cs_17700 = Community(id=11, name="CS 17700 - Programming With Multimedia Objects")

# # Add these instances to the session and commit to save changes
# db.session.add_all([cs_59300, cs_59799, cs_15900, cs_18000, cs_18200, cs_18300, cs_18400, cs_19000, cs_50011, cs_17600, cs_17700])
# db.session.commit()