from flask import Flask, request, jsonify, session, make_response
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin
from flask_session import Session
from config import ApplicationConfig
from models import db, User
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

with app.app_context():
    db.create_all()

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

        data = decode_token(token)

        if data is None:
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
@cross_origin()
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

@app.route("/login", methods=["POST"])
@cross_origin()
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

@app.route("/get_profile", methods=["POST"])
@cross_origin()
def get_profile():

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




@app.route("/send_message", methods=["POST"])
@cross_origin()
def send_message():

    '''
    body:
    {
        "token": <authentication token>,
        "recipient_username": <username of person that gets message>,
        "title": <title of message>,
        "body": <the contents of the message>
    }
    '''

    token_data = decode_token(token)
    if token_data is None:
        return jsonify({"error": "Token invalid!"}), 401

    recipient_username = request.json["recipient_username"]
    recipient = User.query.filter_by(username=recipient_username).first()
    if recipient is None:
        return jsonify({"error": "Recipient not found!"}), 401

    msg_title = request.json["title"]
    msg_body = request.json["body"]

    new_msg = Message(
        sender_id = token_data["id"],
        recipient_id = recipient.id,
        title = msg_title,
        content = msg_body
    )

    db.session.add(new_msg)
    db.session.commit()

    # Ask Arnob if this needs to return anything
    return jsonify({"msg": "Message sent!"}), 200

@app.route("/get_messages", methods=["POST"])
@cross_origin()
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
    message_list = [{'id': community.id, 'name': community.name} for message in messages]


# Still requires implementation, could just be a redirect to homepage?
@app.route("/logout", methods=["POST"])
def logout_user():
    return "200"

if __name__ == "__main__":
    app.run(port=8000, debug=True)