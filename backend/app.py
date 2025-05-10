import os
from flask import Flask, request, jsonify, send_from_directory, url_for, make_response
from flask_mail import Message as MailMessage
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import Enum
import jwt
from functools import wraps
from datetime import datetime, timedelta
from flask_mail import Mail
from flask_cors import CORS



##############################################PARTIE AMINE####################################################
import numpy as np
import pandas as pd
from lightfm import LightFM
from lightfm.data import Dataset
import unicodedata
import random
from fuzzywuzzy import process
import pickle
import os
##################################################################################################################


app = Flask(__name__,template_folder='templates')
CORS(app, origins=["http://localhost:3000"])
app.config['SECRET_KEY'] = '59c9d8576f920846140e2a8985911bec588c08aebf4c7799ba0d5ae388393703'  
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:amino159753@localhost/metascout"
db = SQLAlchemy(app)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'layouni.nourelhouda@gmail.com'
app.config['MAIL_PASSWORD'] = 'kvni phac wprf smll'
mail = Mail(app)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    profile_image = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(80), nullable=False)




class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    content = db.Column(db.Text)
    image_url = db.Column(db.String(255), nullable=True)
    video_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='posts', lazy=True)
    def to_dict(self):
        return {
            'post_id': self.post_id,
            'user_id': self.user_id,
            'content': self.content,
            'image_url': self.image_url,
            'video_url': self.video_url,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')  
        }

    def __init__(self, user_id, content, image_url=None, video_url=None):
        self.user_id = user_id
        self.content = content
        self.image_url = image_url
        self.video_url = video_url

    def __repr__(self):
        return f'<Post {self.post_id}>'
class Reaction(db.Model):
    reaction_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'))
    user_id = db.Column(db.Integer)
    reaction_type = db.Column(Enum('like', 'love', 'laugh', 'wow', 'angry', 'sad',name="reaction_type_enum"))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'))
    user_id = db.Column(db.Integer)
    comment_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Share(db.Model):
    share_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'))
    user_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    seen = db.Column(db.Boolean, default=False) 
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)


class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    last_message_time = db.Column(db.DateTime, default=db.func.current_timestamp())


########################################################PARTIE AMINE############################################################
# Global variables for models (add near top)
recommendation_models = None
model_loaded = False

#class
class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recommended_club = db.Column(db.String(255))
    recommended_player = db.Column(db.String(255))
    recommended_agency = db.Column(db.String(255))

    club_id = db.Column(db.Integer)  # Optional
    player_id = db.Column(db.Integer)  # Optional
    agency_id = db.Column(db.Integer)  # Optional

    score = db.Column(db.Float)
    model_version = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    viewed = db.Column(db.Boolean, default=False)

# I CHANGED THE TOKEN    
# #############################################################################################################################   

#def token_required(f):
#    @wraps(f)
#    def decorated(*args, **kwargs):
#        token = request.headers.get('Authorization')

 #       if not token:
  #          return jsonify({'message': 'Token is missing!'}), 401
#
 #       try:
  #          decoded_token = jwt.decode(token.split(" ")[1], app.config['SECRET_KEY'], algorithms=['HS256'])
   #         current_user = User.query.get(decoded_token['user_id'])
    #    except:
     #       return jsonify({'message': 'Token is invalid!'}), 401
#
 #       return f(current_user, *args, **kwargs)
    
  #  return decorated
##################################################################################################################################3  

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        print(f"🔑 Raw Authorization header: {token}")  # Debug
        
        if not token:
            print("❌ No token provided")
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Extract token (remove "Bearer " prefix if present)
            token = token.split(" ")[1] if " " in token else token
            print(f"🔍 Token after extraction: {token}")
            
            decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            print(f"📄 Decoded token: {decoded_token}")
            
            # Use 'public_id' (matching your login endpoint)
            current_user = User.query.get(decoded_token['public_id'])
            if not current_user:
                print(f"❌ User not found for public_id: {decoded_token['public_id']}")
                return jsonify({'message': 'Invalid user!'}), 401
                
        except jwt.ExpiredSignatureError:
            print("❌ Token expired")
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            print("❌ Invalid token")
            return jsonify({'message': 'Token is invalid!'}), 401
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            return jsonify({'message': 'Token verification failed!'}), 401

        print(f"✅ Authenticated as user ID: {current_user.id}")
        return f(current_user, *args, **kwargs)
    return decorated


