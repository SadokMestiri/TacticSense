import base64
import os
import random
import traceback
from flask import Flask, Request, json, request, jsonify, send_from_directory, url_for, make_response
from flask_mail import Message as MailMessage
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import numpy as np
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import Enum
import jwt
from functools import wraps
from datetime import datetime, timedelta
from flask_mail import Mail
import re
from flask_cors import CORS
from datetime import date, timedelta
import joblib
import pandas as pd
from futurehouse_client import FutureHouseClient, JobNames
from futurehouse_client.models.app import TaskRequest
from threading import Thread
from web3 import Web3
from pdf2image import convert_from_bytes
import fitz 
import pytesseract
from PIL import Image

app = Flask(__name__,template_folder='templates')
CORS(app, origins=["http://localhost:3000"])
app.config['SECRET_KEY'] = '59c9d8576f920846140e2a8985911bec588c08aebf4c7799ba0d5ae388393703'  
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:0000@localhost/metascout"
db = SQLAlchemy(app)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'layouni.nourelhouda@gmail.com'
app.config['MAIL_PASSWORD'] = 'liqm qofg jseq mzty'
mail = Mail(app)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  

w3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/2264fb8767644f77889c230508451721"))

with open('MetaCoinABI.json', 'r') as f:
    abi = json.load(f)

# Contract address
contract_address = Web3.to_checksum_address("0x2dE8B83c77ecb2FB47c35702E3879E070F79C58d")
owner_private_key="e8be4c05fe6f9bfa3fb7e64e75723d31d8a48dd2f327e1ff09e9dadecd3c3622"
# Owner wallet (the deployer of MetaCoin)
owner_address = w3.to_checksum_address("0x16c7cc09EBA8039EBE2d6d14B0dAA299F77C3FF1")
contract = w3.eth.contract(address=contract_address, abi=abi)

API_KEY = "R+mdo6B8CqEuCfg9VoS/OA.platformv01.eyJqdGkiOiJhNDJkYWIyOC1hZTMzLTQ5MjQtOTgwNC1mZjU5YmQ3YWZiNTIiLCJzdWIiOiJsQk5zNmI1RnVOYlQwVlJCaENrQ2pHTlo3aW8xIiwiaWF0IjoxNzQ2ODg1MTE2fQ.yKadXV4Xe+vVcfKDLg5Xg8y/oWX5WSdGJygS++XdX1k"
client = FutureHouseClient(api_key=API_KEY)
# Load model and encoder
model = joblib.load('modeling/injury_type_model.pkl')
label_encoder = joblib.load('modeling/injury_label_encoder.pkl')
# Load preprocessing objects
scaler = joblib.load('modeling/scaler.pkl')
position_encoder = joblib.load('modeling/position_encoder.pkl')
injury_encoder = joblib.load('modeling/injury_label_encoder.pkl')
nationality_freq = joblib.load('modeling/nationality_freq.pkl')
teamname_freq = joblib.load('modeling/teamname_freq.pkl')

injury_group_map = {
    0: "Ankle/Foot",
    1: "Back/Spine",
    2: "Calf/Shin",
    3: "General/Misc",
    4: "Groin/Hip",
    5: "Head/Neck",
    6: "Knee/Leg",
    7: "Tendon",
    8: "Thigh/Hamstring",
    9: "Upper Body"
}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    profile_image = db.Column(db.String(255), nullable=True) 
    eth_address = db.Column(db.String(42), unique=True, nullable=False)
    private_key = db.Column(db.String(256), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)  

    def __init__(self,username, email, password ,name, profile_image, role):
        self.username = username
        self.email = email
        self.password = password
        self.name = name
        self.profile_image = profile_image
        self.role = role

class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    club_name = db.Column(db.String(100), nullable=False)
    competition = db.Column(db.String(100), nullable=True)
    squad_size = db.Column(db.Integer, nullable=True)
    country = db.Column(db.String(100), nullable=True)

class PlayerProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

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
    photo = db.Column(db.String(255), nullable=True)
    score = db.Column(db.Float, nullable=True)

    user = db.relationship('User', backref=db.backref('player_profile', uselist=False))

class Coach_Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False)

    nationality = db.Column(db.String(80), nullable=True)
    date_of_appointment = db.Column(db.Date, nullable=True)
    date_of_end_contract = db.Column(db.Date, nullable=True)
    years_of_experience = db.Column(db.Integer, nullable=True)
    qualification = db.Column(db.String(120), nullable=True)
    availability = db.Column(db.Boolean, default=True)
    photo = db.Column(db.String(255), nullable=True)

    user = db.relationship('User', backref=db.backref('coach_profile', uselist=False))

class Agent_Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False)

    nationality = db.Column(db.String(80), nullable=True)
    date_of_appointment = db.Column(db.Date, nullable=True)
    date_of_end_contract = db.Column(db.Date, nullable=True)
    years_of_experience = db.Column(db.Integer, nullable=True)
    qualification = db.Column(db.String(120), nullable=True)
    availability = db.Column(db.Boolean, default=True)

    user = db.relationship('User', backref=db.backref('agent_profile', uselist=False))

class Staff_Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False)

    nationality = db.Column(db.String(80), nullable=True)
    date_of_appointment = db.Column(db.Date, nullable=True)
    date_of_end_contract = db.Column(db.Date, nullable=True)
    years_of_experience = db.Column(db.Integer, nullable=True)
    qualification = db.Column(db.String(120), nullable=True)
    availability = db.Column(db.Boolean, default=True)

    user = db.relationship('User', backref=db.backref('staff_profile', uselist=False))

class Scout_Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False)

    nationality = db.Column(db.String(80), nullable=True)
    date_of_appointment = db.Column(db.Date, nullable=True)
    date_of_end_contract = db.Column(db.Date, nullable=True)
    years_of_experience = db.Column(db.Integer, nullable=True)
    qualification = db.Column(db.String(120), nullable=True)
    availability = db.Column(db.Boolean, default=True)

    user = db.relationship('User', backref=db.backref('scout_profile', uselist=False))

class Manager_Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False)

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

class Play(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    profile_image = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(50), nullable=False)  

class UserStreak(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    current_streak = db.Column(db.Integer, nullable=False)
    highest_streak = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    connection_dates = db.Column(db.JSON, nullable=False)  # Storing dates as JSON
    daily_points = db.Column(db.JSON, nullable=False)  # Store daily points in JSON
    last_login_date = db.Column(db.Date, nullable=True)

    user = db.relationship('User', backref='user_streak', uselist=False)

    def __repr__(self):
        return f"<UserStreak {self.user_id}>"


class PostHashtag(db.Model):
    __tablename__ = 'post_hashtag'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'), nullable=False)
    hashtag_id = db.Column(db.Integer, db.ForeignKey('hashtags.id'), nullable=False)

class JobHashtag(db.Model):
    __tablename__ = 'job_hashtag'
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    hashtag_id = db.Column(db.Integer, db.ForeignKey('hashtags.id'), nullable=False)
    job = db.relationship('Job', back_populates='hashtags')
    hashtag = db.relationship('Hashtag', back_populates='jobs')


class Hashtag(db.Model):
    __tablename__ = 'hashtags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    jobs = db.relationship('JobHashtag', back_populates='hashtag', overlaps="job_hashtags")


class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    content = db.Column(db.Text)
    image_url = db.Column(db.String(255), nullable=True)
    video_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='posts', lazy=True)
    hashtags = db.relationship(
        'Hashtag',
        secondary='post_hashtag',
        backref=db.backref('posts', lazy='dynamic')
    )    
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

