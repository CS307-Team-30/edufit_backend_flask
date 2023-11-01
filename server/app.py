from flask import Flask, request, jsonify, session, make_response
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin
from flask_session import Session
from config import ApplicationConfig
from models import Community, Post, db, User
from functools import wraps
from dotenv import load_dotenv

import jwt
import os
import datetime

load_dotenv()

app = Flask(__name__)
app.config.from_object(ApplicationConfig)

secret_key = "this_is_a_key"

bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)
server_session = Session(app)


db.init_app(app)

dummy_posts = [
    {"title": "Dummy Post 1", "content": "Content of dummy post 1", "user_id": 1, "community_id": 1},
    {"title": "Dummy Post 2", "content": "Content of dummy post 2", "user_id": 1, "community_id": 1},
    # Add more dummy posts as needed
]

with app.app_context():

    # Ensure all tables are created
    db.create_all()

    # Create and add dummy posts to the database
    for post_data in dummy_posts:
        post = Post(title=post_data["title"], content=post_data["content"], user_id=post_data["user_id"], community_id=post_data["community_id"])
        db.session.add(post)

    # Commit the changes to the database
    db.session.commit()

def decode_token(token: str):
    try:
        data = jwt.decode(token, secret_key, algorithms=["HS256"])
    except:
        return None
    return data

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({
                "error": "Token is missing"
            }), 400

        try:
            data = jwt.decode(token, secret_key, algorithms=["HS256"])
        except:
            return jsonify({
                "error": "Token is invalid"
            }), 400

        return f(*args, **kwargs)

    return decorated

@app.route("/protected")
@token_required
def protected():
    return jsonify({"message": "Access granted (got token)"})

@app.route("/unprotected")
def unprotected():
    return jsonify({"message": "This is viewable by anyone."})

@app.route("/@me")
def get_current_user():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    user = User.query.filter_by(id=user_id).first()
    return jsonify({
        "id": user.id,
        "username": new_user.username,
        "email": user.email
    }) 

@app.route("/register", methods=["POST"])
def register_user():

    '''
    body:
    {
        "username": <username>,
        "email": <email>,
        "password": <password>
    }
    '''

    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]

    username_in_use = User.query.filter_by(username=username).first() is not None
    if username_in_use:
        return jsonify({"error": "Username is taken"}), 409

    email_in_use = User.query.filter_by(email=email).first() is not None
    if email_in_use:
        return jsonify({"error": "Email is taken"}), 409

    hashed_password = bcrypt.generate_password_hash(password)
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    token = jwt.encode(
        {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        },
        secret_key,
        algorithm="HS256"
    )

    return jsonify({
        "token": token
    })

@app.route("/create-post", methods=["POST"])
def create_post():
    token = request.json["authToken"]
    decodedToken = decode_token(token)

    username = decodedToken['username']
    
    user = User.query.filter_by(username=username).first()

    if user is None:
        return jsonify({"error": "User does not exist"}), 401
    
    community_id = request.json["communityId"]
    post_title = request.json["postTitle"]
    post_content = request.json["postDescription"]

    # Create a new Post object
    new_post = Post(
        title=post_title,  # Assuming the post content has a title
        content=post_content,  # Assuming the post content has the actual content
        user_id=user.id,
        community_id=community_id
    )

    # Add the new post to the database
    db.session.add(new_post)
    db.session.commit()

    return jsonify({"message": "Post created successfully"}), 201


    # token = jwt.encode(
    #     {
    #         "id": user.id,
    #         "username": user.username,
    #         "email": user.email,
    #         'exp' : datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    #     },
    #     secret_key,
    #     algorithm="HS256"
    # )

    # return jsonify({
    #     "token": token
    # })

@app.route("/login", methods=["POST"])
def login_user():

    '''
    body:
    {
        "username": <username>,
        "password": <password>
    }
    '''

    username = request.json["username"]
    password = request.json["password"]

    user = User.query.filter_by(username=username).first()

    if user is None:
        return jsonify({"error": "User does not exist"}), 401

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Password is incorrect"}), 401

    token = jwt.encode(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        },
        secret_key,
        algorithm="HS256"
    )

    return jsonify({
        "token": token
    })

@app.route("/create-community", methods=["POST"])
def create_community():
    # Retrieve data from the POST request
    data = request.json

    # Check if the required data is present
    if not data or 'name' not in data:
        return jsonify({"error": "Missing community name"}), 400

    # Create a new Community instance
    new_community = Community(name=data['name'])

    # Add the new community to the database
    db.session.add(new_community)

    # Commit the changes to the database
    try:
        db.session.commit()
        return jsonify({"message": "Community created successfully", "id": new_community.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/all-communities", methods=["GET"])
def get_communities():
    communities = Community.query.all()

    # Convert the community objects to a list of dictionaries
    communities_list = [{'id': community.id, 'name': community.name} for community in communities]

    # Return the list as JSON

    try:
        return jsonify(communities_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get_messages", methods=["POST"])
def get_messages():
    
    '''
    body:
    {
        "token": <authentication token>
    }
    '''

    token_data = decode_token(token)
    if token_data is None:
        return jsonify({"error": "Token invalid!"}), 401

    user_id = token_data["id"]

    # Gets all messages with current user as the recipient id
    messages = Messages.query.filter_by(recipient_id = user_id)

    # Converts to table
    message_list = [
        {
            'msg_id': message.msg_id,
            'sender_id': message.sender_id,
            'recipient_id': message.recipient_id,
            'title': message.title,
            'content': message.content,
            'read': message.read
        } 
        for message in messages
    ]

    # Return the list as JSON
    try:
        return jsonify(message_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/logout", methods=["POST"])
def logout_user():
    # session.pop("user_id")
    return "200"

if __name__ == "__main__":
# Creating instances of the Community class for each CS course
    
    app.run(port=8000, debug=True)