@app.route('/')
def hello():
    return 'Hey!'

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    
    # Validate the sender and receiver
    sender = User.query.get(data['sender_id'])
    receiver = User.query.get(data['receiver_id'])
    
    if not sender or not receiver:
        return jsonify({'message': 'Invalid sender or receiver'}), 400
    
    # Create a new message
    new_message = Message(
        sender_id=data['sender_id'],
        receiver_id=data['receiver_id'],
        message=data['message'],
        seen=False,
        conversation_id=data['conversation_id']
    )
    
    db.session.add(new_message)
    db.session.commit()
    
    # Return the new message
    return jsonify({
        'message': 'Message sent successfully',
        'message_id': new_message.id,
        'sender_id': new_message.sender_id,
        'receiver_id': new_message.receiver_id,
        'message': new_message.message,
        'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }), 201

@app.route('/mark_message_seen/<int:message_id>', methods=['POST'])
def mark_message_seen(message_id):
    message = Message.query.get(message_id)
    
    if message:
        message.seen = True
        db.session.commit()
        return jsonify({'message': 'Message marked as seen'}), 200
    else:
        return jsonify({'message': 'Message not found'}), 404

@app.route('/get_messages/<int:user1_id>/<int:user2_id>', methods=['GET'])
def get_messages(user1_id, user2_id):
    messages = Message.query.filter(
        (Message.sender_id == user1_id and Message.receiver_id == user2_id) |
        (Message.sender_id == user2_id and Message.receiver_id == user1_id)
    ).order_by(Message.timestamp.asc()).all()  # Order by timestamp
    
    # Fetch the user profiles (assuming there is a User model)
    user1 = User.query.get(user1_id)
    user2 = User.query.get(user2_id)

    message_list = []
    for msg in messages:
        # Determine the sender and receiver's profile image
        sender_image = user1.profile_image if msg.sender_id == user1_id else user2.profile_image
        receiver_image = user1.profile_image if msg.receiver_id == user1_id else user2.profile_image
        
        message_list.append({
            'id': msg.id,
            'sender_id': msg.sender_id,
            'receiver_id': msg.receiver_id,
            'message': msg.message,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'sender_image': sender_image,
            'receiver_image': receiver_image,
            'seen': msg.seen
        })
    
    return jsonify(message_list), 200

@app.route('/create_conversation', methods=['POST'])
def create_conversation():
    data = request.get_json()
    
    # Check if conversation already exists
    conversation = Conversation.query.filter(
        ((Conversation.user1_id == data['user1_id']) & (Conversation.user2_id == data['user2_id'])) |
        ((Conversation.user1_id == data['user2_id']) & (Conversation.user2_id == data['user1_id']))
    ).first()
    
    if not conversation:
        # Create new conversation
        new_conversation = Conversation(
            user1_id=data['user1_id'],
            user2_id=data['user2_id']
        )
        db.session.add(new_conversation)
        db.session.commit()
        return jsonify({'message': 'Conversation created successfully', 'conversation_id': new_conversation.id}), 201
    
    return jsonify({'message': 'Conversation already exists', 'conversation_id': conversation.id}), 200

@app.route('/get_conversations/<int:user_id>', methods=['GET'])
def get_conversations(user_id):
    try:
        # Get conversations for the user (either user1_id or user2_id)
        conversations = db.session.query(Conversation).filter(
            (Conversation.user1_id == user_id) | (Conversation.user2_id == user_id)
        ).all()

        # Prepare the conversation data
        conversations_data = []
        for conversation in conversations:
            # Get the other user in the conversation
            other_user_id = conversation.user1_id if conversation.user2_id == user_id else conversation.user2_id
            other_user = db.session.query(User).filter_by(id=other_user_id).first()

            # Get the last message in the conversation
            last_message = db.session.query(Message).filter_by(conversation_id=conversation.id).order_by(Message.timestamp.desc()).first()
            
            last_message_text = last_message.message if last_message else "No messages yet"
            last_time = last_message.timestamp if last_message else datetime.utcnow()

            # Count the unread messages where the logged-in user is the receiver and the message is not seen
            unread_count = db.session.query(Message).filter(
                Message.conversation_id == conversation.id,
                Message.receiver_id == user_id,  # Ensure the logged-in user is the receiver
                Message.seen == False  # Only count unread messages
            ).count()

            conversations_data.append({
                'id': other_user.id,
                'name': other_user.name,
                'profile_image': other_user.profile_image,
                'last_message': last_message_text,
                'last_time': last_time.strftime('%Y-%m-%d %H:%M:%S'),
                'unread_count': unread_count,
                'conversation_id': conversation.id
            })

        return jsonify(conversations_data), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


    except Exception as e:
        print(f"Error fetching conversations: {e}")
        return jsonify({"error": "An error occurred while fetching conversations."}), 500

@app.route('/get_post_by_id/<int:post_id>', methods=['GET'])
def get_post_by_id(post_id):
    post = Post.query.get(post_id)
    
    if post:
        return jsonify({
            'id': post.post_id,
            'user_id': post.user_id,
            'content': post.content,
            'image_url': post.image_url,
            'video_url': post.video_url,
            'created_at': post.created_at
        })
    else:
        return jsonify({'message': 'Post not found'}), 404
    
@app.route('/get_user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        profile_image = user.profile_image.replace("\\", "/")  


        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'name': user.name,
            'profile_image': profile_image 
        }), 200
    except Exception as e:
        print(f"Error fetching user data: {e}")
        return jsonify({'message': 'User not found'}), 404

@app.route('/register', methods=['POST'])
def register():
    try:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return jsonify({'message': 'Username or email already exists'}), 409

        profile_image = request.files.get('profile_image')
        profile_image_path = None
        if profile_image and allowed_file(profile_image.filename):
            filename = secure_filename(profile_image.filename)
            profile_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_image.save(profile_image_path) 

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(username=username, email=email, password=hashed_password, name=name, profile_image=profile_image_path)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred. Please try again.'}), 500

@app.route('/me', methods=['GET'])
def get_userId():
    token = request.cookies.get('token')
    if not token:
        return jsonify({'message': 'Token is missing!'}), 401

    try:
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded_token['user_id']
        return jsonify({'user_id': user_id})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401
    
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    
    # Check if user exists and password matches
    if user and check_password_hash(user.password, password):
        # Create JWT token with expiration of 24 hours
        token = jwt.encode({
            'public_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, app.config['SECRET_KEY'])
        return jsonify({'token': str(token)}) ,200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401
    
@app.route('/resetPassword', methods=['PUT'])
def reset_password():
    token = request.json['token']
    newPassword = request.json['newPassword']
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['public_id']

        user = User.query.filter_by(id=user_id).first()
        if user:
            user.password = generate_password_hash(newPassword, method='pbkdf2:sha256')
            db.session.commit()
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'message': 'Utilisateur introuvable'}), 404
    except jwt.ExpiredSignatureError:
        return jsonify({'success': False, 'message': 'Session expirée'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'success': False, 'message': 'Invalid token'}), 401

def send_reset_email(email, user_id):
    token = jwt.encode({'public_id': user_id, 'exp': datetime.utcnow() + timedelta(hours=24)}, app.config['SECRET_KEY'], algorithm='HS256')
    subject = "Réinitialiser votre mot de passe"
    reset_link = f"http://localhost:3000/ResetPassword?token={str(token)}"

    msg = MailMessage(subject="Réinitialiser votre mot de passe",
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[email])
    msg.html = f"""
            <p>Hello,</p>
            <p>Click on the link to reset your password: {reset_link}</p>
            <p>Best regards,<br>The MetaScout Team</p>
        """
    mail.send(msg)

@app.route('/reset', methods=['POST'])
def reset():
    username = request.json['username']
    email = request.json['email']
    user = User.query.filter_by(username=username).first()
    
    if user: 
                send_reset_email(email, user.id)
                return jsonify({"message": "mail envoyé"}), 200
    else:
        return jsonify({"error": "email introuvable"}), 401

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/create_post', methods=['POST'])
def create_post():
    if 'text' not in request.form:
        return jsonify({'error': 'No text content provided'}), 400

    post_content = request.form['text']
    user_id = request.form['user_id']

    uploaded_image = None
    uploaded_video = None

    if 'image' in request.files:
        image_file = request.files['image']
        if image_file and allowed_file(image_file.filename):
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)
            uploaded_image = url_for('uploaded_file', filename=image_filename)

    if 'video' in request.files:
        video_file = request.files['video']
        if video_file and allowed_file(video_file.filename):
            video_filename = secure_filename(video_file.filename)
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
            video_file.save(video_path)
            uploaded_video = url_for('uploaded_file', filename=video_filename)

    post = Post(user_id=user_id, content=post_content, image_url=uploaded_image, video_url=uploaded_video)
    db.session.add(post)
    db.session.commit()

    return jsonify({
        'message': 'Post created successfully',
        'post_content': post_content,
        'image_url': uploaded_image,
        'video_url': uploaded_video
    })

