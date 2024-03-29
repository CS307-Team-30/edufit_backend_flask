from flask_socketio import SocketIO, emit, send
from flask import Flask, request, jsonify, send_from_directory, session, make_response
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin
from flask_session import Session
from flask_mail import Mail, Message
from config import ApplicationConfig
from models import Chatbox, Community, GoalEntry, MilestoneEntry, PrivateMessage, Post, Profile, WeightEntry, db, User, Comment, Instructor, user_chatbox_association
from functools import wraps
from dotenv import load_dotenv

import jwt
import os
import datetime

load_dotenv()

app = Flask(__name__)
app.config.from_object(ApplicationConfig)
socketio = SocketIO(app,cors_allowed_origins="*")

UPLOAD_FOLDER = 'images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'edufitburner@gmail.com'
app.config['MAIL_PASSWORD'] = 'ahptphuobidkszvu'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

secret_key = "this_is_a_key"

bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)
server_session = Session(app)


db.init_app(app)

with app.app_context():

    # LONG COMMENT HERE

    
    # Ensure all tables are created
    db.create_all()
    # instructor1 = Instructor(name="John Doe", email="john@example.com", bio="Expert in Programming")
    # instructor2 = Instructor(name="Jane Smith", email="jane@example.com", bio="Data Science Specialist")

    # # # Add instructors to the session
    # db.session.add(instructor1)
    # db.session.add(instructor2)

    # # # Create two communities
    # community1 = Community(name="CS10100", description="Learn the basics of programming.")
    # community2 = Community(name="CS20100", description="Advanced concepts in programming.")
    # db.session.add(community1)
    # db.session.add(community2)

    # community1.instructors.append(instructor1)
    # community2.instructors.append(instructor1)
    # community2.instructors.append(instructor2)

    # # Commit to save instructors and communities
    # community1 = Community.query.filter_by(name="CS10100").first()
    # community2 = Community.query.filter_by(name="CS20100").first()

    # if community1 and community2:
    # # Make community1 a prerequisite for community2
    #     community2.prerequisites.append(community1)

    # db.session.commit()

    # LONG COMMENT END


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

    # print("new user id: " + new_user.id)
    
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

@app.route("/change-password", methods=["POST"])
def change_password():

    '''
    body:
    {
        "authToken": <token>,
        "password": <new password again>
        "confirmation": <password again>
    }
    '''

    token = request.json["authToken"]
    token_data = jwt.decode(token, secret_key, algorithms=["HS256"])

    password = request.json["password"]
    confirmation = request.json["confirmation"]

    # EXIT 1 : Token is invalid

    if token is None:
        print("Token is invalid")
        return jsonify({"error": "Token is invalid"}), 401

    user_id = token_data['id']
    user = User.query.filter_by(id=user_id).first()

    # EXIT 2 : User not found

    if user is None:
        print("User not found")
        return jsonify({"error": "User not found."})

    # EXIT 3 : Password not confirmed

    if not password == confirmation:
        return jsonify({"error": "Your passwords do not match!"})

    # EXIT 4 : Password cannot be same one as before

    if bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Password cannot be the same one as before."})

    # All checks passed: change password
    
    hashed_password = bcrypt.generate_password_hash(password)
    user.password = hashed_password
    db.session.commit()

    return jsonify({"msg": "Password change successful!"})

@app.route("/update-bio", methods=["POST"])
def update_bio():

    '''
    body:
    {
        "authToken": <token>,
        "new_bio": <new bio>
    }
    '''

    token = request.json["authToken"]
    token_data = jwt.decode(token, secret_key, algorithms=["HS256"])

    new_bio = request.json["new_bio"]

    # EXIT 1 : Token is invalid

    if token is None:
        print("Token is invalid")
        return jsonify({"error": "Token is invalid"}), 401

    user_id = token_data['id']
    user = User.query.filter_by(id=user_id).first()

    # EXIT 2 : User not found

    if user is None:
        print("User not found")
        return jsonify({"error": "User not found"})

    # All checks passed: change bio
    
    user.bio = bio
    db.session.commit()

    return jsonify({"msg": "Bio change successful"})

