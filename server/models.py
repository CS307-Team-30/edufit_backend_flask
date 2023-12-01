from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from sqlalchemy import Table, create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import jwt


Base = declarative_base()

db = SQLAlchemy()

def get_uuid():
    return uuid4().int


community_prerequisite_association = Table('community_prerequisite', db.metadata,
    Column('community_id', Integer, ForeignKey('communities.id'), primary_key=True),
    Column('prerequisite_id', Integer, ForeignKey('communities.id'), primary_key=True)
)

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


# Association table for the many-to-many relationship between Users and Chatboxes
user_chatbox_association = Table('user_chatbox', db.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('chatbox_id', Integer, ForeignKey('chatboxes.id'), primary_key=True)
)

class PrivateMessage(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key for the many-to-one relationship with User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User", backref="messages")

    # Foreign key for the many-to-one relationship with Chatbox
    chatbox_id = db.Column(db.Integer, db.ForeignKey('chatboxes.id'))
    chatbox = db.relationship("Chatbox", back_populates="messages")


class Profile(db.Model):
    __tablename__ = "profiles"
    id = db.Column(
        db.Integer,
        primary_key=True,
        unique=True,
    )
    user_id = db.Column(
        db.Integer,
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
        default="user_icon.jpg",
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


class Chatbox(db.Model):
    __tablename__ = 'chatboxes'
    id = db.Column(db.Integer, primary_key=True)
    
    # Relationship with Message
    messages = db.relationship("PrivateMessage", back_populates="chatbox")

    # Relationship with User
    users = db.relationship("User", secondary=user_chatbox_association, back_populates='chatboxes')



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
                                     secondary=community_prerequisite_association,
                                     primaryjoin=id==community_prerequisite_association.c.community_id,
                                     secondaryjoin=id==community_prerequisite_association.c.prerequisite_id,
                                     backref="prerequisite_for")


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

    chatboxes = db.relationship("Chatbox", secondary=user_chatbox_association, back_populates="users")
    posts = relationship("Post", back_populates="user")