@app.route('/get_posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    posts_data = []

    # Fetch all reactions in a single query to optimize performance
    reactions_data = db.session.query(
        Reaction.post_id,
        Reaction.reaction_type,
        db.func.count(Reaction.reaction_id)
    ).group_by(Reaction.post_id, Reaction.reaction_type).all()

    # Organize reactions into a dictionary for quick lookup
    reactions_dict = {}
    for post_id, reaction_type, count in reactions_data:
        if post_id not in reactions_dict:
            reactions_dict[post_id] = {}
        reactions_dict[post_id][reaction_type] = count

    for post in posts:
        post_reactions = reactions_dict.get(post.post_id, {})

        # Fetch comments for the current post
        comments = Comment.query.filter_by(post_id=post.post_id).all()
        comments_data = [{
            'user_id': comment.user_id,
            'comment_text': comment.comment_text,
            'created_at': comment.created_at
        } for comment in comments]

        posts_data.append({
            'id': post.post_id,
            'user_id': post.user_id,
            'user_name': post.user.name,
            'content': post.content,
            'image_url': post.image_url,
            'video_url': post.video_url,
            'likes': post_reactions.get('like', 0),
            'loves': post_reactions.get('love', 0),
            'laughs': post_reactions.get('laugh', 0),
            'wows': post_reactions.get('wow', 0),
            'angrys': post_reactions.get('angry', 0),
            'sads': post_reactions.get('sad', 0),
            'created_at': post.created_at,
            'comments': comments_data  # Add comments data
        })

    return jsonify(posts_data), 200

@app.route('/get_comments/<int:post_id>', methods=['GET'])
def get_comments(post_id):
    comments = Comment.query.filter_by(post_id=post_id).all()
    
    comments_data = [
        {
            'id': comment.comment_id,
            'post_id': comment.post_id,
            'user_id': comment.user_id,
            'comment_text': comment.comment_text,
            'created_at': comment.created_at
        }
        for comment in comments
    ]
    
    return jsonify(comments_data), 200


@app.route('/react_to_post', methods=['POST'])
def react_to_post():
    data = request.get_json()
    user_id = data.get('user_id')
    post_id = data.get('post_id')
    reaction_type = data.get('reaction_type')

    if not user_id or not post_id or not reaction_type:
        return jsonify({'error': 'Missing data'}), 400

    reaction = Reaction.query.filter_by(user_id=user_id, post_id=post_id).first()

    if reaction:
        if reaction.reaction_type == reaction_type:
            db.session.delete(reaction)  # Remove reaction if it's the same
            message = "Reaction removed"
        else:
            reaction.reaction_type = reaction_type  # Update reaction type
            message = "Reaction updated"
    else:
        new_reaction = Reaction(user_id=user_id, post_id=post_id, reaction_type=reaction_type)
        db.session.add(new_reaction)
        message = "Reaction added"

    db.session.commit()
    return jsonify({'message': message}), 200


@app.route('/add_comment', methods=['POST'])
def add_comment():
    data = request.json
    new_comment = Comment(**data)
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({'message': 'Comment added'})




####################################################################################################################################
#####################################################################################################################################    
#          PARTIE AMINE

##recherche

@app.route('/search', methods=['GET'])
def search_users():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    # Search for users matching the query
    users = User.query.filter(
        User.username.ilike(f'%{query}%') | 
        User.name.ilike(f'%{query}%')
    ).limit(10).all()
    
    # Format the results with clean paths
    results = [{

        'username': user.username,
        'profile_image': user.profile_image.replace("\\", "/") if user.profile_image else None,
    } for user in users]
    
    return jsonify(results)

@app.route('/user/<username>', methods=['GET'])
def get_user_profile(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'username': user.username,
        'name': user.name,
        'profile_image': user.profile_image.replace("\\", "/") if user.profile_image else None,
    })