@app.route("/report-post", methods=["POST"])
def report_post():

    '''
    {
        authToken: [token],
        post_id: [id of post],
        reason: [string, inputtable]
    }
    '''

    data = request.json
    token = data["authToken"]
    token_data = jwt.decode(token, secret_key, algorithms=["HS256"])

    username = token_data["username"]
    post_id = data["post_id"]

    post = Post.query.get(post_id)
    post_title = post.title
    post_content = post.content

    msg = Message(
        subject='Post Report #' + str(post_id),
        sender='edufitburner@gmail.com',
        recipients=['jhcheng@purdue.edu']
    )
    msg.body = "A user has reported Post #" + str(post_id) + " for inappropriate content.\nReason: " + data["reason"] + "\n\n#################\n\nPost title:\n" + post_title + "\n\nPost content:\n" + post_content
    mail.send(msg)

    return "Message sent!", 200

@app.route('/user/<int:user_id>/milestone/<int:milestone_id>', methods=['DELETE'])
def delete_milestone_entry(user_id, milestone_id):
    milestone_entry = MilestoneEntry.query.filter_by(id=milestone_id, user_id=user_id).first()
    if milestone_entry:
        db.session.delete(milestone_entry)
        db.session.commit()
        return jsonify({"success": True, "message": "Milestone entry deleted successfully"})
    else:
        return jsonify({"success": False, "message": "Milestone entry not found"}), 404


@app.route('/user/<int:user_id>/goal/<int:goal_id>', methods=['DELETE'])
def delete_goal_entry(user_id, goal_id):
    goal_entry = GoalEntry.query.filter_by(id=goal_id, user_id=user_id).first()
    if goal_entry:
        db.session.delete(goal_entry)
        db.session.commit()
        return jsonify({"success": True, "message": "Goal entry deleted successfully"})
    else:
        return jsonify({"success": False, "message": "Goal entry not found"}), 404


@app.route('/user/<int:user_id>/weight', methods=['POST'])
def add_weight_entry(user_id):
    data = request.json
    new_weight_entry = WeightEntry(
        date=data['date'],
        weight=data['weight'],
        user_id=user_id
    )
    db.session.add(new_weight_entry)
    db.session.commit()
    return jsonify({"success": True, "message": "Weight entry added successfully"})


@app.route('/user/<int:user_id>/weights', methods=['GET'])
def get_weight_entries(user_id):
    weight_entries = WeightEntry.query.filter_by(user_id=user_id).all()
    return jsonify([
        {"date": entry.date, "weight": entry.weight} for entry in weight_entries
    ])

@app.route('/user/<int:user_id>/goal', methods=['POST'])
def add_goal_entry(user_id):
    data = request.json
    new_goal_entry = GoalEntry(
        user_id=user_id,
        exerciseName=data['exerciseName'],
        targetPounds=data['targetPounds'],
        date=data['date'],
        description=data['description']
    )
    db.session.add(new_goal_entry)
    db.session.commit()
    return jsonify({"success": True, "message": "Goal entry added successfully"})



@app.route('/user/<int:user_id>/goals', methods=['GET'])
def get_goal_entries(user_id):
    goal_entries = GoalEntry.query.filter_by(user_id=user_id).all()
    return jsonify([
        {"id": entry.id, "exerciseName": entry.exerciseName, "targetPounds": entry.targetPounds, 
         "date": entry.date, "description": entry.description} for entry in goal_entries
    ])


@app.route('/user/<int:user_id>/milestone', methods=['POST'])
def add_milestone_entry(user_id):
    data = request.json
    new_milestone_entry = MilestoneEntry(
        user_id=user_id,
        exerciseName=data['exerciseName'],
        targetPounds=data['targetPounds'],
        date=data['date'],
        description=data['description']
    )
    db.session.add(new_milestone_entry)
    db.session.commit()
    return jsonify({"success": True, "message": "Milestone entry added successfully"})


@app.route('/user/<int:user_id>/milestones', methods=['GET'])
def get_milestone_entries(user_id):
    milestone_entries = MilestoneEntry.query.filter_by(user_id=user_id).all()
    return jsonify([
        {"id": entry.id, "exerciseName": entry.exerciseName, "targetPounds": entry.targetPounds, 
         "date": entry.date, "description": entry.description} for entry in milestone_entries
    ])




@app.route("/add-comment", methods=["POST"])
def add_comment():
    # Extract data from request
    data = request.json
    user_id = data.get('user_id')
    post_id = data.get('post_id')
    comment_content = data.get('comment')

    # Validate data
    if not user_id or not post_id or not comment_content:
        return jsonify({"error": "Missing data"}), 400

    user = User.query.get(user_id)
    post = Post.query.get(post_id)

    if not user or not post:
        return jsonify({"error": "User or Post not found"}), 404

    # Create a new Comment object
    new_comment = Comment(content=comment_content, user_id=user_id, post_id=post_id)

    # Add the new comment to the database
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({"message": "Comment added successfully"}), 201


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


