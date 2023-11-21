from flask import Flask, request, jsonify, session, make_response
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin
from flask_session import Session
from config import ApplicationConfig
from models import Community, Post, db, User, Profile
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
    # for post_data in dummy_posts:
    #     post = Post(title=post_data["title"], content=post_data["content"], user_id=post_data["user_id"], community_id=post_data["community_id"])
    #     db.session.add(post)

    # # Commit the changes to the database
    db.session.commit()

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

def decode_token(token: str):
    try:
        data = jwt.decode(token, secret_key, algorithms=["HS256"])
    except:
        return None
    
    return data

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
    
    new_profile = Profile(user_id=new_user.id, nickname=new_user.username)
    db.session.add(new_profile)

    db.session.commit()
    
    # session["user_id"] = new_user.id

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

    '''
    return jsonify({
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email
    })
    '''


@app.route("/user-communities/<int:user_id>", methods=["GET"])
def get_user_communities(user_id):
    # Fetch the user by ID
    user = User.query.get(user_id)

    # Check if the user exists
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Get all communities the user is subscribed to
    subscribed_communities = user.communities

    # Convert the community objects to a list of dictionaries
    communities_list = [{
        'id': community.id,
        'name': community.name
    } for community in subscribed_communities]

    # Return the list as JSON
    return jsonify(communities_list), 200


@app.route("/subscribe", methods=["POST"])
def subscribe_to_community():
    user_id = request.json.get('user_id')
    community_id = request.json.get('community_id')

    if not user_id or not community_id:
        return jsonify({"error": "Missing user ID or community ID"}), 400

    user = User.query.get(user_id)
    community = Community.query.get(community_id)

    if not user or not community:
        return jsonify({"error": "User or Community not found"}), 404

    if community in user.communities:
        return jsonify({"message": "User already subscribed to community"}), 409

    user.communities.append(community)
    db.session.commit()

    return jsonify({"message": "User subscribed to community successfully"}), 200


@app.route("/user-subscribed-posts/<int:user_id>", methods=["GET"])
def get_user_subscribed_posts(user_id):
    # Fetch the user by ID
    user = User.query.get(user_id)

    # Check if the user exists
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Get the IDs of communities the user is subscribed to
    subscribed_community_ids = [community.id for community in user.communities]

    # Query the database to get all posts from these communities
    posts = Post.query.filter(Post.community_id.in_(subscribed_community_ids)).all()

    # Convert the posts to a list of dictionaries for JSON serialization
    posts_list = []
    for post in posts:
        # Fetch the author and community details
        author = User.query.get(post.user_id)
        community = Community.query.get(post.community_id)

        post_details = {
            'title': post.title,
            'content': post.content,
            'author': {
                'id': author.id,
                'username': author.username,
                'email': author.email,
                # Add other user fields as needed
            },
            'community': {
                'id': community.id,
                'name': community.name,
                # Add other community fields as needed
            },
            # 'comments': [
            #     {
            #         'id': comment.id,
            #         'content': comment.content,
            #         # Add other comment fields as needed
            #     } for comment in post.comments
            # ] if post.comments else []
        }
        posts_list.append(post_details)

    # Return the list as JSON
    return jsonify(posts_list), 200

@app.route("/unsubscribe", methods=["POST"])
def unsubscribe_from_community():
    user_id = request.json.get('user_id')
    community_id = request.json.get('community_id')

    if not user_id or not community_id:
        return jsonify({"error": "Missing user ID or community ID"}), 400

    user = User.query.get(user_id)
    community = Community.query.get(community_id)

    if not user or not community:
        return jsonify({"error": "User or Community not found"}), 404

    if community not in user.communities:
        return jsonify({"message": "User not subscribed to community"}), 409

    user.communities.remove(community)
    db.session.commit()

    return jsonify({"message": "User unsubscribed from community successfully"}), 200


