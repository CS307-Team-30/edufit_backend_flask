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


instructor_community_association = Table('instructor_community', db.metadata,
    Column('instructor_id', Integer, ForeignKey('instructors.id'), primary_key=True),
    Column('community_id', Integer, ForeignKey('communities.id'), primary_key=True)
)

user_community_association = Table('user_community', db.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('community_id', Integer, ForeignKey('communities.id'))
)


post_upvote_association = Table('post_upvotes', db.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('post_id', Integer, ForeignKey('posts.id'))
)

post_downvote_association = Table('post_downvotes', db.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('post_id', Integer, ForeignKey('posts.id'))
)

comment_upvote_association = Table('comment_upvotes', db.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('comment_id', Integer, ForeignKey('comments.id'))
)

comment_downvote_association = Table('comment_downvotes', db.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('comment_id', Integer, ForeignKey('comments.id'))
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

    upvoted_by = relationship("User", secondary=comment_upvote_association)
    downvoted_by = relationship("User", secondary=comment_downvote_association)



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

    upvoted_by = relationship("User", secondary=post_upvote_association)
    downvoted_by = relationship("User", secondary=post_downvote_association)



class Instructor(db.Model):
    __tablename__ = "instructors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    bio = db.Column(db.Text)

    # Relationship - one instructor can have many communities
    communities = db.relationship("Community", secondary=instructor_community_association, back_populates="instructors")


class Community(db.Model):
    __tablename__ = "communities"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)   
    description = db.Column(db.String, nullable=False)

    users = relationship("User", secondary=user_community_association, back_populates='communities')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    posts = relationship("Post", back_populates="community")
        # Add a foreign key for Instructor
    instructors = db.relationship("Instructor", secondary=instructor_community_association, back_populates="communities")

    prerequisite_id = db.Column(db.Integer, db.ForeignKey('communities.id'))

    # Define the relationship (self-referential)
    prerequisites = db.relationship('Community', 
                                    backref=db.backref('prerequisite', remote_side=[id]),
                                    lazy='dynamic')


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
