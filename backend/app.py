import os
from tkinter.tix import Control
from flask import Flask, request, jsonify, send_from_directory, url_for, make_response
from flask_mail import Message as MailMessage
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import Enum
from flask_mail import Mail, Message 
import jwt
from functools import wraps
from datetime import datetime, timedelta
from flask_cors import CORS
import torch
import torch.nn as nn
import numpy as np
import joblib


app = Flask(__name__,template_folder='templates')
CORS(app, origins=["http://localhost:3000"])
app.config['SECRET_KEY'] = '59c9d8576f920846140e2a8985911bec588c08aebf4c7799ba0d5ae388393703'  
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:feres1@localhost/metascout"
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
    role = db.Column(db.String(50), nullable=False)  

    def __init__(self,username, email, password ,name, profile_image, role):
        self.username = username
        self.email = email
        self.password = password
        self.name = name
        self.profile_image = profile_image
        self.role = role

class Skills(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

    skill = db.Column(db.Integer, nullable=True)
    ratingS1 = db.Column(db.Integer, unique=False, nullable=True)

class PlayerProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    club_id = db.Column(db.Integer, nullable=True)#db.Integer, db.ForeignKey('club__profile.id'), unique=False, nullable=True)  # Fixed table name
    agency_id = db.Column(db.Integer, nullable=True)#db.Integer, db.ForeignKey('agency__profile.id'), unique=False, nullable=True)

    # Infos générales
    name = db.Column(db.String(20), nullable=True)
    season = db.Column(db.String(20), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    nationality = db.Column(db.String(50), nullable=True)
    position = db.Column(db.String(50), nullable=True)
    matches = db.Column(db.Integer, nullable=True)
    minutes = db.Column(db.Integer, nullable=True)
    goals = db.Column(db.Integer, nullable=True)
    assists = db.Column(db.Integer, nullable=True)
    club = db.Column(db.String(100), nullable=True)
    market_value = db.Column(db.Float, nullable=True)

    total_yellow_cards = db.Column(db.Integer, nullable=True)
    total_red_cards = db.Column(db.Integer, nullable=True)

    # Métriques
    performance_metrics = db.Column(db.Float, nullable=True)
    media_sentiment = db.Column(db.Float, nullable=True)

    # Attributs joueur
    aggression = db.Column(db.Integer, nullable=True)
    reactions = db.Column(db.Integer, nullable=True)
    long_pass = db.Column(db.Integer, nullable=True)
    stamina = db.Column(db.Integer, nullable=True)
    strength = db.Column(db.Integer, nullable=True)
    sprint_speed = db.Column(db.Integer, nullable=True)
    agility = db.Column(db.Integer, nullable=True)
    jumping = db.Column(db.Integer, nullable=True)
    heading = db.Column(db.Integer, nullable=True)
    free_kick_accuracy = db.Column(db.Integer, nullable=True)
    volleys = db.Column(db.Integer, nullable=True)

    # Gardien
    gk_positioning = db.Column(db.Integer, nullable=True)
    gk_diving = db.Column(db.Integer, nullable=True)
    gk_handling = db.Column(db.Integer, nullable=True)
    gk_kicking = db.Column(db.Integer, nullable=True)
    gk_reflexes = db.Column(db.Integer, nullable=True)
    user = db.relationship('User', backref=db.backref('player_profile', uselist=False))
    #club = db.relationship('Club_Profile', foreign_keys=[club_id], backref=db.backref('player_profile', uselist=False))  # Explicit foreign key
    #agency = db.relationship('Agency_Profile', foreign_keys=[agency_id], backref=db.backref('player_profile', uselist=False))

class Coach_Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    club_id = db.Column(db.Integer, nullable=True)#db.Integer, db.ForeignKey('club__profile.id'), unique=False, nullable=True)  # Fixed table name
    name = db.Column(db.String(80), nullable=True)

    nationality = db.Column(db.String(80), nullable=True)
    date_of_appointment = db.Column(db.Date, nullable=True)
    date_of_end_contract = db.Column(db.Date, nullable=True)
    years_of_experience = db.Column(db.Integer, nullable=True)
    qualification = db.Column(db.String(120), nullable=True)
    availability = db.Column(db.Boolean, default=True)

    user = db.relationship('User', backref=db.backref('coach_profile', uselist=False))
    #club = db.relationship('Club_Profile', backref=db.backref('coach_profile', uselist=False))  # Fixed relationship

class Agent_Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    agency_id = db.Column(db.Integer, nullable=True)#db.Integer, db.ForeignKey('agency__profile.id'), unique=False, nullable=True)
    name = db.Column(db.String(80), nullable=True)

    nationality = db.Column(db.String(80), nullable=True)
    date_of_appointment = db.Column(db.Date, nullable=True)
    date_of_end_contract = db.Column(db.Date, nullable=True)
    years_of_experience = db.Column(db.Integer, nullable=True)
    qualification = db.Column(db.String(120), nullable=True)
    availability = db.Column(db.Boolean, default=True)

    user = db.relationship('User', backref=db.backref('agent_profile', uselist=False))
    #agency = db.relationship('Agency_Profile', foreign_keys=[agency_id], backref=db.backref('agent_profile', uselist=False))

class Staff_Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    club_id = db.Column(db.Integer, nullable=True)#db.Integer, db.ForeignKey('club__profile.id'), unique=False, nullable=True)  # Fixed table name
    name = db.Column(db.String(80), nullable=True)

    nationality = db.Column(db.String(80), nullable=True)
    date_of_appointment = db.Column(db.Date, nullable=True)
    date_of_end_contract = db.Column(db.Date, nullable=True)
    years_of_experience = db.Column(db.Integer, nullable=True)
    qualification = db.Column(db.String(120), nullable=True)
    availability = db.Column(db.Boolean, default=True)

    user = db.relationship('User', backref=db.backref('staff_profile', uselist=False))
    #club = db.relationship('Club_Profile', foreign_keys=[club_id], backref=db.backref('staff_profile', uselist=False))  # Fixed relationship

class Scout_Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    club_id = db.Column(db.Integer, nullable=True)#db.Integer, db.ForeignKey('club__profile.id'), unique=False, nullable=True)  # Fixed table name
    name = db.Column(db.String(80), nullable=True)

    nationality = db.Column(db.String(80), nullable=True)
    date_of_appointment = db.Column(db.Date, nullable=True)
    date_of_end_contract = db.Column(db.Date, nullable=True)
    years_of_experience = db.Column(db.Integer, nullable=True)
    qualification = db.Column(db.String(120), nullable=True)
    availability = db.Column(db.Boolean, default=True)

    user = db.relationship('User', backref=db.backref('scout_profile', uselist=False))
    #club = db.relationship('Club_Profile', backref=db.backref('scout_profile', uselist=False))  # Fixed relationship

class Manager_Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    club_id = db.Column(db.Integer, nullable=True)#db.Integer, db.ForeignKey('club__profile.id'), unique=False, nullable=True)  # Fixed table name
    name = db.Column(db.String(80), nullable=True)

    nationality = db.Column(db.String(80), nullable=True)
    date_of_appointment = db.Column(db.Date, nullable=True)
    date_of_end_contract = db.Column(db.Date, nullable=True)
    years_of_experience = db.Column(db.Integer, nullable=True)
    qualification = db.Column(db.String(120), nullable=True)
    availability = db.Column(db.Boolean, default=True)

    total_matches = db.Column(db.Integer, nullable=True)
    wins = db.Column(db.Integer, nullable=True)
    draws = db.Column(db.Integer, nullable=True)
    losses = db.Column(db.Integer, nullable=True)
    ppg = db.Column(db.Float, nullable=True)  # Points per game

    user = db.relationship('User', backref=db.backref('manager_profile', uselist=False))
    #club = db.relationship('Club_Profile', backref=db.backref('manager_profile', uselist=False))  # Fixed relationship

class Agency_Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    player_id = db.Column(db.Integer, nullable=True)#db.Integer, db.ForeignKey('player_profile.id'), unique=False, nullable=True)
    club_id = db.Column(db.Integer, nullable=True)#db.Integer, db.ForeignKey('club__profile.id'), unique=False, nullable=True)  # Fixed table name
    agent_id = db.Column(db.Integer, nullable=True)#db.Integer, db.ForeignKey('agent__profile.id'), unique=False, nullable=True)  # Fixed table name

    country = db.Column(db.String(80), nullable=True)

    user = db.relationship('User', backref=db.backref('agency_profile', uselist=False))
    #player = db.relationship('PlayerProfile', foreign_keys=[player_id], backref=db.backref('agency_profile', uselist=False))
    #club = db.relationship('Club_Profile', foreign_keys=[club_id], backref=db.backref('agency_profile', uselist=False))  # Fixed relationship
    #agent = db.relationship('Agent_Profile', foreign_keys=[agent_id], backref=db.backref('agency_profile', uselist=False))  # Fixed relationship

class Club_Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    player_id = db.Column(db.Integer, nullable=True)#db.Integer, db.ForeignKey('player_profile.id'), unique=False, nullable=True)
    agency_id = db.Column(db.Integer, nullable=True)#db.Integer, db.ForeignKey('agency__profile.id'), unique=False, nullable=True)
    staff_id = db.Column(db.Integer, nullable=True)#db.Integer, db.ForeignKey('staff__profile.id'), unique=False, nullable=True)

    country = db.Column(db.String(80), nullable=True)
    competition = db.Column(db.String(100), nullable=True)
    squad_size = db.Column(db.Integer, nullable=True)

    user = db.relationship('User', backref=db.backref('club_profile', uselist=False))
    #player = db.relationship('PlayerProfile', foreign_keys=[player_id], backref=db.backref('club_profile', uselist=False))
    #agency = db.relationship('Agency_Profile', foreign_keys=[agency_id], backref=db.backref('club_profile', uselist=False))
    #staff = db.relationship('Staff_Profile', foreign_keys=[staff_id], backref=db.backref('club_profile', uselist=False))
    
class Play(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    profile_image = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(50), nullable=False)  

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

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token or not token.startswith("Bearer "):
            return jsonify({'message': 'Token is missing or improperly formatted!'}), 401

        try:
            decoded_token = jwt.decode(token.split(" ")[1], app.config['SECRET_KEY'], algorithms=['HS256'])
            print(f"Decoded Token: {decoded_token}")  # Debug log
            user_id = decoded_token.get('user_id')
            if not user_id:
                return jsonify({'message': 'Token is invalid: user_id is missing!'}), 401
            current_user = User.query.get(user_id)
            if not current_user:
                return jsonify({'message': 'User not found!'}), 404
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        except Exception as e:
            return jsonify({'message': f'An error occurred: {str(e)}'}), 500

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
        if user.role == 'Player':
            user_profile = PlayerProfile.query.filter_by(user_id=user.id).first()
            user_skills = Skills.query.filter_by(user_id=user.id).first()
            return jsonify({
                'id': user.id,
                'agency_id': user_profile.agency_id,
                'club_id': user_profile.club_id,
                'username': user.username,
                'email': user.email,
                'name': user.name,
                'profile_image': profile_image,
                'role': user.role,
                'season': user_profile.season,
                'age': user_profile.age,
                'nationality': user_profile.nationality,
                'position': user_profile.position,
                'matches': user_profile.matches,
                'minutes': user_profile.minutes,
                'goals': user_profile.goals,
                'assists': user_profile.assists,
                'club': user_profile.club,
                'market_value': user_profile.market_value,
                'total_yellow_cards': user_profile.total_yellow_cards,
                'total_red_cards': user_profile.total_red_cards,
                'performance_metrics': user_profile.performance_metrics,
                'media_sentiment': user_profile.media_sentiment,
                'aggression': user_profile.aggression,
                'reactions': user_profile.reactions,
                'long_pass': user_profile.long_pass,
                'stamina': user_profile.stamina,
                'strength': user_profile.strength,
                'sprint_speed': user_profile.sprint_speed,
                'agility': user_profile.agility,
                'jumping': user_profile.jumping,
                'heading': user_profile.heading,
                'free_kick_accuracy': user_profile.free_kick_accuracy,
                'volleys': user_profile.volleys,
                'gk_positioning': user_profile.gk_positioning,
                'gk_diving': user_profile.gk_diving,
                'gk_handling': user_profile.gk_handling,
                'gk_kicking': user_profile.gk_kicking,
                'gk_reflexes': user_profile.gk_reflexes,
                'ratingS1': user_skills.ratingS1,
                'skill': user_skills.skill
            }), 200
        elif user.role == 'Coach':
            Coach = Coach_Profile.query.filter_by(user_id=user.id).first()
            return jsonify({
                'id': user.id,
                'club_id': Coach.club_id,
                'username': user.username,
                'email': user.email,
                'name': user.name,
                'profile_image': profile_image,
                'role': user.role,
                'nationality': Coach.nationality,
                'date_of_appointment': Coach.date_of_appointment,
                'date_of_end_contract': Coach.date_of_end_contract,
                'years_of_experience': Coach.years_of_experience,
                'qualification': Coach.qualification,
                'availability': Coach.availability
            }), 200
        elif user.role == 'Agent':
            Agent = Agent_Profile.query.filter_by(user_id=user.id).first()
            return jsonify({
                'id': user.id,
                'agency_id': Agent.agency_id,
                'username': user.username,
                'email': user.email,
                'name': user.name,
                'profile_image': profile_image,
                'role': user.role,
                'nationality': Agent.nationality,
                'date_of_appointment': Agent.date_of_appointment,
                'date_of_end_contract': Agent.date_of_end_contract,
                'years_of_experience': Agent.years_of_experience,
                'qualification': Agent.qualification,
                'availability': Agent.availability
            }), 200
        elif user.role == 'Staff':
            Staff = Staff_Profile.query.filter_by(user_id=user.id).first()
            return jsonify({
                'id': user.id,
                'club_id': Staff.club_id,
                'username': user.username,
                'email': user.email,
                'name': user.name,
                'profile_image': profile_image,
                'role': user.role,
                'nationality': Staff.nationality,
                'date_of_appointment': Staff.date_of_appointment,
                'date_of_end_contract': Staff.date_of_end_contract,
                'years_of_experience': Staff.years_of_experience,
                'qualification': Staff.qualification,
                'availability': Staff.availability
            }), 200
        elif user.role == 'Scout':
            Scout = Scout_Profile.query.filter_by(user_id=user.id).first()
            return jsonify({
                'id': user.id,
                'club_id': Scout.club_id,
                'username': user.username,
                'email': user.email,
                'name': user.name,
                'profile_image': profile_image,
                'role': user.role,
                'nationality': Scout.nationality,
                'date_of_appointment': Scout.date_of_appointment,
                'date_of_end_contract': Scout.date_of_end_contract,
                'years_of_experience': Scout.years_of_experience,
                'qualification': Scout.qualification,
                'availability': Scout.availability
            }), 200
        elif user.role == 'Manager':
            Manager = Manager_Profile.query.filter_by(user_id=user.id).first()
            return jsonify({
                'id': user.id,
                'club_id': Manager.club_id,
                'username': user.username,
                'email': user.email,
                'name': user.name,
                'profile_image': profile_image,
                'role': user.role,
                'nationality': Manager.nationality,
                'date_of_appointment': Manager.date_of_appointment,
                'date_of_end_contract': Manager.date_of_end_contract,
                'years_of_experience': Manager.years_of_experience,
                'qualification': Manager.qualification,
                'availability': Manager.availability,
                'total_matches': Manager.total_matches,
                'wins': Manager.wins,
                'draws': Manager.draws,
                'losses': Manager.losses,
                'ppg': Manager.ppg
            }), 200
        elif user.role == 'Club':
            Club = Club_Profile.query.filter_by(user_id=user.id).first()
            return jsonify({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'name': user.name,
                'profile_image': profile_image,
                'role': user.role,
                'country': Club.country,
                'competition': Club.competition,
                'squad_size': Club.squad_size
            }), 200
        elif user.role == 'Agency':
            Agency = Agency_Profile.query.filter_by(user_id=user.id).first()
            return jsonify({
                'id': user.id,
                'club_id': Agency.club_id,
                'username': user.username,
                'email': user.email,
                'name': user.name,
                'profile_image': profile_image,
                'role': user.role,
                'country': Agency.country
            }), 200
        else:
            user_profile = None  # Handle cases where the role doesn't match any known profiles
            return jsonify({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'name': user.name,
                'profile_image': profile_image,
                'role': user.role
            }), 200

    except Exception as e:
        print(f"Error fetching user data: {e}")
        return jsonify({'message': 'User not found'}), 404

@app.route('/get_clubs', methods=['GET'])
def get_clubs():
    try:
        clubs = User.query.filter_by(role="Club").all() #Club_Profile.query.all()
        club_list = [{'id': club.id, 'name': club.name} for club in clubs]  # Replace 'country' with the actual club name field
        return jsonify(club_list), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch clubs', 'details': str(e)}), 500
    
@app.route('/get_agencies', methods=['GET'])
def get_agencies():
    try:
        agencies = User.query.filter_by(role="Agency").all() #Agency_Profile.query.all()
        agency_list = [{'id': agency.id, 'name': agency.name} for agency in agencies]  # Replace 'country' with the actual agency name field
        return jsonify(agency_list), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch agencies', 'details': str(e)}), 500

@app.route('/register', methods=['POST'])
def register():
    try:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        role = request.form['role']
        
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return jsonify({'message': 'Username or email already exists'}), 409

        profile_image = request.files.get('profile_image')
        profile_image_path = None
        if profile_image and allowed_file(profile_image.filename):
            filename = secure_filename(profile_image.filename)
            profile_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_image.save(profile_image_path) 

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        role = request.form.get('role')
        print(role)
        
        new_user = User(username=username, email=email, password=hashed_password, name=name, profile_image=profile_image_path, role=role)
        
        db.session.add(new_user)
        db.session.commit()

        # Add user to the appropriate profile table based on role
        if role == 'Manager':
            new_profile = Manager_Profile(user_id=new_user.id)
            new_staff = Staff_Profile(user_id=new_user.id)
            db.session.add(new_staff)
        elif role == 'Scout':
            new_profile = Scout_Profile(user_id=new_user.id)
            new_staff = Staff_Profile(user_id=new_user.id)
            db.session.add(new_staff)
        elif role == 'Staff':
            new_profile = Staff_Profile(user_id=new_user.id)
        elif role == 'Agent':
            new_profile = Agent_Profile(user_id=new_user.id)
        elif role == 'Coach':
            new_profile = Coach_Profile(user_id=new_user.id)
            new_staff = Staff_Profile(user_id=new_user.id)
            db.session.add(new_staff)
        elif role == 'Player':
            new_profile = PlayerProfile(user_id=new_user.id)
            new_skills = Skills(user_id=new_user.id)
            db.session.add(new_skills)
        elif role == 'Club':
            new_profile = Club_Profile(user_id=new_user.id)
        elif role == 'Agency':
            new_profile = Agency_Profile(user_id=new_user.id)
        else:
            return jsonify({'error': 'Invalid role provided'}), 400

        print(new_profile)
        db.session.add(new_profile)
        db.session.commit()

        # Send welcome email
    #     msg = Message("Welcome to MetaScout!",
    #                   sender=app.config['MAIL_USERNAME'],
    #                   recipients=[email])
    #     msg.html = f"""
    #         <p>Hello {name},</p>
    #         <p>Thank you for signing up on MetaScout. We’re excited to have you with us!</p>
    #         <p>Best regards,<br>The MetaScout Team</p>
    #     """
    #     mail.send(msg)

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

    print(username)
    print(password)
    user = User.query.filter_by(username=username).first()
    
    # Check if user exists and password matches
    if user and check_password_hash(user.password, password):
        # Create JWT token with expiration of 24 hours
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, app.config['SECRET_KEY'])
        return jsonify({'token': str(token)}) ,200
        #return jsonify({'message': 'Login successful','user_id': user.id }), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401
    
@app.route('/resetPassword', methods=['PUT'])
def reset_password():
    token = request.json['token']
    newPassword = request.json['newPassword']
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']

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
    token = jwt.encode({'user_id': user_id, 'exp': datetime.utcnow() + timedelta(hours=24)}, app.config['SECRET_KEY'], algorithm='HS256')
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

@app.route('/update_profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.form  # Use request.json to handle JSON data

    # Debug: Log incoming data
    print(f"Request data: {data}")
    
# Handle profile image upload (if applicable)
    if 'profile_image' in request.files:
        profile_image = request.files.get('profile_image')
        print(f"Profile image: {profile_image}")
        if profile_image and allowed_file(profile_image.filename):
            filename = secure_filename(profile_image.filename)
            profile_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_image.save(profile_image_path)
            current_user.profile_image = profile_image_path

    data = request.json  # Use request.json to handle JSON data 
    # Update user fields
    if 'username' in data:
        current_user.username = data['username']
    if 'email' in data:
        current_user.email = data['email']
    if 'name' in data:
        current_user.name = data['name']
    if 'role' in data:
        current_user.role = data['role']
    if 'password' in data:
        current_user.password = generate_password_hash(data['password'], method='pbkdf2:sha256')


    
    def convert_value(value, target_type):
        """Helper function to convert values to the correct type or None."""
        if value in ['null', 'undefined', '']:
            return None
        try:
            return target_type(value)
        except ValueError:
            return None

    try:
        # Fetch the user's profile
        if current_user.role == 'Player':
            user_profile = PlayerProfile.query.filter_by(user_id=current_user.id).first()

            if not user_profile:
                return jsonify({'error': 'Player profile not found'}), 404

            # Update PlayerProfile fields with type conversion
            if 'club_id' in data:
                user_profile.club_id = data['club_id']
            if 'agency_id' in data:
                user_profile.agency_id = data['agency_id']
            if 'nationality' in data:
                user_profile.nationality = data['nationality']
            if 'position' in data:
                user_profile.position = data['position']
            if 'age' in data:
                user_profile.age = data['age']
            if 'matches' in data:
                user_profile.matches = data['matches']
            if 'minutes' in data:
                user_profile.minutes = data['minutes']
            if 'goals' in data:
                user_profile.goals = data['goals']
            if 'assists' in data:
                user_profile.assists = data['assists']
            if 'market_value' in data:
                user_profile.market_value = data['market_value']
            if 'total_yellow_cards' in data:
                user_profile.total_yellow_cards = data['total_yellow_cards']
            if 'total_red_cards' in data:
                user_profile.total_red_cards = data['total_red_cards']
            if 'performance_metrics' in data:
                user_profile.performance_metrics = data['performance_metrics']
            if 'media_sentiment' in data:
                user_profile.media_sentiment = data['media_sentiment']
            if 'aggression' in data:
                user_profile.aggression = data['aggression']
            if 'reactions' in data:
                user_profile.reactions = data['reactions']
            if 'long_pass' in data:
                user_profile.long_pass = data['long_pass']
            if 'stamina' in data:
                user_profile.stamina = data['stamina']
            if 'strength' in data:
                user_profile.strength = data['strength']
            if 'sprint_speed' in data:
                user_profile.sprint_speed = data['sprint_speed']
            if 'agility' in data:
                user_profile.agility = data['agility']
            if 'jumping' in data:
                user_profile.jumping = data['jumping']
            if 'heading' in data:
                user_profile.heading = data['heading']
            if 'free_kick_accuracy' in data:
                user_profile.free_kick_accuracy = data['free_kick_accuracy']
            if 'volleys' in data:
                user_profile.volleys = data['volleys']

        elif current_user.role == 'Coach':
            user_profile = Coach_Profile.query.filter_by(user_id=current_user.id).first()

            if not user_profile:
                return jsonify({'error': 'Coach profile not found'}), 404

            # Update Coach_Profile fields
            if 'club_id' in data:
                user_profile.club_id = data['club_id']
            if 'nationality' in data:
                user_profile.nationality = data['nationality']
            if 'date_of_appointment' in data:
                user_profile.date_of_appointment = datetime.strptime(data['date_of_appointment'], '%Y-%m-%d').date()
            if 'date_of_end_contract' in data:
                user_profile.date_of_end_contract = datetime.strptime(data['date_of_end_contract'], '%Y-%m-%d').date()
            if 'years_of_experience' in data:
                user_profile.years_of_experience = data['years_of_experience']
            if 'qualification' in data:
                user_profile.qualification = data['qualification']
            if 'availability' in data:
                user_profile.availability = data['availability']

        elif current_user.role == 'Agent':
            user_profile = Agent_Profile.query.filter_by(user_id=current_user.id).first()

            if not user_profile:
                return jsonify({'error': 'Agent profile not found'}), 404

            # Update Agent_Profile fields
            if 'agency_id' in data:
                user_profile.agency_id = data['agency_id']
            if 'nationality' in data:
                user_profile.nationality = data['nationality']
            if 'date_of_appointment' in data:
                user_profile.date_of_appointment = datetime.strptime(data['date_of_appointment'], '%Y-%m-%d').date()
            if 'date_of_end_contract' in data:
                user_profile.date_of_end_contract = datetime.strptime(data['date_of_end_contract'], '%Y-%m-%d').date()
            if 'years_of_experience' in data:
                user_profile.years_of_experience = data['years_of_experience']
            if 'qualification' in data:
                user_profile.qualification = data['qualification']
            if 'availability' in data:
                user_profile.availability = data['availability']

        elif current_user.role == 'Staff':
            user_profile = Staff_Profile.query.filter_by(user_id=current_user.id).first()

            if not user_profile:
                return jsonify({'error': 'Staff profile not found'}), 404

            # Update Staff_Profile fields
            if 'club_id' in data:
                user_profile.club_id = data['club_id']
            if 'nationality' in data:
                user_profile.nationality = data['nationality']
            if 'date_of_appointment' in data:
                user_profile.date_of_appointment = datetime.strptime(data['date_of_appointment'], '%Y-%m-%d').date()
            if 'date_of_end_contract' in data:
                user_profile.date_of_end_contract = datetime.strptime(data['date_of_end_contract'], '%Y-%m-%d').date()
            if 'years_of_experience' in data:
                user_profile.years_of_experience = data['years_of_experience']
            if 'qualification' in data:
                user_profile.qualification = data['qualification']
            if 'availability' in data:
                user_profile.availability = data['availability']

        elif current_user.role == 'Scout':
            user_profile = Scout_Profile.query.filter_by(user_id=current_user.id).first()

            if not user_profile:
                return jsonify({'error': 'Scout profile not found'}), 404
            
            print(f"Updating profile for role: {current_user.role}")
            print(f"Incoming data: {data}")

            # Update Scout_Profile fields
            if 'club_id' in data:
                user_profile.club_id = data['club_id']
            if 'nationality' in data:
                user_profile.nationality = data['nationality']
            if 'date_of_appointment' in data:
                user_profile.date_of_appointment = datetime.strptime(data['date_of_appointment'], '%Y-%m-%d').date()
            if 'date_of_end_contract' in data:
                user_profile.date_of_end_contract = datetime.strptime(data['date_of_end_contract'], '%Y-%m-%d').date()
            if 'years_of_experience' in data:
                user_profile.years_of_experience = data['years_of_experience']
            if 'qualification' in data:
                user_profile.qualification = data['qualification']
            if 'availability' in data:
                user_profile.availability = data['availability']

        elif current_user.role == 'Manager':
            user_profile = Manager_Profile.query.filter_by(user_id=current_user.id).first()

            if not user_profile:
                return jsonify({'error': 'Manager profile not found'}), 404

            # Update Manager_Profile fields
            if 'club_id' in data:
                user_profile.club_id = data['club_id']
            if 'nationality' in data:
                user_profile.nationality = data['nationality']
            if 'date_of_appointment' in data:
                user_profile.date_of_appointment = datetime.strptime(data['date_of_appointment'], '%Y-%m-%d').date()
            if 'date_of_end_contract' in data:
                user_profile.date_of_end_contract = datetime.strptime(data['date_of_end_contract'], '%Y-%m-%d').date()
            if 'years_of_experience' in data:
                user_profile.years_of_experience = data['years_of_experience']
            if 'qualification' in data:
                user_profile.qualification = data['qualification']
            if 'availability' in data:
                user_profile.availability = data['availability']
            if 'total_matches' in data:
                user_profile.total_matches = data['total_matches']
            if 'wins' in data:
                user_profile.wins = data['wins']
            if 'draws' in data:
                user_profile.draws = data['draws']
            if 'losses' in data:
                user_profile.losses = data['losses']
            if 'ppg' in data:
                user_profile.ppg = data['ppg']
        elif current_user.role == 'Club':
            user_profile = Club_Profile.query.filter_by(user_id=current_user.id).first()

            if not user_profile:
                return jsonify({'error': 'Club profile not found'}), 404

            # Update Club_Profile fields
            if 'country' in data:
                user_profile.country = data['country']
            if 'competition' in data:
                user_profile.competition = data['competition']
            if 'squad_size' in data:
                user_profile.squad_size = data['squad_size']
        elif current_user.role == 'Agency':
            user_profile = Agency_Profile.query.filter_by(user_id=current_user.id).first()

            if not user_profile:
                return jsonify({'error': 'Agency profile not found'}), 404

            # Update Agency_Profile fields
            if 'club_id' in data:
                user_profile.club_id = data['club_id']
            if 'country' in data:
                user_profile.country = data['country']

        else:
            return jsonify({'error': 'Invalid role'}), 400

        # Debug: Log updated user data
        print(f"Updating user: {current_user}")
        print(f"Username: {current_user.username}, Email: {current_user.email}, Name: {current_user.name}, Role: {current_user.role}")

        # Ensure current_user and user_profile are attached to the session
        db.session.add(current_user)
        db.session.add(user_profile)

        # Commit changes
        db.session.commit()
        print("Database commit successful")

        # Refresh the object to reflect changes
        db.session.refresh(current_user)
        db.session.refresh(user_profile)

        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Database commit failed: {e}")
        return jsonify({'error': 'An error occurred while updating the profile', 'details': str(e)}), 500
    
@app.route('/predict', methods=['POST'])
def predict():
    # Load the PyTorch model
    class MarketValuePredictor(nn.Module):
        def __init__(self, input_dim, hidden_dim1, hidden_dim2, hidden_dim3, dropout_rate):
            super(MarketValuePredictor, self).__init__()
            self.model = nn.Sequential(
                nn.Linear(input_dim, hidden_dim1),
                nn.ReLU(),
                nn.BatchNorm1d(hidden_dim1),
                nn.Dropout(dropout_rate),
                nn.Linear(hidden_dim1, hidden_dim2),
                nn.ReLU(),
                nn.BatchNorm1d(hidden_dim2),
                nn.Dropout(dropout_rate),
                nn.Linear(hidden_dim2, hidden_dim3),
                nn.ReLU(),
                nn.Linear(hidden_dim3, 1)
            )
            
        def forward(self, x):
            return self.model(x)

    input_dim = 39   
    hidden_dim1= 222
    hidden_dim2= 80
    hidden_dim3= 21
    dropout_rate= 0.038842948881822076

    model = MarketValuePredictor(input_dim, hidden_dim1, hidden_dim2, hidden_dim3, dropout_rate)

    # Load the state dictionary
    model.load_state_dict(torch.load('uploads/marketValuemodel/market_value_predictor.pth'))
    scaler = joblib.load("uploads\marketValuemodel\scaler_market_value.pkl")
    # Set the model to evaluation mode
    model.eval()

    try:
        # Validate the request body
        if not request.json or 'input' not in request.json:
            return jsonify({'error': 'Invalid request. "input" key is missing.'}), 400

        # Get input data from the request
        input_data = request.json['input']

        # Ensure input_data is a list of numbers
        if not isinstance(input_data, list) or not all(isinstance(i, (int, float)) for i in input_data):
            return jsonify({'error': 'Invalid input format. Expected a list of numbers.'}), 400

        
        input_tensor = torch.tensor([input_data], dtype=torch.float32) # Convert to tensor
        input_tensor = torch.tensor([input_data], dtype=torch.float32)  # Shape: [1, 39]
        # Perform prediction
        with torch.no_grad():
            prediction = model(input_tensor)
        
        # Convert prediction to a list and return as JSON
        #prediction_list = prediction.numpy().tolist()
        prediction_array = prediction.numpy()

        # Apply reverse scaling using the scaler
        scaled_prediction = scaler.inverse_transform(prediction_array)

        # Convert the scaled prediction to a list and return as JSON
        scaled_prediction_list = scaled_prediction.tolist()
        return jsonify({'prediction': scaled_prediction_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/average_rating', methods=['GET'])
def calculate_average_rating():
    try:
        # Query the Skills table to calculate the average of the 'ratingS1' column
        average_rating = db.session.query(db.func.avg(Skills.ratingS1)).scalar()

        # Return the average rating as a JSON response
        return jsonify({'average_rating': average_rating}), 200
    except Exception as e:
        # Handle any errors that occur during the query
        return jsonify({'error': 'An error occurred while calculating the average rating', 'details': str(e)}), 500

app.app_context().push()
if __name__ == '__main__':
    app.run(debug=True)