####################################recommendation##########################################################3
def load_recommendation_models():
    global recommendation_models
    try:
        model_path = os.path.join(os.path.dirname(__file__), 'models', 'recommendation_models.pkl')
        print(f"Attempting to load models from: {model_path}")
        
        if not os.path.exists(model_path):
            print("❌ Error: Model file not found")
            return
            
        with open(model_path, 'rb') as f:
            recommendation_models = pickle.load(f)
            
            # Validate required keys
            required_keys = {
                'club_model', 'player_model', 'club_dataset', 
                'player_dataset', 'club_id_to_name'
            }
            if not all(key in recommendation_models for key in required_keys):
                missing = required_keys - recommendation_models.keys()
                raise KeyError(f"Missing required model components: {missing}")
                
            print("✅ Successfully loaded and validated models")
    except Exception as e:
        print(f"❌ Load error: {str(e)}")
        recommendation_models = None
        



# Call this when starting your app
load_recommendation_models()

# Add this helper function at the top of your file
def get_user_type(current_user, recommendation_models):
    # Agency = user in club dataset
    if current_user.role == "Agency":
        return 'agency'
    # Player = item in player dataset (agencys recommend players)
    elif current_user.role == "player":
        return 'player'
    elif current_user.role == "Club":
        return 'club'
    elif current_user.role == "Agent":
        return 'agent'
    else:
        return 'staff'




##########################################################################33    
# CLUBS TO AGENCY
@app.route('/api/recommend/clubs/toagency', methods=['POST'])
@token_required
def recommend_clubs(current_user):
    try:
        user_type = get_user_type(current_user, recommendation_models)
        print(user_type)
        if user_type != 'agency':
            return jsonify({'message': 'No club recommendations available (user is not an agency)'}), 200
            
        data = request.get_json() or {}
        top_n = min(int(data.get('top_n', 5)), 20)
        
        if not recommendation_models:
            return jsonify({'error': 'Recommendation system not ready'}), 503

        # Get models and mappings
        model = recommendation_models['club_model']
        agency_id_map = recommendation_models['agency_id_map_club']
        club_id_map = recommendation_models['club_id_map']
        id_to_club = recommendation_models['id_to_club']
        club_id_to_name = recommendation_models['club_id_to_name']

        # Get agency index
        agency_idx = agency_id_map.get(str(current_user.id))
        if agency_idx is None:
            return jsonify([])
            
        # Get predictions
        scores = model.predict(agency_idx, np.arange(len(club_id_map)))
        top_indices = np.argsort(-scores)[:top_n]
        
        # Prepare recommendations
        recommendations = []
        for idx in top_indices:
            club_id = id_to_club[idx]
            recommendations.append({
                'club': club_id_to_name.get(club_id, "Unknown Club"),
                'score': float(scores[idx]),
                'club_id': club_id,
                'recommended_stars': score_to_stars(float(scores[idx]))

            })
        
        # Save to database  
        for rec in recommendations:
            db.session.add(Recommendation(
                user_id=current_user.id,
                recommended_club=rec['club'],
                club_id=rec['club_id'],
                score=rec['score']
            ))
        db.session.commit()
        
        return jsonify(recommendations)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# PLAYERS TO AGENCY