@app.route('/get-votes', methods=['POST'])
def get_votes():
    data = request.json
    post_id = data.get('post_id')

    # Check if user and post exist
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    # Check existing votes

    return jsonify({
        "upvotes": [user.id for user in post.upvoted_by],
        "downvotes": [user.id for user in post.downvoted_by]
    }), 200


@app.route('/vote', methods=['POST'])
def handle_vote():
    data = request.json
    vote_type = data.get('vote_type')  # 'upvote' or 'downvote'
    user_id = data.get('user_id')
    post_id = data.get('post_id')

    # Check if user and post exist
    user = User.query.get(user_id)
    post = Post.query.get(post_id)
    if not user or not post:
        return jsonify({"error": "User or Post not found"}), 404

    # Check existing votes
    if user in post.upvoted_by:
        if vote_type == 'downvote':
            # Move from upvote to downvote
            post.upvoted_by.remove(user)
            post.downvoted_by.append(user)
        else:
            # Remove from upvote
            post.upvoted_by.remove(user)

    elif user in post.downvoted_by:
        if vote_type == 'upvote':
            # Move from downvote to upvote
            post.downvoted_by.remove(user)
            post.upvoted_by.append(user)
        else:
            # Remove from downvote
            post.downvoted_by.remove(user)
    else:
        # New vote
        if vote_type == 'upvote':
            post.upvoted_by.append(user)
        elif vote_type == 'downvote':
            post.downvoted_by.append(user)

    # Commit changes to the database
    db.session.commit()

    return jsonify({
        "upvotes": [user.id for user in post.upvoted_by],
        "downvotes": [user.id for user in post.downvoted_by]
    }), 200

@app.route("/get-comments", methods=["POST"])
def get_comments():
    post_id = request.json.get("post_id")

    if not post_id:
        return jsonify({"error": "Missing Post ID"}), 400 
    
    post = Post.query.get(post_id)

    if not post:
        return jsonify({"error": "Post not found!"}), 404
    
    comments = Comment.query.filter_by(post_id=post_id).all()

    # Format the results into a list of dictionaries
    comments_list = []
    for comment in comments:
        user = User.query.get(comment.user_id)
        comment_data = {
            'id': comment.id,
            'content': comment.content,
            'user_id': comment.user_id,
            'username': user.username,
            'post_id': comment.post_id
        }
        comments_list.append(comment_data)

    # Return the JSON response
    return jsonify(comments_list)



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
        upvote_ids = [user.id for user in post.upvoted_by]
        downvote_ids = [user.id for user in post.downvoted_by]
        # Fetch the author and community details
        author = User.query.get(post.user_id)
        community = Community.query.get(post.community_id)

        post_details = {
            'id': post.id,
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
            'upvotes': upvote_ids,  # List of user IDs who upvoted
            'downvotes': downvote_ids,
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
    # Query the database to get the specified community
    community = Community.query.get(community_id)
    if not community:
        return jsonify({"error": "Community not found"}), 404

    # Query to get all posts for the specified community
    posts = Post.query.filter_by(community_id=community_id).all()

    # Convert the posts to a list of dictionaries for JSON serialization
    posts_list = []

    for post in posts:
        # Fetch the user details
        user = User.query.get(post.user_id)
        upvote_ids = [u.id for u in post.upvoted_by]
        downvote_ids = [u.id for u in post.downvoted_by]
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
                'name': community.name
            },
            'upvotes': upvote_ids,  # List of user IDs who upvoted
            'downvotes': downvote_ids,
        }
        posts_list.append(post_details)

    # Prepare prerequisites list
    prerequisites_list = [{
        'id': prereq.id,
        'name': prereq.name,
    } for prereq in community.prerequisites]

    # Prepare instructors list
    instructors_list = []
    for instructor in community.instructors:
        # Fetch the communities (courses) taught by the instructor
        taught_courses = [{'id': course.id, 'name': course.name} for course in instructor.communities]

        instructor_details = {
            'id': instructor.id,
            'name': instructor.name,
            'email': instructor.email,
            'bio': instructor.bio,
            'courses': taught_courses  # Add the taught courses here
        }
        instructors_list.append(instructor_details)

    # Construct the final response
    response = {
        'description': community.description,
        'prerequisites': prerequisites_list,
        'instructors': instructors_list,
        'post_list': posts_list
    }

    return jsonify(response)


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
    print("New post: " + str(new_post.id))

    return jsonify({"message": "Post created successfully"}), 201