@app.route('/community/<int:community_id>', methods=['GET'])
def get_community_posts(community_id):
    # Query the database to get all posts for the specified community
    posts = Post.query.filter_by(community_id=community_id).all()

    # Convert the posts to a list of dictionaries for JSON serialization
    posts_list = []
    for post in posts:
        # Fetch the user and community details
        user = User.query.get(post.user_id)
        community = Community.query.get(post.community_id)

        post_details = {
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'author': {
                'id': user.id,
                'username': user.username
            },
            'community': {
                'id': community.id,
                'name': community.name,
                'description': community.description
            }
        }
        posts_list.append(post_details)

    return jsonify(posts_list)

@app.route("/create-post", methods=["POST"])
def create_post():
    token = request.json["authToken"]
    decodedToken = jwt.decode(token, secret_key, algorithms=["HS256"])
    print(decodedToken)
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

    '''
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email
    })
    '''



@app.route("/login", methods=["POST"])
def login_user():
    username = request.json["username"]
    password = request.json["password"]

    user = User.query.filter_by(username=username).first()
    print(user.id)

    if user is None:
        return jsonify({"error": "User does not exist"}), 401

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Password is incorrect"}), 401
    
    # session["user_id"] = user.id

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

@app.route("/get-profile", methods=["GET"])
def get_profile():
    print("Starting...")

    token = request.args.get("authToken")
    token_data = jwt.decode(token, secret_key, algorithms=["HS256"])

    # print("Got token: " + token)

    if token is None:
        print("Token is invalid")
        return jsonify({"error": "Token is invalid"}), 401

    user_id = token_data['id']
    # print("user_id" + user_id)

    user_id = request.args.get('user_id')
    profile = Profile.query.filter_by(user_id=user_id).first()

    if profile is None:
        print("Profile does not exist")
        return jsonify({"error": "Profile does not exist"}), 401
        return jsonify({"error": "Profile does not exist"}), 404

    return jsonify({
        "user_id": profile.user_id,
        "nickname": profile.nickname,
        "bio": profile.bio,
        "profile_pic": profile.profile_pic
    })

@app.route("/update_profile", methods=["POST"])
def update_profile():

    user_data = decode_token(request.json["token"])

    if user_data is None:
        return jsonify({"error": "Token is invalid"}), 400
    
    profile = Profile.query.filter_by(user_id=user_data[id]).first()

    if profile is None:
        return jsonify({"error": "No profile found"}), 400

    new_nickname = request.json["nickname"]
    new_bio = request.json["bio"]
    new_profile_pic = request.json["profile_pic"]

    if new_nickname:
        profile.nickname = new_nickname

    if new_bio:
        profile.bio = new_bio

    if new_profile_pic:
        profile.profile_pic = new_profile_pic

    return "200"
    '''
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email
    })
    '''
@app.route("/create-community", methods=["POST"])
def create_community():
    # Retrieve data from the POST request
    data = request.json

    # Check if the required data is present
    if not data or 'name' not in data:
        return jsonify({"error": "Missing community name"}), 400

    # Create a new Community instance
    new_community = Community(name=data['name'], description=data['description'])

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

@app.route("/send-message", methods=["POST"])
def send_message():
    '''
    body:
    {
        "authToken": <authentication token>,
        "recipient_username": <username of person that gets message>,
        "title": <title of message>,
        "body": <the contents of the message>
    }
    '''
    token = request.json["authToken"]
    token_data = jwt.decode(token, secret_key, algorithms=["HS256"])
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

@app.route("/get-messages", methods=["GET"])
def get_messages():
    
    '''
    body:
    {
        "authToken": <authentication token>
    }
    '''
    token = request.json["authToken"]
    token_data = jwt.decode(token, secret_key, algorithms=["HS256"])
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

@app.route("/all-communities", methods=["GET"])
def get_communities():
    communities = Community.query.all()

    # Convert the community objects to a list of dictionaries
    communities_list = [{'id': community.id, 'name': community.name, 'description': community.description} for community in communities]

    # Return the list as JSON

    try:
        return jsonify(communities_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route("/logout", methods=["POST"])
def logout_user():
    # session.pop("user_id")
    return "200"

if __name__ == "__main__":
# Creating instances of the Community class for each CS course
    
    app.run(port=8000, debug=True)