@app.route('/api/recommend/players/toagency', methods=['POST'])
@token_required
def recommend_players(current_user):
    try:
        user_type = get_user_type(current_user, recommendation_models)
        print(user_type)
        if user_type != 'agency':
            return jsonify({'message': 'No player recommendations available (user is not an agency)'}), 200
            
        data = request.get_json() or {}
        top_n = min(int(data.get('top_n', 5)), 20)
        
        if not recommendation_models:
            return jsonify({'error': 'Recommendation system not ready'}), 503

        # Get models and mappings
        model = recommendation_models['player_model']
        agency_id_map = recommendation_models['agency_id_map_player']
        player_id_map = recommendation_models['player_id_map']
        id_to_player = recommendation_models['id_to_player']
        player_id_to_name = recommendation_models['player_id_to_name']

        # Get agency index
        agency_idx = agency_id_map.get(str(current_user.id))
        if agency_idx is None:
            return jsonify([])
            
        # Get predictions
        scores = model.predict(agency_idx, np.arange(len(player_id_map)))
        top_indices = np.argsort(-scores)[:top_n]
        
        # Prepare recommendations
        recommendations = []
        for idx in top_indices:
            player_id = id_to_player[idx]
            recommendations.append({
                'player': player_id_to_name.get(player_id, "Unknown Player"),
                'score': float(scores[idx]),
                'player_id': player_id,
                'recommended_stars': score_to_stars(float(scores[idx]))

            })

        # Save to database
        for rec in recommendations:
            db.session.add(Recommendation(
                user_id=current_user.id,
                recommended_player=rec['player'],
                player_id=rec['player_id'],
                score=rec['score']
            ))
        db.session.commit()
            
        return jsonify(recommendations)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


#Agencies to PLayers
@app.route('/api/recommend/agencies/toplayer', methods=['POST'])
@token_required
def recommend_agencies(current_user):      
    try:
        user_type = get_user_type(current_user, recommendation_models)
        print(user_type)
        if user_type != 'player':
            return jsonify({'message': 'No player recommendations available (user is not an agency)'}), 200
            
        data = request.get_json() or {}
        top_n = min(int(data.get('top_n', 5)), 20)
        
        if not recommendation_models:
            return jsonify({'error': 'Recommendation system not ready'}), 503
        
        # Get all required models and mappings
        model = recommendation_models['player_model']
        player_id_map = recommendation_models['player_id_map']
        agency_id_map = recommendation_models['agency_id_map_player']
        id_to_agency = recommendation_models['id_to_agency_player']
        agency_id_to_name = recommendation_models['agency_id_to_name']

        # Verify player exists
        player_idx = player_id_map.get(str(current_user.id))
        if player_idx is None:
            return jsonify([])

        # Get top_n parameter
        data = request.get_json() or {}
        top_n = min(int(data.get('top_n', 5)), 20)

        # Get predictions (EXACTLY like Jupyter)
        scores = model.predict(
            user_ids=np.arange(len(agency_id_map)),
            item_ids=np.repeat(player_idx, len(agency_id_map))
        )

        # Build recommendations (EXACT Jupyter logic)
        recommendations = []
        for idx in np.argsort(-scores):
            agency_id = id_to_agency[idx]
            agency_name = agency_id_to_name.get(agency_id, agency_id)
            
            # Skip NaN like Jupyter
            if pd.isna(agency_name):
                continue
                
            recommendations.append({
                'agency': str(agency_name),
                'score': float(scores[idx]),
                'recommended_stars': score_to_stars(float(scores[idx])),
                'agency_id': agency_id

            })
            
            # Stop when we have enough valid recommendations
            if len(recommendations) >= top_n:
                break

        return jsonify(recommendations)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
        