@app.route("/hydration", methods=["POST"])
def userHydration():
    data = request.json
    user_id = data.get("id")
    water_consumed = data.get("waterConsumed")

    if user_id is None or water_consumed is None:
        return 'Invalid request. Please provide id and waterConsumed.', 400

    user = User.query.get(user_id)

    if user is None:
        return 'User not found', 404

    user.waterConsumed += water_consumed

    db.session.commit()

    return f'Water consumption updated for user ID: {user_id}', 200

@app.route("/hydration/<int:user_id>", methods=["GET"])
def getHydrationInfo(user_id):
    user = User.query.get(user_id)

    if user is None:
        return 'User not found', 404

    return jsonify({
        'user_id': user.id,
        'waterConsumed': user.waterConsumed
    }), 200

@app.route("/login", methods=["POST"])
def login_user():
    username = request.json["username"]
    password = request.json["password"]

    user = User.query.filter_by(username=username).first()

    if user is None:
        return jsonify({"error": "User does not exist."}), 401

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Password is incorrect."}), 401
    
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

@app.route("/get-profile/<string:user_id>", methods=["GET"])
def get_profile(user_id):

    print("Getting profile of user_id: " + user_id)
    profile = Profile.query.filter_by(user_id=user_id).first()

    if profile is None:
        print("Profile does not exist")
        return jsonify({"error": "Profile does not exist"}), 404

    return jsonify({
        "user_id": profile.user_id,
        "nickname": profile.nickname,
        "bio": profile.bio,
        "profile_pic": profile.profile_pic
    })

@app.route("/update-profile-pic", methods=["POST"])
def update_profile_pic():

    '''
    {
        token = [token],
        new_pic = [string]
    }
    '''

    token = request.json["token"]
    user_data = jwt.decode(token, secret_key, algorithms=["HS256"])

    if user_data is None:
        return jsonify({"error": "Token is invalid"}), 400
    
    profile = Profile.query.filter_by(user_id=user_data['id']).first()

    if profile is None:
        return jsonify({"error": "No profile found"}), 400

    new_profile_pic = request.json["new_pic"]

    if new_profile_pic:
        profile.profile_pic = new_profile_pic

    db.session.commit()

    return "200"


@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filename)

    return 'File uploaded successfully'


@app.route('/images/<filename>')
def get_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/logout", methods=["POST"])
def logout_user():
    # session.pop("user_id")
    return "200"                                               