class PlayerRating(db.Model):
    __tablename__ = 'player_rating'
    id = db.Column(db.Integer, primary_key=True)
    
    coach_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player_profile.id'), nullable=False)
    
    score = db.Column(db.Float, nullable=False)

    # Un coach peut noter un joueur une seule fois
    __table_args__ = (db.UniqueConstraint('coach_id', 'player_id', name='unique_rating'),)

    coach = db.relationship('User', backref='given_ratings')
    player = db.relationship('PlayerProfile', backref='received_ratings')

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player_profile.id'))
    coach_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    player = db.relationship('PlayerProfile', backref='notifications')
    coach = db.relationship('User', backref='sent_notifications')

# Group conversation model, which holds multiple users
class GroupConversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)  # Optional name for the group chat
    users = db.relationship('User', secondary='group_conversation_user', backref='group_conversations')

# Intermediate table to link users and group conversations
class GroupConversationUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_conversation_id = db.Column(db.Integer, db.ForeignKey('group_conversation.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Group message model for storing messages in group chats
class GroupMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    seen = db.Column(db.Boolean, default=False)
    group_conversation_id = db.Column(db.Integer, db.ForeignKey('group_conversation.id'), nullable=False)

class GroupMessageSeen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_message_id = db.Column(db.Integer, db.ForeignKey('group_message.id'), nullable=False)
    seen = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref=db.backref('seen_messages', lazy=True))
    group_message = db.relationship('GroupMessage', backref=db.backref('seen_by', lazy=True))

class MessageReaction(db.Model):
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), primary_key=True)
    reaction_name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    is_group = db.Column(db.Boolean, nullable=False)  # To differentiate if group or one-to-one message

    # Relationships
    message = db.relationship('Message', backref=db.backref('reactions', lazy=True))
    user = db.relationship('User', backref=db.backref('reactions', lazy=True))
    conversation = db.relationship('Conversation', backref=db.backref('message_reactions', lazy=True))

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=True)
    salary = db.Column(db.String(50), nullable=True)
    job_type = db.Column(db.String(50), nullable=False)  # Full-time, Part-time, etc.
    experience = db.Column(db.String(50), nullable=False)  # 1-2 years, 2-3 years, etc.
    category = db.Column(db.String(50), nullable=True)  # Category of job
    hashtags = db.relationship('JobHashtag', back_populates='job', overlaps="hashtag,job_hashtags")
 

class JobPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    job = db.relationship('Job', backref='jobposts', lazy=True)
    user = db.relationship('User', backref='jobposts', lazy=True)