# CLUBS TO PLAYER
@app.route('/api/recommend/clubs/toplayer', methods=['POST'])
@token_required
def recommend_clubs_to_player(current_user):
    try:
        user_type = get_user_type(current_user, recommendation_models)
        print(user_type)
        if user_type != 'player':
            return jsonify({'message': 'No player recommendations available (user is not an agency)'}), 200
        # Convert to string for consistent comparison
        player_id = str(current_user.id)

        # Load required data
        transfer_df = recommendation_models['transfer_df']
        agency_id_map_club = recommendation_models['agency_id_map_club']
        club_model = recommendation_models['club_model']
        club_id_map = recommendation_models['club_id_map']
        id_to_club = recommendation_models['id_to_club']
        club_id_to_name = recommendation_models['club_id_to_name']

        # Find representing agencies
        player_agencies = set(
            transfer_df[transfer_df['Player Id'].astype(str) == player_id]['Agency Id'].astype(str).unique()
        )

        if not player_agencies:
            return jsonify([])

        # Predict and aggregate scores
        all_scores = np.zeros(len(club_id_map))
        valid_agencies = 0
        
        for agency_id in player_agencies:
            if agency_id in agency_id_map_club:
                agency_idx = agency_id_map_club[agency_id]
                all_scores += club_model.predict(agency_idx, np.arange(len(club_id_map)))
                valid_agencies += 1

        if valid_agencies == 0:
            return jsonify({'message': 'No valid agency mappings found'}), 200

        # Prepare results
        recommendations = []
        for idx in np.argsort(-all_scores)[:3]:  # Return top 3 as requested
            club_id = id_to_club.get(idx, f"unknown_{idx}")
            club_name = club_id_to_name.get(club_id, f"Club_{club_id}")
            
            if pd.isna(club_name):
                continue
                
            recommendations.append({
                'club': str(club_name),
                'score': float(all_scores[idx]),
                'club_id': str(club_id),
                'recommended_stars': score_to_stars(float(all_scores[idx]))

            })

        return jsonify(recommendations)

    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500