@app.route("/delete-user", methods=["POST"])
def delete_user():

    '''
    body:
    {
        "user_id": <id of current user> replace with token later?,
        "password": <user password again>
    }
    '''

    # token = request.args.get("authToken")
    user_id = request.json["user_id"]
    password = request.json["password"]

    '''
    # EXIT 1 : Token is invalid

    if token is None:
        print("Token is invalid")
        return jsonify({"error": "Token is invalid"}), 401

    token_data = jwt.decode(token, secret_key, algorithms=["HS256"])
    user_id = token_data['id']
    '''
    
    user = User.query.filter_by(id=user_id).first()

    # EXIT 2 : User not found

    if user is None:
        print("User not found")
        return jsonify({"error": "User not found"})

    profile = Profile.query.filter_by(user_id=user_id).first()

    # EXIT 3 : Profile not found

    if profile is None:
        print("Profile not found")
        return jsonify({"error": "Profile not found"})

    # EXIT 4 : Password is incorrect

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Your password is incorrect."})

    # All checks passed: delete account

    db.session.delete(user)
    db.session.delete(profile)

    db.session.commit()

    return jsonify({"message": "Account deleted. Returning to homepage..."})
    # Note: Frontend should redirect to login after


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
    communities_list = []
    for community in communities:
        # Fetch prerequisites and instructors for each community
        prerequisites_list = [{'id': prereq.id, 'name': prereq.name} for prereq in community.prerequisites]
        instructors_list = [{'id': instructor.id, 'name': instructor.name, 'email': instructor.email, 'bio': instructor.bio} for instructor in community.instructors]

        # Add community details along with prerequisites and instructors
        community_details = {
            'id': community.id,
            'name': community.name,
            'description': community.description,
            'prerequisites': prerequisites_list,
            'instructors': instructors_list
        }
        communities_list.append(community_details)

    # Return the list as JSON
    try:
        return jsonify(communities_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500




@socketio.on("message")
def handleMessage(msg):
    print(msg)
    send(msg, broadcast=True)
    return None




@socketio.on('send_message')
def handle_send_message(data):
    try:
        user_id = data['user_id']
        chatbox_id = data['chatbox_id']
        message_content = data['message']

        # Create a new message instance
        new_message = PrivateMessage(user_id=user_id, chatbox_id=chatbox_id, content=message_content)
        
        # Add the new message to the database
        db.session.add(new_message)
        db.session.commit()

        # Fetch the user to include user details in the message data
        user = User.query.get(user_id)

        # Prepare message data to send back to clients
        message_data = {
            'user_id': user_id,
            'chatbox_id': chatbox_id,
            'content': message_content,
            'timestamp': new_message.timestamp.isoformat(),  # Send timestamp as ISO format string
            'username': user.username if user else 'Unknown User'
        }

        # Emit the message to all clients connected to this chatbox
        emit('new_message', message_data, to=str(chatbox_id))  # Ensure chatbox_id is a string if it's used as a room name

    except Exception as e:
        print(f"An error occurred: {e}")
        emit('error', {'message': 'Error in sending message'})



@app.route("/user-chatboxes/<int:user_id>", methods=["GET"])
def get_user_chatboxes(user_id):
    # Fetch the user by ID
    user = User.query.get(user_id)

    # Check if the user exists
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Get all chatboxes the user is associated with
    user_chatboxes = user.chatboxes

    chatboxes_list = []
    for chatbox in user_chatboxes:
        # Find the other user in the chatbox
        other_user = next(u for u in chatbox.users if u.id != user_id)

        # Find the last message in the chatbox (if any)
        last_message = PrivateMessage.query.filter_by(chatbox_id=chatbox.id).order_by(PrivateMessage.timestamp.desc()).first()
        last_message_content = last_message.content if last_message else None

        chatbox_details = {
            'chatbox_id': chatbox.id,
            'other_user_username': other_user.username,
            'last_message': last_message_content,
        }
        chatboxes_list.append(chatbox_details)

    # Return the list as JSON
    return jsonify(chatboxes_list), 200


@app.route("/messages/<int:chatbox_id>", methods=["GET"])
def get_chatbox_messages(chatbox_id):
    try:
        # Query for messages in the chatbox
        messages = PrivateMessage.query.filter_by(chatbox_id=chatbox_id).order_by(PrivateMessage.timestamp).all()

        # Transform messages into a JSON-friendly format
        messages_list = [{
            'id': message.id,
            'user_id': message.user_id,
            'chatbox_id': message.chatbox_id,
            'content': message.content,
            'timestamp': message.timestamp.isoformat()  # Convert datetime to string
        } for message in messages]

        return jsonify(messages_list), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "Error fetching messages"}), 500


@app.route("/check-create-chatbox", methods=["POST"])
def check_or_create_chatbox():
    data = request.json
    user1_id = data['user1_id']
    user2_id = data['user2_id']

    # Aliases for user_chatbox_association table
    uca1 = user_chatbox_association.alias()
    uca2 = user_chatbox_association.alias()

    # Query to find existing chatbox between these two users
    existing_chatbox = Chatbox.query \
        .join(uca1, Chatbox.id == uca1.c.chatbox_id) \
        .filter(uca1.c.user_id == user1_id) \
        .join(uca2, Chatbox.id == uca2.c.chatbox_id) \
        .filter(uca2.c.user_id == user2_id) \
        .first()

    if existing_chatbox:
        # Chatbox already exists
        chatbox_id = existing_chatbox.id
    else:
        # Create a new Chatbox
        new_chatbox = Chatbox()
        db.session.add(new_chatbox)
        db.session.commit()

        # Associate users with the new chatbox
        association1 = user_chatbox_association.insert().values(user_id=user1_id, chatbox_id=new_chatbox.id)
        association2 = user_chatbox_association.insert().values(user_id=user2_id, chatbox_id=new_chatbox.id)
        db.session.execute(association1)
        db.session.execute(association2)
        db.session.commit()

        chatbox_id = new_chatbox.id

    # Return chatbox information
    return jsonify({"chatbox_id": chatbox_id}), 200


if __name__ == "__main__":

    # Start the Flask application
    socketio.run(app, port=8000)
