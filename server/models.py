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
    return uuid4().int


user_community_association = Table('user_community', db.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('community_id', Integer, ForeignKey('communities.id'))
)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    
    # Foreign key for the many-to-one relationship with Post
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    post = relationship("Post", back_populates="comments")

    # Foreign key for the many-to-one relationship with User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = relationship("User", back_populates="comments")





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

    comments = relationship("Comment", back_populates="post")



class Community(db.Model):
    __tablename__ = "communities"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)   
    description = db.Column(db.String, nullable=False)

    users = relationship("User", secondary=user_community_association, back_populates='communities')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    posts = relationship("Post", back_populates="community")

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(
        db.Integer,
        primary_key=True,
        unique=True,
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
    communities = relationship("Community", secondary=user_community_association, back_populates="users")
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
    waterConsumed = db.Column(
        db.Integer,
        default=0
    )

    comments = relationship("Comment", back_populates="user")


    posts = relationship("Post", back_populates="user")