@app.route('/api/recommend/players/toclub', methods=['POST'])
@token_required
def recommend_players_to_club(current_user):
    try:
        # Debug print
        print(f"\n=== Starting recommendations for club ID: {current_user.id} ===")

        # Verify user is a club
        user_type = get_user_type(current_user, recommendation_models)
        if user_type != 'club':
            return jsonify({'message': 'No player recommendations available (user is not a club)'}), 200

        # Get parameters
        data = request.get_json() or {}
        try:
            top_n = min(int(data.get('top_n', 5)), 20)
        except ValueError:
            return jsonify({'error': 'Invalid top_n parameter - must be an integer'}), 400

        # Load necessary models and mappings
        club_model = recommendation_models['club_model']
        player_model = recommendation_models['player_model']
        agency_id_map_club = recommendation_models['agency_id_map_club']
        agency_id_map_player = recommendation_models['agency_id_map_player']
        club_id_map = recommendation_models['club_id_map']
        player_id_map = recommendation_models['player_id_map']
        player_id_to_name = recommendation_models['player_id_to_name']
        id_to_player = recommendation_models['id_to_player']

        # Map current club to index
        club_norm = str(current_user.id)  # Assuming club ID is already normalized
        if club_norm not in club_id_map:
            print(f"Club ID {club_norm} not found in club_id_map")
            return jsonify({'message': 'No player recommendations available for this club'}), 200
        
        club_idx = club_id_map[club_norm]
        print(f"Club index: {club_idx}")

        # Get all agencies that work with this club (from transfer data)
        transfer_df = recommendation_models['transfer_df']
        club_agencies = set(transfer_df[transfer_df['Club_norm'] == club_norm]['Agency_norm'])
        
        if not club_agencies:
            print("No agencies found for this club")
            return jsonify([])

        print(f"Found {len(club_agencies)} associated agencies")

        # Initialize and calculate scores
        num_players = len(player_id_map)
        all_scores = np.zeros(num_players)
        
        valid_agency_count = 0
        for agency in club_agencies:
            if agency in agency_id_map_player:
                agency_idx = agency_id_map_player[agency]
                all_scores += player_model.predict(agency_idx, np.arange(num_players))
                valid_agency_count += 1

        if valid_agency_count == 0:
            print("No valid agency-player mappings found")
            return jsonify({'message': 'No valid player mappings found'}), 200

        # Normalize scores
        all_scores /= valid_agency_count
        
        # Adjust negative scores if needed
        if np.all(all_scores < 0):
            all_scores += 2

        # Get top recommendations
        recommendations = []
        for idx in np.argsort(-all_scores)[:top_n]:
            player_id = id_to_player.get(idx)
            player_name = player_id_to_name.get(player_id, f"Player {player_id}")
            score = float(all_scores[idx])
            
            recommendations.append({
                'player_id': player_id,
                'player': player_name,
                'score': score,
                'recommended_stars': score_to_stars(score)
            })

        print(f"Generated {len(recommendations)} recommendations")
        print("Sample recommendation:", recommendations[0] if recommendations else "None")

        return jsonify({
            'success': True,
            'club_id': current_user.id,
            'recommendations': recommendations
        })

    except Exception as e:
        print(f"Error in recommend_players_to_club: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500




#AGENCIES TO CLUB
@app.route('/api/recommend/agencies/toclub', methods=['POST'])
@token_required
def recommend_agencies_to_club(current_user):
    try:
        # Verify club
        user_type = get_user_type(current_user, recommendation_models)
        if user_type != 'club':
            return jsonify({'message': 'No agency recommendations available (user is not a club)'}), 200

        # Get parameters
        data = request.get_json() or {}
        top_n = min(int(data.get('top_n', 5)), 20)

        if not recommendation_models:
            return jsonify({'error': 'Recommendation system not ready'}), 503

        # Get models and mappings
        model = recommendation_models['club_model']
        club_id_map = recommendation_models['club_id_map']
        agency_id_map = recommendation_models['agency_id_map_club']
        id_to_agency = recommendation_models['id_to_agency_club']
        agency_id_to_name = recommendation_models['agency_id_to_name']

        # Verify club exists
        club_idx = club_id_map.get(str(current_user.id))
        if club_idx is None:
           return jsonify([])

        # Get predictions
        scores = model.predict(
            user_ids=np.arange(len(agency_id_map)),
            item_ids=np.repeat(club_idx, len(agency_id_map))
        )

        # Build recommendations
        recommendations = []
        for idx in np.argsort(-scores):
            agency_id = id_to_agency[idx]
            agency_name = agency_id_to_name.get(agency_id, agency_id)
            
            # Skip NaN values
            if pd.isna(agency_name):
                continue
                
            recommendations.append({
                'agency': str(agency_name),
                'score': float(scores[idx]),
                'agency_id': agency_id,
                'recommended_stars': score_to_stars(float(scores[idx]))

            })
            
            if len(recommendations) >= top_n:
                break

        return jsonify(recommendations)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


#Agents to agency
@app.route('/api/recommend/agents/toagency', methods=['POST'])
@token_required
def recommend_agents_to_agency(current_user):
    try:
        # Ensure user is an agent (since we're recommending agencies to agents)
        user_type = get_user_type(current_user, recommendation_models)
        if user_type != 'agency':
            return jsonify({'message': 'No agency recommendations available (user is not an agent)'}), 200

        data = request.get_json() or {}
        top_n = min(int(data.get('top_n', 5)), 20)

        if not recommendation_models:
            return jsonify({'error': 'Recommendation system not ready'}), 503

        # Load the correct models and mappings
        model = recommendation_models['agents_model']
        id_to_agency_agent = recommendation_models.get('id_to_agency_agent', {})
        agency_id_to_name = recommendation_models.get('agency_id_to_name', {})
        agents_to_name = recommendation_models.get('agents_to_name', {})
        agent_id_map_agency = recommendation_models.get('agent_id_map_agency', {})

        # Get and normalize agent name
        agent_name = current_user.name.strip().lower()

        # Find agent ID and index with safety checks
        agent_id = None
        for aid, name in agents_to_name.items():
            if str(name).strip().lower() == agent_name:
                agent_id = aid
                break

        if agent_id is None or agent_id not in agent_id_map_agency:
            return jsonify([])

        agent_idx = agent_id_map_agency.get(agent_id)
        if agent_idx is None:
            return jsonify([])

        # Predict scores - agents recommending agencies
        scores = model.predict(
            user_ids=np.repeat(agent_idx, len(id_to_agency_agent)),
            item_ids=np.arange(len(id_to_agency_agent))
        )

        # Build recommendations with all safety checks
        recommendations = []
        valid_count = 0
        
        for idx in np.argsort(-scores):  # Sort by descending score
            if valid_count >= top_n:
                break
                
            agency_id = id_to_agency_agent.get(idx)
            if agency_id is None:
                continue
                
            agency_name = agency_id_to_name.get(agency_id)
            if agency_name is None or pd.isna(agency_name):
                continue
                
            try:
                recommendations.append({
                    'agency': str(agency_name),
                    'score': float(scores[idx]),
                    'agency_id': str(agency_id),
                    'recommended_stars': score_to_stars(float(scores[idx]))
                })
                valid_count += 1
            except (ValueError, TypeError):
                continue

        return jsonify(recommendations)

    except Exception as e:
        return jsonify({'error': str(e)}), 500





#agencies agent
@app.route('/api/recommend/agencies/toagent', methods=['POST'])
@token_required
def recommend_agencies_to_agent(current_user):
    try:
        # Ensure user is an agent
        user_type = get_user_type(current_user, recommendation_models)
        if user_type != 'agent':
            return jsonify({'message': 'No agency recommendations available (user is not an agent)'}), 200

        data = request.get_json() or {}
        top_n = min(int(data.get('top_n', 5)), 20)

        if not recommendation_models:
            return jsonify({'error': 'Recommendation system not ready'}), 503

        model = recommendation_models['agents_model']
        id_to_agency_agent = recommendation_models['id_to_agency_agent']
        id_to_agent_agency = recommendation_models['id_to_agent_agency']
        agency_id_to_name = recommendation_models['agency_id_to_name']

        agent_name = current_user.name.strip().lower()

        # Map agent name directly to index
        agent_idx = None
        for idx, agent_id in id_to_agent_agency.items():
            if str(agent_id).strip().lower() == agent_name:
                agent_idx = idx
                break

        if agent_idx is None:
            return jsonify([])

        # Predict scores
        scores = model.predict(
            user_ids=np.repeat(agent_idx, len(id_to_agency_agent)),
            item_ids=np.arange(len(id_to_agency_agent))
        )

        recommendations = []
        for idx in np.argsort(-scores):
            agency_id = id_to_agency_agent.get(idx)
            agency_name = agency_id_to_name.get(agency_id, agency_id)
            if pd.isna(agency_name):
                continue
            recommendations.append({
                'agency': str(agency_name),
                'score': float(scores[idx]),
                'agency_id': agency_id,
                'recommended_stars': score_to_stars(float(scores[idx]))
            })
            if len(recommendations) >= top_n:
                break

        return jsonify(recommendations)

    except Exception as e:
        return jsonify({'error': str(e)}), 500






##STAFFS TO CLUB
@app.route('/api/recommend/clubs/tostaff', methods=['POST'])
@token_required
def recommend_clubs_to_staff(current_user):
    try:
        # Ensure user is staff
        user_type = get_user_type(current_user, recommendation_models)
        if user_type != 'staff':
            return jsonify({'message': 'No club recommendations available (user is not staff)'}), 200

        data = request.get_json() or {}
        top_n = min(int(data.get('top_n', 5)), 20)

        if not recommendation_models:
            return jsonify({'error': 'Recommendation system not ready'}), 503

        # Load model and mappings
        model = recommendation_models['staff_model']
        id_to_user_s = recommendation_models['id_to_user_s']  # index -> staff name
        user_id_map_s = recommendation_models['user_id_map_s']  # staff name -> index
        id_to_item_s = recommendation_models['id_to_item_s']  # index -> club id
        club_id_to_name = recommendation_models['club_id_to_name']  # club id -> name

        # Normalize staff name
        staff_name = current_user.name.strip().lower()

        # Find staff index by name
        staff_idx = None
        for name, idx in user_id_map_s.items():
            if name.strip().lower() == staff_name:
                staff_idx = idx
                break

        if staff_idx is None:
            return jsonify([])

        # Predict scores
        scores = model.predict(
            user_ids=np.repeat(staff_idx, len(id_to_item_s)),
            item_ids=np.arange(len(id_to_item_s))
        )

        recommendations = []
        for idx in np.argsort(-scores):
            club_id = id_to_item_s.get(idx)
            club_name = club_id_to_name.get(club_id, club_id)
            if pd.isna(club_name):
                continue
            recommendations.append({
                'club': str(club_name),
                'score': float(scores[idx]),
                'club_id': club_id,
                'recommended_stars': score_to_stars(float(scores[idx]))
            })
            if len(recommendations) >= top_n:
                break

        return jsonify(recommendations)

    except Exception as e:
        return jsonify({'error': str(e)}), 500



##STAFF TO CLUB
@app.route('/api/recommend/staff/toclub', methods=['POST'])
@token_required
def recommend_staff_to_club(current_user):
    try:
        if not recommendation_models:
            return jsonify({'error': 'Recommendation system not ready'}), 503

        user_type = get_user_type(current_user, recommendation_models)
        if user_type != 'club':
            return jsonify({'message': 'No staff recommendations available (user is not a club)'}), 200

        data = request.get_json() or {}
        top_n = min(int(data.get('top_n', 5)), 20)

        staff_model = recommendation_models['staff_model']
        staff_name_map = recommendation_models['staff_name_map']
        user_id_map_s = recommendation_models['user_id_map_s']
        item_id_map_s = recommendation_models['item_id_map_s']
        id_to_user_s = recommendation_models['id_to_user_s']

        # Normalize club name from current_user
        club_name = current_user.name.strip().lower()

        if club_name not in item_id_map_s:
            return jsonify({'message': 'Club not found in mapping'}), 404

        club_idx = item_id_map_s[club_name]

        # Predict scores for all staff
        scores = staff_model.predict(
            user_ids=np.arange(len(user_id_map_s)),
            item_ids=np.repeat(club_idx, len(user_id_map_s))
        )

        # Format results
        recommendations = []
        for idx in np.argsort(-scores):
            staff_id = id_to_user_s.get(idx)
            staff_name = staff_name_map.get(staff_id, staff_id)

            if pd.isna(staff_name):
                continue

            recommendations.append({
                'staff': str(staff_name),
                'score': float(scores[idx]),
                'recommended_stars': score_to_stars(float(scores[idx]))
            })

            if len(recommendations) >= top_n:
                break

        return jsonify(recommendations)

    except Exception as e:
        app.logger.error(f"Error in staff-to-club recommendation: {str(e)}")
        return jsonify({'error': str(e)}), 500




#########################################################################
def score_to_stars(score, max_stars=5):
    # Normalize score to be between 0 and 1 if necessary
    score = max(0, min(score, 1))  
    
    # Multiply by max stars and round
    stars = round(score * max_stars)
    
    return '★' * stars + '☆' * (max_stars - stars)



###########################################################################33
@app.route('/api/recommendations/history', methods=['GET'])
@token_required
def get_recommendation_history(current_user):
    recommendations = Recommendation.query.filter_by(user_id=current_user.id)\
        .order_by(Recommendation.created_at.desc())\
        .limit(10)\
        .all()
    
    return jsonify([{
        'club': rec.recommended_club,
        'score': rec.score,
        'date': rec.created_at.strftime('%Y-%m-%d')
    } for rec in recommendations])


app.app_context().push()
if __name__ == '__main__':
    app.run(debug=True)