class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    job = db.relationship('Job', backref='applications', lazy=True)
    user = db.relationship('User', backref='applications', lazy=True)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            decoded_token = jwt.decode(token.split(" ")[1], app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(decoded_token['user_id'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)
    
    return decorated


def extract_hashtags(content):
    return set(re.findall(r"#(\w+)", content))
def handle_hashtags(post, job, content):
    hashtags = extract_hashtags(content)
    
    if not hashtags:
        return  # No hashtags to process, exit early
    
    try:
        # Process hashtags for posts
        if post:
            for hashtag in hashtags:
                # Check if the hashtag already exists in the database
                hashtag_obj = Hashtag.query.filter_by(name=hashtag).first()
                
                # If it doesn't exist, create and add it
                if not hashtag_obj:
                    hashtag_obj = Hashtag(name=hashtag)
                    db.session.add(hashtag_obj)
                    db.session.commit()  # Ensure the hashtag is committed to the database before referencing it
                
                # Create the association in the post_hashtag table
                post_hashtag = PostHashtag(post_id=post.post_id, hashtag_id=hashtag_obj.id)
                db.session.add(post_hashtag)
        
        # Process hashtags for jobs
        if job:
            for hashtag in hashtags:
                hashtag_obj = Hashtag.query.filter_by(name=hashtag).first()
                
                if not hashtag_obj:
                    hashtag_obj = Hashtag(name=hashtag)
                    db.session.add(hashtag_obj)
                    db.session.commit()  # Ensure the hashtag is committed to the database before referencing it
                
                # Check if the hashtag was created successfully and has a valid id
                if not hashtag_obj.id:
                    raise Exception(f"Hashtag {hashtag} was not properly created.")
                
                # Create the association in the job_hashtag table
                job_hashtag = JobHashtag(job_id=job.id, hashtag_id=hashtag_obj.id)
                db.session.add(job_hashtag)

        # Commit all changes to the database
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(f"Error handling hashtags: {str(e)}")  # Log the error for debugging
        raise e  # Reraise exception to let the caller handle it

@app.route('/')
def hello():
    return 'Hey!'

""" @app.route('/send_message', methods=['POST'])
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
    }), 201 """

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()

    # Validate the sender
    sender = User.query.get(data['sender_id'])
    if not sender:
        return jsonify({'message': 'Invalid sender'}), 400

    # Check if it's a group conversation or a one-to-one conversation
    is_group_conversation = data.get('is_group_conversation', False)

    if is_group_conversation:
        # It's a group conversation
        group_conversation_id = data['conversation_id']
        group_conversation = GroupConversation.query.get(group_conversation_id)
        if not group_conversation:
            return jsonify({'message': 'Group conversation not found'}), 400

        # Create a new group message
        new_message = GroupMessage(
            sender_id=data['sender_id'],
            message=data['message'],
            group_conversation_id=group_conversation_id,
            seen=False  # Initially, mark it as not seen by any user
        )
        db.session.add(new_message)
        db.session.commit()

        # Optionally: Here you can broadcast the message to all users in the group (if needed)
        # For example, a WebSocket could notify all users in the group about the new message

    else:
        # It's a one-to-one conversation
        conversation_id = data['conversation_id']
        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            return jsonify({'message': 'Conversation not found'}), 400

        # Ensure the receiver exists (only for one-to-one conversations)
        receiver_id = data.get('receiver_id')
        if not receiver_id:
            return jsonify({'message': 'Receiver ID is required for one-to-one conversations'}), 400

        receiver = User.query.get(receiver_id)
        if not receiver:
            return jsonify({'message': 'Invalid receiver'}), 400

        # Create a new message for one-to-one conversation
        new_message = Message(
            sender_id=data['sender_id'],
            receiver_id=receiver_id,
            message=data['message'],
            conversation_id=conversation_id,
            seen=False
        )
        db.session.add(new_message)

    # Commit the transaction
    db.session.commit()

    # Return the new message details
    response_data = {
        'message': 'Message sent successfully',
        'message_id': new_message.id,
        'sender_id': new_message.sender_id,
        'message': new_message.message,
        'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }

    # Include additional data in the response if it's a group message
    if is_group_conversation:
        response_data['group_conversation_id'] = new_message.group_conversation_id
    else:
        response_data['receiver_id'] = new_message.receiver_id

    return jsonify(response_data), 201

@app.route('/mark_message_seen/<int:message_id>', methods=['POST'])
def mark_message_seen(message_id):
    message = Message.query.get(message_id)
    
    if message:
        message.seen = True
        db.session.commit()
        return jsonify({'message': 'Message marked as seen'}), 200
    else:
        return jsonify({'message': 'Message not found'}), 404

@app.route('/mark_group_message_seen/<int:group_message_id>', methods=['POST'])
def mark_group_message_seen(group_message_id):
    group_message = GroupMessage.query.get(group_message_id)
    
    if group_message:
        user_id = request.json.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Check if the user has already seen the message
        seen_entry = GroupMessageSeen.query.filter_by(user_id=user_id, group_message_id=group_message_id).first()
        
        if not seen_entry:
            # If the user hasn't seen the message, add them to the "seen_by" relationship
            seen_entry = GroupMessageSeen(user_id=user_id, group_message_id=group_message_id, seen=True)
            db.session.add(seen_entry)
            db.session.commit()

            return jsonify({'message': 'Group message marked as seen by the user'}), 200
        else:
            return jsonify({'message': 'User has already seen this message'}), 200
    else:
        return jsonify({'message': 'Group message not found'}), 404

""" @app.route('/get_messages/<int:user1_
id>/<int:user2_id>', methods=['GET'])
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
    
    return jsonify(message_list), 200 """

@app.route('/get_messages/<int:user_id>/<int:conversation_id>', methods=['GET'])
def get_messages(user_id, conversation_id):
    # Get the is_group_conversation flag from the query parameters
    is_group_conversation = request.args.get('is_group_conversation', 'false').lower() == 'true'

    if is_group_conversation:
        # It's a group conversation
        group_conversation = GroupConversation.query.get(conversation_id)
        if not group_conversation:
            return jsonify({'message': 'Group conversation not found'}), 400

        # Fetch group messages
        group_messages = GroupMessage.query.filter_by(group_conversation_id=conversation_id).order_by(GroupMessage.timestamp.asc()).all()

        # Prepare the message data
        message_list = []
        for msg in group_messages:
            sender = User.query.get(msg.sender_id)
            if not sender:
                return jsonify({'message': f'User with ID {msg.sender_id} not found'}), 404
            sender_image = sender.profile_image

               # Fetch the users who have seen the message
            seen_users = [seen.user.name for seen in msg.seen_by if seen.seen]

            message_list.append({
                'id': msg.id,
                'sender_id': msg.sender_id,
                'message': msg.message,
                'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'sender_image': sender_image,
                'seen_by': seen_users,  # List of users who have seen the message
                'seen_count': len(seen_users),  # Total count of users who have seen the message
            })
        
        return jsonify(message_list), 200

    else:
        # It's a one-to-one conversation
        # Assuming your conversation model has user1_id and user2_id
        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            return jsonify({'message': 'Conversation not found'}), 400

        user1_id = conversation.user1_id
        user2_id = conversation.user2_id

        # Fetch the messages between the two users
        messages = Message.query.filter(
            ((Message.sender_id == user1_id) & (Message.receiver_id == user2_id)) |
            ((Message.sender_id == user2_id) & (Message.receiver_id == user1_id))
        ).order_by(Message.timestamp.asc()).all()

        # Fetch the user profiles
        user1 = User.query.get(user1_id)
        user2 = User.query.get(user2_id)

        if not user1:
            return jsonify({'message': f'User with ID {user1_id} not found'}), 404
        if not user2:
            return jsonify({'message': f'User with ID {user2_id} not found'}), 404

        message_list = []
        for msg in messages:
            sender_image = user1.profile_image if msg.sender_id == user1_id else user2.profile_image
            receiver_image = user1.profile_image if msg.receiver_id == user1_id else user2.profile_image

            seen_users = []
            if msg.seen:
                # Only one user (either the sender or receiver) will have seen the message
                seen_users = [user1.name if msg.sender_id == user2_id else user2.name]

            message_list.append({
                'id': msg.id,
                'sender_id': msg.sender_id,
                'receiver_id': msg.receiver_id,
                'message': msg.message,
                'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'sender_image': sender_image,
                'receiver_image': receiver_image,
                'seen_by': seen_users,  # Only the user who has seen the message
                'seen_count': len(seen_users),  # 1 user in a one-to-one conversation
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

""" @app.route('/get_conversations/<int:user_id>', methods=['GET'])
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
 """
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
    
@app.route('/get_users', methods=['GET'])
def get_users():
    try:
        # Fetch all users from the database
        users = User.query.all()
        
        # Check if there are users
        if not users:
            return jsonify({'message': 'No users found'}), 404
        
        # Create a list to store user data
        users_data = []
        
        for user in users:
            profile_image = user.profile_image.replace("\\", "/")  # Correct the file path format
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'name': user.name,
                'profile_image': profile_image
            })
        
        # Return the list of users
        return jsonify(users_data), 200

    except Exception as e:
        print(f"Error fetching user data: {e}")
        return jsonify({'message': 'Error fetching users'}), 500
    
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
            'profile_image': profile_image,
            'role': user.role
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

        # Generate a new Ethereum address
        account = w3.eth.account.create()  # Creates a new Ethereum account
        eth_address = account.address  # The generated Ethereum address
        private_key = account._private_key  # Private key as bytes, no need for .hex()

        # Validate Ethereum address
        if not Web3.is_address(eth_address):
            return jsonify({"message": "Invalid Ethereum address"}), 400

        # Check if username or email already exists
        role = request.form['role']
        
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return jsonify({'message': 'Username or email already exists'}), 409

        # Handle profile image upload
        profile_image = request.files.get('profile_image')
        profile_image_path = None
        if profile_image and allowed_file(profile_image.filename):
            filename = secure_filename(profile_image.filename)
            profile_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_image.save(profile_image_path)

        # Hash password using scrypt method (more secure than sha256)
        hashed_password = generate_password_hash(password, method='scrypt')

        # Create new user with encrypted private key
        new_user = User(username=username, email=email, password=hashed_password, name=name, profile_image=profile_image_path, eth_address=eth_address, private_key=private_key,role=role)
        db.session.add(new_user)
        db.session.commit()

        if role == 'Player':
            print("Creating player profile for:", name)
            player_profile = PlayerProfile(
                user_id=new_user.id,
                name=new_user.name,
                photo=new_user.profile_image,
                season='',
                age=0,
                nationality='',
                position='',
                matches=0,
                minutes=0,
                goals=0,
                assists=0,
                club='',
                market_value=0.0,
                total_yellow_cards=0,
                total_red_cards=0,
                score=0.0
            )
            db.session.add(player_profile)

        elif role == 'Coach':
            print("Creating coach profile for:", name)
            coach_profile = Coach_Profile(
                user_id=new_user.id,
                name=new_user.name,
                photo=new_user.profile_image,
                nationality=''
            )
            db.session.add(coach_profile)

        elif role == 'Manager':
            print("Creating manager profile for:", name)
            manager_profile = Manager_Profile(
                user_id=new_user.id,
                name=new_user.name,
                nationality=''
            )
            db.session.add(manager_profile)

        elif role == 'Agent':
            print("Creating agent profile for:", name)
            agent_profile = Agent_Profile(
                user_id=new_user.id,
                name=new_user.name,
                nationality=''
            )
            db.session.add(agent_profile)

        elif role == 'Scout':
            print("Creating scout profile for:", name)
            scout_profile = Scout_Profile(
                user_id=new_user.id,
                name=new_user.name
            )
            db.session.add(scout_profile)

        elif role == 'Staff':
            print("Creating staff profile for:", name)
            staff_profile = Staff_Profile(
                user_id=new_user.id,
                name=new_user.name
            )
            db.session.add(staff_profile)

        # Final commit for any profile added
        db.session.commit()

        # Send welcome email
        msg = Message("Welcome to MetaScout!",
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[email])
        msg.html = f"""
            <p>Hello {name},</p>
            <p>Thank you for signing up on MetaScout. We’re excited to have you with us!</p>
            <p>Best regards,<br>The MetaScout Team</p>
        """
        mail.send(msg)

        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        print("Registration failed:", str(e))
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
@app.route('/verify_document', methods=['POST'])
def verify_document():
    try:
        file = request.files['file']
        role = request.form.get('role')

        if not file or not role:
            return jsonify({'error': 'Missing file or role'}), 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        text = ""

        if filename.lower().endswith('.pdf'):
            # Extract text from PDF by converting each page to image
            doc = fitz.open(file_path)
            for page in doc:
                pix = page.get_pixmap()
                img_path = file_path + "_page.png"
                pix.save(img_path)
                img = Image.open(img_path)
                text += pytesseract.image_to_string(img)
                os.remove(img_path)
            doc.close()
        else:
            # Image file
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)

        print(f"OCR Text Extracted: {text}")  # DEBUG
        print("Received file:", file)
        print("Filename:", file.filename)
        print("Role:", role)


        if role.lower() in text.lower():
            return jsonify({'valid': True})
        else:
            return jsonify({'valid': False})

    except Exception as e:
        print("Error during verification:", e)  # Log error in console
        return jsonify({'error': str(e)}), 500

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

    if user and check_password_hash(user.password, password):
        token = jwt.encode({
            'public_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, app.config['SECRET_KEY'])

        return jsonify({'token': token}), 200
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
            user.password = generate_password_hash(newPassword, method='sha256')
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

    # Debugging: Print the arguments before passing them
    print(f"Post Content: {post_content}")
    print(f"Post Object: {post}")

    try:
        # Call handle_hashtags and ensure all arguments are passed correctly
        handle_hashtags(post=post, job=None,content=post_content)
    except Exception as e:
        print(f"Error while handling hashtags: {str(e)}")
        return jsonify({'error': 'Error processing hashtags'}), 500
    db.session.commit()

    return jsonify({
        'message': 'Post created successfully',
        'post_content': post_content,
        'image_url': uploaded_image,
        'video_url': uploaded_video
    })


@app.route('/hashtag/<string:hashtag>')
def get_posts_by_hashtag(hashtag):
    hashtag_obj = Hashtag.query.filter_by(name=hashtag).first()
    if not hashtag_obj:
        return jsonify([])  # No posts found for the hashtag
    
    # Fetch posts associated with the hashtag through the PostHashtag association table
    post_hashtags = PostHashtag.query.filter_by(hashtag_id=hashtag_obj.id).all()
    
    posts = [
        {
            "id": post.post_id,
            "content": post.content,
            "user_name": post.user.name,
            "created_at": post.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        for post_hashtag in post_hashtags
        for post in [Post.query.get(post_hashtag.post_id)]
    ]
    
    return jsonify(posts)


@app.route('/hashtag/jobs/<string:hashtag>')
def get_jobs_by_hashtag(hashtag):
    hashtag_obj = Hashtag.query.filter_by(name=hashtag).first()
    if not hashtag_obj:
        return jsonify([])  # No jobs found for the hashtag
    
    # Fetch jobs associated with the hashtag through the JobHashtag association table
    job_hashtags = JobHashtag.query.filter_by(hashtag_id=hashtag_obj.id).all()
    
    jobs = []
    for job_hashtag in job_hashtags:
        job = Job.query.get(job_hashtag.job_id)
        if job:
            # Get job post associated with the job
            job_post = JobPost.query.filter_by(job_id=job.id).first()
            if job_post:
                # Get user info from job_post
                user = User.query.get(job_post.user_id)
                if user:
                    jobs.append({
                        "job_id": job.id,
                        "title": job.title,
                        "description": job.description,
                        "type":job.job_type,
                        "location": job.location,
                        "salary": job.salary,
                        "user_id": job_post.user_id,
                        "user_name": user.name,
                        "user_email": user.email,
                        "profile_image":user.profile_image,
                        "posted_at": job_post.date_posted
                    })
    
    return jsonify(jobs)


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

@app.route('/create_group', methods=['POST'])
def create_group():
    try:
        # Get the data from the request
        data = request.get_json()

        # Ensure group_name and user_ids are provided
        group_name = data.get('name')
        user_ids = data.get('user_ids', [])

        if not group_name or not user_ids:
            return jsonify({'message': 'Group name and user IDs are required'}), 400

        # Create a new group conversation
        new_group_conversation = GroupConversation(name=group_name)

        db.session.add(new_group_conversation)
        db.session.commit()

        # Add users to the group conversation
        for user_id in user_ids:
            group_conversation_user = GroupConversationUser(
                group_conversation_id=new_group_conversation.id, 
                user_id=user_id
            )
            db.session.add(group_conversation_user)

        db.session.commit()

        # Return the response
        return jsonify({
            'message': 'Group chat created successfully',
            'group_conversation_id': new_group_conversation.id
        }), 201

    except Exception as e:
        print(f"Error creating group: {e}")
        return jsonify({'message': 'An error occurred while creating the group'}), 500

""" @app.route('/get_group_conversations/<int:user_id>', methods=['GET'])
def get_group_conversations(user_id):
    try:
        # Get all group conversations for a user
        group_conversations = db.session.query(GroupConversation).join(GroupConversationUser).filter(GroupConversationUser.user_id == user_id).all()

        group_conversations_data = []
        for group_conversation in group_conversations:
            # Get the last message in the group conversation
            last_group_message = db.session.query(GroupMessage).filter_by(group_conversation_id=group_conversation.id).order_by(GroupMessage.timestamp.desc()).first()
            last_message_text = last_group_message.message if last_group_message else "No messages yet"
            last_time = last_group_message.timestamp if last_group_message else datetime.utcnow()

            # Count unread messages where the logged-in user is the receiver and the message is not seen
            unread_count = db.session.query(GroupMessage).filter(
                GroupMessage.group_conversation_id == group_conversation.id,
                GroupMessage.seen == False
            ).count()

            group_conversations_data.append({
                'id': group_conversation.id,
                'name': group_conversation.name,
                'last_message': last_message_text,
                'last_time': last_time.strftime('%Y-%m-%d %H:%M:%S'),
                'unread_count': unread_count
            })

        return jsonify(group_conversations_data), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
 """

@app.route('/get_conversations/<int:user_id>', methods=['GET'])
def get_conversations(user_id):
    try:
        all_conversations = []

        # Get one-to-one conversations for a user
        one_to_one_conversations = db.session.query(Conversation).filter(
            (Conversation.user1_id == user_id) | (Conversation.user2_id == user_id)
        ).all()

        # Add one-to-one conversations to the list
        for conv in one_to_one_conversations:
            other_user_id = conv.user1_id if conv.user2_id == user_id else conv.user2_id
            other_user = db.session.query(User).filter_by(id=other_user_id).first()

            # Get the last message in the one-to-one conversation
            last_message = db.session.query(Message).filter_by(conversation_id=conv.id).order_by(Message.timestamp.desc()).first()
            last_message_text = last_message.message if last_message else "No messages yet"
            last_time = last_message.timestamp if last_message else datetime.utcnow()

            unread_count = db.session.query(Message).filter(
                Message.conversation_id == conv.id,
                Message.receiver_id == user_id,
                Message.seen == False
            ).count()

            all_conversations.append({
                'id': conv.id,
                'other_user_id':other_user.id,
                'name': other_user.name,
                'profile_image': other_user.profile_image,
                'last_message': last_message_text,
                'last_time': last_time.strftime('%Y-%m-%d %H:%M:%S'),
                'unread_count': unread_count,
                'type': 'one-to-one',
            })
            # Get group conversations for a user
            group_conversations = db.session.query(GroupConversation).join(GroupConversationUser).filter(GroupConversationUser.user_id == user_id).all()

            # Add group conversations to the list
            for group_conv in group_conversations:
                # Fetch users in the group
                group_users = db.session.query(User).join(GroupConversationUser).filter(GroupConversationUser.group_conversation_id == group_conv.id).all()

                # Get the last group message
                last_group_message = db.session.query(GroupMessage).filter_by(group_conversation_id=group_conv.id).order_by(GroupMessage.timestamp.desc()).first()
                last_message_text = last_group_message.message if last_group_message else "No messages yet"
                last_time = last_group_message.timestamp if last_group_message else datetime.utcnow()

                # Calculate unread count for group messages
                unread_count = db.session.query(GroupMessage).filter(
                    GroupMessage.group_conversation_id == group_conv.id
                ).filter(
                    GroupMessage.id.notin_(
                        db.session.query(GroupMessageSeen.group_message_id).filter(
                            GroupMessageSeen.user_id == user_id,
                            GroupMessageSeen.seen == True
                        )
                    )
                ).count()

                # Prepare the group conversation response
                all_conversations.append({
                    'id': group_conv.id,
                    'name': group_conv.name,
                    'last_message': last_message_text,
                    'last_time': last_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'unread_count': unread_count,
                    'type': 'group',
                    'users': [{'id': user.id, 'name': user.name, 'profile_image': user.profile_image} for user in group_users]  # Include user info
                })

            return jsonify(all_conversations), 200

    except Exception as e:
            return jsonify({"message": str(e)}), 500

@app.route('/add_message_reaction', methods=['POST'])
def add_message_reaction():
    try:
        data = request.get_json()
        message_id = data.get('message_id')
        conversation_id = data.get('conversation_id')
        reaction_name = data.get('reaction_name')
        user_id = data.get('user_id')
        is_group = data.get('is_group')  # Whether it's a group message or not
        
        # Check if the user already reacted to this message in the context of this conversation
        existing_reaction = MessageReaction.query.filter_by(
            message_id=message_id,
            conversation_id=conversation_id,
            user_id=user_id
        ).first()

        if existing_reaction:
            # Update existing reaction
            existing_reaction.reaction_name = reaction_name
        else:
            # Add new reaction if not present
            new_reaction = MessageReaction(
                message_id=message_id,
                conversation_id=conversation_id,
                reaction_name=reaction_name,
                user_id=user_id,
                is_group=is_group
            )
            db.session.add(new_reaction)

        db.session.commit()

        # Fetch updated reactions based on message_id and conversation_id
        reactions = MessageReaction.query.filter_by(
            message_id=message_id, conversation_id=conversation_id
        ).all()

        updated_reactions = {reaction.reaction_name: len([r for r in reactions if r.reaction_name == reaction.reaction_name]) for reaction in reactions}

        return jsonify({
            'status': 'success',
            'message_id': message_id,
            'reactions': updated_reactions
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/get_message_reactions', methods=['GET'])
def get_message_reactions():
    try:
        message_id = request.args.get('message_id', type=int)  # Message ID in the query parameters
        conversation_id = request.args.get('conversation_id', type=int)  # Conversation ID in the query parameters

        # Ensure both message_id and conversation_id are provided
        if not message_id or not conversation_id:
            return jsonify({'status': 'error', 'message': 'Message ID and Conversation ID are required'}), 400

        # Fetch all reactions for the specified message and conversation
        reactions = MessageReaction.query.filter_by(
            message_id=message_id, conversation_id=conversation_id
        ).all()

        # Aggregate reactions by reaction_name
        reaction_counts = {}
        for reaction in reactions:
            if reaction.reaction_name in reaction_counts:
                reaction_counts[reaction.reaction_name] += 1
            else:
                reaction_counts[reaction.reaction_name] = 1

        return jsonify({
            'status': 'success',
            'message_id': message_id,
            'conversation_id': conversation_id,
            'reactions': reaction_counts , # Dictionary of reaction_name and its count
            'is_group':reaction.is_group
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/jobs', methods=['GET'])
def get_jobs():
    jobs = Job.query.all()
    
    # Get all job details along with the user who posted the job
    job_list = []
    for job in jobs:
        job_data = {
            'id': job.id,
            'title': job.title,
            'description': job.description,
            'location': job.location,
            'salary': job.salary,
            'job_type': job.job_type,
            'experience': job.experience,
            'category': job.category,
            'posted_by': {
                'user_id': job.jobposts[0].user.id if job.jobposts else None,  # Get user who posted the job
                'username': job.jobposts[0].user.username if job.jobposts else None,  # Get the username
                'name': job.jobposts[0].user.name if job.jobposts else None,  # Get the user's full name
                'profile_image':job.jobposts[0].user.profile_image if job.jobposts else None,
            },
            'date_posted': job.jobposts[0].date_posted.isoformat() if job.jobposts else None
        }
        job_list.append(job_data)
    
    return jsonify(job_list)


@app.route('/apply/<int:job_id>', methods=['POST'])
def apply_for_job(job_id):
    data = request.get_json()  # Get the data sent in the POST request body
    current_user_id = data.get('current_user')  # Assuming the frontend sends 'current_user' in the request body

    if not current_user_id:
        return jsonify({"error": "User ID not provided"}), 400  # Bad request if user ID is missing

    # Fetch the job to ensure it exists
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    # Create the application
    application = JobApplication(
        job_id=job_id, 
        user_id=current_user_id,  # Use the provided user_id from the request
        application_date=datetime.utcnow()
    )

    # Add the application to the database
    db.session.add(application)
    db.session.commit()

    return jsonify({'message': 'Application submitted successfully'}), 200

    
@app.route('/applications/<int:job_id>', methods=['GET'])
def get_applications_for_job(job_id):
    # Fetch the job by job_id to ensure it exists
    job = Job.query.get(job_id)
    
    if not job:
        return jsonify({"error": "Job not found"}), 404

    # Query all applications for the given job_id
    applications = JobApplication.query.filter_by(job_id=job_id).all()

    if not applications:
        return jsonify({"message": "No applications found for this job"}), 404

    # Format the response to include application details
    application_details = []
    for application in applications:
        application_details.append({
            'application_id': application.id,
            'user_id': application.user_id,
            'application_date': application.application_date,
            'user_name': application.user.name,  # Assuming 'name' is a field in your User model
            'job_title': application.job.title,  # Assuming 'title' is a field in your Job model
        })

    return jsonify({
        "job_id": job_id,
        "applications": application_details
    }), 200


@app.route('/post-job', methods=['POST'])
def post_job():
    if not request.is_json:
        return jsonify({'message': 'Request must be JSON'}), 400
        
    data = request.get_json()

    # Ensure the necessary data is provided in the request
    required_fields = ['title', 'description', 'location', 'salary', 'job_type', 'experience', 'user_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400
    
    try:
        # Extract the user_id from the data
        user_id = data['user_id']

        # Fetch the user from the database using the user_id
        current_user = User.query.get(user_id)

        if not current_user:
            return jsonify({'message': 'User not found'}), 404

        # Create a new Job
        new_job = Job(
            title=data['title'],
            description=data['description'],
            location=data['location'],
            salary=data['salary'],
            job_type=data['job_type'],
            experience=data['experience'],
            category=data.get('category', None)  # optional field
        )

        # Debugging: print the job details before adding to the session
        print(f"Creating Job: {new_job.title}, {new_job.location}, {new_job.salary}")

        db.session.add(new_job)

        # Handle hashtags for the job
        handle_hashtags(post=None, job=new_job, content=new_job.description)

        # Commit to the database
        db.session.commit()

        # Debugging: ensure job is saved
        print(f"Job created successfully with ID: {new_job.id}")

        # Create a new JobPost to associate the Job with the User
        new_job_post = JobPost(
            user_id=current_user.id,
            job_id=new_job.id,
            date_posted=datetime.utcnow()
        )

        # Debugging: print the new job post details before committing
        print(f"Creating JobPost: {new_job_post.user_id}, {new_job_post.job_id}")

        db.session.add(new_job_post)
        db.session.commit()

        # Debugging: Ensure the JobPost is saved
        print(f"JobPost created with ID: {new_job_post.id}")

        return jsonify({'message': 'Job posted successfully'}), 201
    
    except Exception as e:
        # Rollback the session in case of error
        db.session.rollback()
        # Debugging: print the error
        print(f"Error occurred: {str(e)}")
        return jsonify({'message': str(e)}), 500


@app.route('/job/<int:job_id>', methods=['GET'])
def get_single_job(job_id):
    try:
        # Fetch the job along with the user who posted it
        job = Job.query.get_or_404(job_id)  # This will raise a 404 error if the job doesn't exist
        job_post = JobPost.query.filter_by(job_id=job_id).first()  # Fetch the JobPost entry for this job
        
        if not job_post:
            return jsonify({'message': 'Job post details not found'}), 404
        
        # Retrieve the user who posted the job
        user = job_post.user
        
        # Construct response with job and posting details
        job_details = {
            'id': job.id,
            'title': job.title,
            'description': job.description,
            'location': job.location,
            'salary': job.salary,
            'job_type': job.job_type,
            'experience': job.experience,
            'category': job.category,
            'date_posted': job_post.date_posted,
            'posted_by': {
                'user_id': user.id,
                'username': user.username,  # Adjust based on the actual user model field
                'email': user.email,  # Adjust based on your user model
                'profile_image': user.profile_image,  # Adjust based on your user model
            }
        }
        
        return jsonify(job_details), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    


""" @app.route('/update_streak/<int:user_id>', methods=['POST'])
def update_streak(user_id):
    # Get the current date
    current_date = date.today()

    # Try to get the user's existing streak record
    user_streak = UserStreak.query.filter_by(user_id=user_id).first()

    if user_streak:
        # Get the user's last connection date
        last_connection_date = user_streak.connection_dates[-1] if user_streak.connection_dates else None

        # Check if the last connection date exists and calculate if the streak is consecutive
        if last_connection_date:
            last_connection_date = date.fromisoformat(last_connection_date)

            # Check if the last connection was the day before today (consecutive days)
            if last_connection_date == current_date - timedelta(days=1):
                # Consecutive streak, increment current streak
                user_streak.current_streak += 1
            else:
                # Non-consecutive streak (user hasn't logged in for a while), reset current streak to 1
                user_streak.current_streak = 1

            # Update the highest streak if necessary
            if user_streak.current_streak > user_streak.highest_streak:
                user_streak.highest_streak = user_streak.current_streak

        else:
            # If there is no last connection date, it's the user's first login, so set streak to 1
            user_streak.current_streak = 1

        # Update other fields
        user_streak.score += 10  # Increment score by 10, for example
        user_streak.connection_dates.append(current_date.isoformat())  # Append today's date
        user_streak.last_login_date = current_date.isoformat()

    else:
        # If no streak exists, create a new streak record
        user_streak = UserStreak(
            user_id=user_id,
            current_streak=1,  # First login, so streak is 1
            highest_streak=1,  # First login, so highest streak is also 1
            score=10,  # Initial score, can be customized
            connection_dates=[current_date.isoformat()],  # Start with today's date
            daily_points={current_date.isoformat(): 10},  # Points for the first day
            last_login_date=current_date.isoformat()  # Set today's date as the last login
        )
        db.session.add(user_streak)

    try:
        db.session.commit()
        return jsonify({"message": "User streak updated successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500 """

""" 
@app.route('/get_streak/<int:user_id>', methods=['GET'])
def get_streak(user_id):
    streak = UserStreak.query.filter_by(user_id=user_id).first()
    if not streak:
        return jsonify({"message": "No streak data found"}), 404
    
    return jsonify({
        "current_streak": streak.current_streak,
        "highest_streak": streak.highest_streak,
        "score": streak.score,
        "connection_days": streak.connection_dates,
        "daily_points": streak.daily_points,
        "last_login_date": streak.last_login_date
    }) """

def get_top_3_predictions(model, sample_df, group_map):
    """Return top 3 predicted injury group labels (no probabilities)."""
    try:
        if hasattr(model, 'predict_proba'):
            probs = model.predict_proba(sample_df)[0]
        else:
            preds = model.predict(sample_df)
            if preds.ndim == 1:
                probs = [1.0 if i == int(preds[0]) else 0.0 for i in range(len(group_map))]
            else:
                probs = preds[0]

        probs = np.nan_to_num(probs, nan=0.0, posinf=0.0, neginf=0.0)

        top3_idx = np.argsort(probs)[::-1][:3]
        top3_labels = [group_map.get(i, f"Unknown ({i})") for i in top3_idx]

        return top3_labels

    except Exception as e:
        print(f"Error in get_top_3_predictions: {e}")
        return ["Prediction Error"]



@app.post("/predict_injury_type")
def predict_injury():
    data = request.get_json()
    df = pd.DataFrame([data])

    # Convert data types
    df['Age'] = pd.to_numeric(df['Age'], errors='coerce', downcast='integer')
    df['total_minutes_played'] = pd.to_numeric(df['total_minutes_played'], errors='coerce', downcast='float')
    df['matches_played'] = pd.to_numeric(df['matches_played'], errors='coerce', downcast='integer')
    df['total_yellow_cards'] = pd.to_numeric(df['total_yellow_cards'], errors='coerce', downcast='integer')
    df['total_red_cards'] = pd.to_numeric(df['total_red_cards'], errors='coerce', downcast='integer')

    # Encoding
    df['Nationality'] = df['Nationality'].map(nationality_freq)
    df['Team_Name'] = df['Team_Name'].map(teamname_freq)
    df['Position'] = position_encoder.transform(df['Position'])

    # Fatigue level
    season_length_weeks = 40
    df['fatigue_level'] = (df['total_minutes_played'] / df['matches_played']) * (df['matches_played'] / season_length_weeks)
    df['fatigue_level'] = (df['fatigue_level'] / df['fatigue_level'].max()) * 100
    df['fatigue_level'] = df['fatigue_level'].round(2)

    # Date handling
    df['Date_of_Injury'] = pd.to_datetime(df['Date_of_Injury'], errors='coerce')
    df['Date_of_return'] = pd.to_datetime(df['Date_of_return'], errors='coerce')
    df['Days_until_return'] = (df['Date_of_return'] - df['Date_of_Injury']).dt.days

    # Clean
    df.dropna(subset=['total_minutes_played', 'matches_played', 'fatigue_level', 'Days_until_return'], inplace=True)
    df['Season'] = df['Season'].apply(lambda x: int(x.split('/')[0]))
    df = df[scaler.feature_names_in_]

    # Scale
    df_scaled = pd.DataFrame(scaler.transform(df), columns=scaler.feature_names_in_)
    df_scaled['Injury_Grouped_Encoded'] = random.randint(0, 9)  # dummy value if needed

    # Predict
    top_3_predictions = get_top_3_predictions(model, df_scaled, injury_group_map)

    return {"top_3_predicted_injury_groups": top_3_predictions}

@app.route('/get_injury_info', methods=['POST'])
def get_injury_info():
    injury_type = request.json.get("injury_type")

    prompt = f"Estimated recovery time for a '{injury_type}' injury for a football/soccer player. Shortest and fastest answer possible."

    task_data = {
        "name": JobNames.CROW,
        "query": prompt,
    }

    # Run the task
    task_responses = client.run_tasks_until_done(task_data)

    # Check for success in any of the responses
    for response in task_responses:
        if hasattr(response, "has_successful_answer") and response.has_successful_answer:
            formatted_result = {
                "injury_type": injury_type,
                "details": response.answer,
            }
            return jsonify(formatted_result)

    # If none of the responses are successful
    return jsonify({"error": "Failed to fetch data from FutureHouse"}), 500
"""
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def process_and_email(injury_type, recipient_email):
    task_data = {
        "name": JobNames.CROW,
        "query": f"Estimated recovery time for {injury_type} injury for football/soccer player",
    }

    task_response = client.run_tasks_until_done(task_data,timeout=60)

    if isinstance(task_response, list):
        answer = task_response[0].answer
    else:
        answer = getattr(task_response, 'answer', "No valid response")

    msg = MailMessage(subject=f"Recovery Info for {injury_type}",
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[recipient_email],
                  body=f"Here is the estimated recovery time:\n\n{answer}")

    Thread(target=send_async_email, args=(app, msg)).start()

@app.route('/get_injury_info', methods=['POST'])
def get_injury_info():
    data = request.get_json()
    injury_type = data.get("injury_type")
    user_email = data.get("email")

    if not injury_type or not user_email:
        return jsonify({"error": "Missing injury_type or email"}), 400

    Thread(target=process_and_email, args=(injury_type, user_email)).start()

    return jsonify({"message": "Processing started. You'll receive an email when it's ready."})"""

#blockchain and streak
# Check MetaCoins Balance
@app.route('/check_balance/<int:user_id>', methods=['GET'])
def check_balance(user_id):
    try:
        user = User.query.filter_by(id=user_id).first()

        if user:
            eth_address = user.eth_address  # Get user's Ethereum address
            balance = contract.functions.balanceOf(eth_address).call()  # Fetch balance from smart contract

            return jsonify({
                "message": "Balance fetched successfully",
                "balance": balance
            }), 200
        else:
            return jsonify({"error": "User not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Burn MetaCoins Route
@app.route('/burn_metacoins', methods=['POST'])
def burn_metacoins():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        burn_amount = data.get("amount")

        if burn_amount <= 0:
            return jsonify({"error": "Amount must be greater than zero"}), 400

        user = User.query.filter_by(id=user_id).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        user_address = user.eth_address
        current_balance = contract.functions.balanceOf(user_address).call()

        if current_balance < burn_amount:
            return jsonify({"error": "Not enough MetaCoins to burn"}), 400

        # Prepare transaction to call burnFrom(user_address, amount)
        nonce = w3.eth.get_transaction_count(owner_address)
        txn = contract.functions.burnFrom(user_address, burn_amount).build_transaction({
            "chainId": 11155111,
            "gas": 150000,
            "gasPrice": w3.to_wei("10", "gwei"),
            "nonce": nonce
        })

        signed_txn = w3.eth.account.sign_transaction(txn, private_key=owner_private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return jsonify({
            "message": f"{burn_amount} MetaCoins burned from user successfully!",
            "tx_hash": tx_hash.hex()
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Updated Streak Route (Update only if it's the next day)
@app.route('/get_streak/<int:user_id>', methods=['GET'])
def get_and_update_streak(user_id):
    current_date = date.today()
    user_streak = UserStreak.query.filter_by(user_id=user_id).first()

    try:
        if user_streak:
            last_connection_date = (
                date.fromisoformat(user_streak.connection_dates[-1])
                if user_streak.connection_dates else None
            )

            already_logged_in_today = (last_connection_date == current_date)

            if already_logged_in_today:
                # No update, just return current state
                return jsonify({
                    "message": "Already logged in today",
                    "current_streak": user_streak.current_streak,
                    "highest_streak": user_streak.highest_streak,
                    "score": user_streak.score,
                    "connection_days": user_streak.connection_dates,
                    "last_login_date": user_streak.last_login_date,
                    "current_streak_day": user_streak.current_streak,
                    "already_logged_in_today": True
                }), 200

            # If last login was yesterday, increment streak
            if last_connection_date == current_date - timedelta(days=1):
                user_streak.current_streak += 1
                user_streak.score = user_streak.current_streak * 10
            else:
                # Missed a day or no login history — reset streak
                user_streak.current_streak = 1
                user_streak.score = 10

            user_streak.connection_dates.append(current_date.isoformat())
            user_streak.last_login_date = current_date.isoformat()

        else:
            # First-time login
            user_streak = UserStreak(
                user_id=user_id,
                current_streak=1,
                highest_streak=1,
                score=10,
                connection_dates=[current_date.isoformat()],
                daily_points={},
                last_login_date=current_date.isoformat()
            )
            db.session.add(user_streak)

        # Update highest streak
        if user_streak.current_streak > user_streak.highest_streak:
            user_streak.highest_streak = user_streak.current_streak

        db.session.commit()

        return jsonify({
            "message": "Streak updated",
            "current_streak": user_streak.current_streak,
            "highest_streak": user_streak.highest_streak,
            "score": user_streak.score,
            "connection_days": user_streak.connection_dates,
            "last_login_date": user_streak.last_login_date,
            "current_streak_day": user_streak.current_streak,
            "already_logged_in_today": False
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    

@app.route("/mint_tokens", methods=["POST"])
def mint_tokens():
    try:
        data = request.get_json()
        mint_amount = data.get("amount")

        if not mint_amount:
            return jsonify({"error": "Missing mint amount"}), 400

        # Load contract owner's private key (from secure source)
        if not owner_private_key:
            return jsonify({"error": "Owner private key not configured"}), 500

        # Mint tokens to the contract owner’s wallet (owner will later transfer if needed)
        nonce = w3.eth.get_transaction_count(owner_address)

        txn = contract.functions.ownerMintTokens(mint_amount).build_transaction({
            "chainId": 11155111,  # Change if not on mainnet
            "gas": 150000,
            "gasPrice": w3.to_wei("10", "gwei"),
            "nonce": nonce,
            "value": 0  # Ensure no ETH is sent with the transaction
        })

        signed_txn = w3.eth.account.sign_transaction(txn, private_key=owner_private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return jsonify({
            "message": f"Minted {mint_amount} tokens to owner wallet.",
            "tx_hash": tx_hash.hex()
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route('/add_metacoins_streak', methods=['POST'])
def add_metacoins_streak():
    try:
        data = request.get_json()
        user_id = data.get("user_id")

        user = User.query.filter_by(id=user_id).first()
        user_streak = UserStreak.query.filter_by(user_id=user_id).first()

        if not user or not user_streak:
            return jsonify({"error": "User or streak not found"}), 404

        current_date = date.today()
        last_connection_date = (
            date.fromisoformat(user_streak.connection_dates[-1])
            if user_streak.connection_dates else None
        )

        # Check if already rewarded today (optional: store last_reward_date to prevent double claim)
        if last_connection_date == current_date:
            # Reward allowed if it's the first login today
            pass
        elif last_connection_date == current_date - timedelta(days=1):
            # Maintained streak, continue
            pass
        elif not last_connection_date:
            # First ever login — allow reward
            pass
        else:
            return jsonify({"message": "Streak not maintained. No MetaCoins added."}), 200

        # Calculate reward
        streak_meta_coins = user_streak.score // 10
        if streak_meta_coins <= 0:
            return jsonify({"message": "No MetaCoins to reward yet."}), 200

        # Step 1: Mint to owner
        owner_nonce = w3.eth.get_transaction_count(owner_address)
        mint_txn = contract.functions.ownerMintTokens(streak_meta_coins).build_transaction({
            "chainId": 11155111,
            "gas": 150000,
            "gasPrice": w3.to_wei("10", "gwei"),
            "nonce": owner_nonce,
        })
        signed_mint_txn = w3.eth.account.sign_transaction(mint_txn, private_key=owner_private_key)
        mint_tx_hash = w3.eth.send_raw_transaction(signed_mint_txn.raw_transaction)
        mint_receipt = w3.eth.wait_for_transaction_receipt(mint_tx_hash)

        # Step 2: Transfer to user
        transfer_nonce = owner_nonce + 1
        transfer_txn = contract.functions.transfer(user.eth_address, streak_meta_coins).build_transaction({
            "chainId": 11155111,
            "gas": 150000,
            "gasPrice": w3.to_wei("10", "gwei"),
            "nonce": transfer_nonce,
        })
        signed_transfer_txn = w3.eth.account.sign_transaction(transfer_txn, private_key=owner_private_key)
        transfer_tx_hash = w3.eth.send_raw_transaction(signed_transfer_txn.raw_transaction)
        transfer_receipt = w3.eth.wait_for_transaction_receipt(transfer_tx_hash)

        return jsonify({
            "message": f"{streak_meta_coins} MetaCoins rewarded successfully for streak!",
            "mint_tx_hash": mint_tx_hash.hex(),
            "transfer_tx_hash": transfer_tx_hash.hex()
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


    
app.app_context().push()
if __name__ == '__main__':
    app.run(debug=True)

@app.route('/get_players', methods=['GET'])
def get_players():
    try:
        players = PlayerProfile.query.all()
        players_data = []

        for player in players:
            profile_image = player.photo.replace("\\", "/") if player.photo else ""

            players_data.append({
                'id': player.id,
                'name': player.name,
                'age': player.age,
                'position': player.position,
                'club': player.club,
                'photo': profile_image,
                'score': player.score,
            })

        return jsonify(players_data), 200

    except Exception as e:
        print(f"Error fetching players: {e}")
        return jsonify({'message': 'Error fetching players'}), 500
    

@app.route('/rate_player', methods=['POST'])
def rate_player():
    try:
        data = request.get_json()
        player_id = data.get('id')
        score = data.get('score')

        user_id = data.get('user_id')
        coach = User.query.get(user_id)

        print("Coach ID:", user_id, "role:", coach.role)
        
        if coach.role != "Coach":
            return jsonify({'message': 'Only coaches can rate players'}), 403

        # Empêcher une double notation
        existing_rating = PlayerRating.query.filter_by(coach_id=user_id, player_id=player_id).first()
        if existing_rating:
            return jsonify({'message': 'You already rated this player'}), 400

        # Ajouter la note
        new_rating = PlayerRating(coach_id=user_id, player_id=player_id, score=score)
        db.session.add(new_rating)

        # Recalcul de la moyenne
        all_ratings = PlayerRating.query.filter_by(player_id=player_id).all()
        average = round(sum(r.score for r in all_ratings) / len(all_ratings), 2)

        player = PlayerProfile.query.get(player_id)
        player.score = average

         # Création de la notification pour le joueur
        notification_message = f"Coach {coach.name} has rated you {score}/5."
        notification = Notification(
            player_id=player_id,
            coach_id=user_id,
            message=notification_message,
            timestamp=datetime.utcnow()  # Timestamp actuel
        )
        db.session.add(notification)

        db.session.commit()
        
        return jsonify({'message': 'Score added', 'average_score': average}), 200

    except Exception as e:
        print(f"Error rating player: {e}")
        return jsonify({'message': 'Internal server error'}), 500
    
@app.route('/player_id/<int:user_id>', methods=['GET'])
def get_player_id(user_id):
    player = PlayerProfile.query.filter_by(user_id=user_id).first()
    if player:
        return jsonify({'player_id': player.id})
    return jsonify({'message': 'Player not found'}), 404

@app.route('/notifications/<int:player_id>', methods=['GET'])
def get_notifications(player_id):
    notifications = Notification.query.filter_by(player_id=player_id).order_by(Notification.timestamp.desc()).all()
    notif_list = [{
        'id': n.id,
        'message': n.message,
        'timestamp': n.timestamp.isoformat(),
        'is_read': n.is_read,
        'coach_image': n.coach.profile_image if n.coach else None
    } for n in notifications]

    return jsonify(notif_list), 200

@app.route('/notifications/read/<int:notif_id>', methods=['POST'])
def mark_notification_read(notif_id):
    notif = Notification.query.get(notif_id)
    if notif:
        notif.is_read = True
        db.session.commit()
        return jsonify({'message': 'Notification marked as read'}), 200
    return jsonify({'message': 'Notification not found'}), 404
