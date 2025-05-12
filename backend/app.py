import base64
import os
import random
import traceback
from flask import Flask, Request, json, request, jsonify, send_from_directory, url_for, make_response
from tkinter.tix import Control
from flask_mail import Message as MailMessage
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import numpy as np
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import Enum
from sqlalchemy import Enum as SQLAlchemyEnum  # Renamed to avoid conflict
import jwt
from functools import wraps
from datetime import datetime, timedelta
from datetime import date
from flask_mail import Mail
import joblib
import pandas as pd
from futurehouse_client import FutureHouseClient, JobNames
from futurehouse_client.models.app import TaskRequest
from threading import Thread
from web3 import Web3
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image
import traceback  # Import traceback for error logging
import enum  # Import Python's standard enum
import threading # Added import for threading
from flask import current_app
import importlib.util # Add this import at the top of your app.py
import sys # Add this import
import subprocess # Add this import for calling ffmpeg
# BO 6
from ml.speech.stt import WhisperTranscriber
from ml.video.extract import extract_audio
from ml.speech.tts import ElevenLabsTTS
from ml.speech.caption import CaptionEnhancer
from ml.video.overlay import overlay_subtitles
from ml.utils.srt import SRTFormatter
from ml.summarizer.gemma_summarizer import GemmaSummarizerService
import re
import nltk
import shutil
import torch
import torch.nn as nn
import unicodedata
from fuzzywuzzy import process
import pickle
import time


# Set up upload folder for processed videos
PROCESSED_FOLDER = os.path.join(os.getcwd(), 'processed_videos')
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


transcriber = WhisperTranscriber()
tts_engine = ElevenLabsTTS()

# Initialize additional components
caption_enhancer = CaptionEnhancer()
srt_formatter = SRTFormatter()


app = Flask(__name__, template_folder='templates')
CORS(app, resources={r"/*": {"origins": "http://localhost:3000", "supports_credentials": True}})
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

# Set up folder for tactical analysis outputs
TACTICS_OUTPUT_FOLDER = os.path.join(os.getcwd(), 'results')
os.makedirs(TACTICS_OUTPUT_FOLDER, exist_ok=True)
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  
pytesseract.pytesseract.tesseract_cmd =r'd:\programFiles\Tesseract-OCR\tesseract.exe'
w3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/2264fb8767644f77889c230508451721"))

with open('MetaCoinABI.json', 'r') as f:
    abi = json.load(f)

# Contract address
contract_address = Web3.to_checksum_address("0x2dE8B83c77ecb2FB47c35702E3879E070F79C58d")
owner_private_key="e8be4c05fe6f9bfa3fb7e64e75723d31d8a48dd2f327e1ff09e9dadecd3c3622"
# Owner wallet (the deployer of MetaCoin)
owner_address = w3.to_checksum_address("0x16c7cc09EBA8039EBE2d6d14B0dAA299F77C3FF1")
contract = w3.eth.contract(address=contract_address, abi=abi)

API_KEY = "NNh90Pfy1FpqllYwQz9oQg.platformv01.eyJqdGkiOiIyN2VkNGM5Ny0wNGEwLTQ1YTQtOGM2Zi1hZWFmMWFiOWIwMDQiLCJzdWIiOiJsQk5zNmI1RnVOYlQwVlJCaENrQ2pHTlo3aW8xIiwiaWF0IjoxNzQ2OTk3NDQ5fQ.c5uuDJvVkLIuyznumKUbUvTDRlgg4OTtyn9e9tA1CNM"
client = FutureHouseClient(api_key=API_KEY)
# Load model and encoder
model = joblib.load('modeling/injury_type_model.pkl')
label_encoder = joblib.load('modeling/injury_label_encoder.pkl')
# Load preprocessing objects
scaler = joblib.load('modeling/scaler.pkl')
position_encoder = joblib.load('modeling/position_encoder.pkl')
injury_encoder = joblib.load('modeling/injury_label_encoder.pkl')
nationality_freq_df = pd.read_csv('modeling/nationality_mapping.csv')
teamname_freq_df = pd.read_csv('modeling/teamname_mapping.csv')
nationality_freq = dict(zip(nationality_freq_df['Value'], nationality_freq_df['Encoded']))
teamname_freq = dict(zip(teamname_freq_df['Value'], teamname_freq_df['Encoded']))


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





performance_model = joblib.load('modelCareer/performance_model.pkl')
longevity_model = joblib.load('modelCareer/longevity_model.pkl')
imputer = joblib.load('modelCareer/imputer.pkl')
with open('modelCareer/model_metadata.json', 'r') as f:
    metadata = json.load(f)
    feature_names = metadata['feature_names']

DATA_PATH = os.path.join(os.path.dirname(__file__), 'modelCareer/player_stats_with_positions.csv')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    profile_image = db.Column(db.String(255))
    eth_address = db.Column(db.String(42), unique=True, nullable=False)
    private_key = db.Column(db.String(256), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)

    player_profile = db.relationship('PlayerProfile', back_populates='user', uselist=False)
    agency_profile = db.relationship('AgencyProfile', back_populates='user', uselist=False)
    agent_profile = db.relationship('AgentProfile', back_populates='user', uselist=False)
    coach_profile = db.relationship('CoachProfile', back_populates='user', uselist=False)
    staff_profile = db.relationship('StaffProfile', back_populates='user', uselist=False)
    scout_profile = db.relationship('ScoutProfile', back_populates='user', uselist=False)
    manager_profile = db.relationship('ManagerProfile', back_populates='user', uselist=False)
    club_profile = db.relationship('ClubProfile', back_populates='user', uselist=False)

    def __init__(self,username, email, password ,name, profile_image,eth_address,private_key, role):
        self.username = username
        self.email = email
        self.password = password
        self.name = name
        self.profile_image = profile_image
        self.eth_address = eth_address
        self.private_key = private_key
        self.role = role

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

class Skills(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

    skill = db.Column(db.Integer, nullable=True)
    ratingS1 = db.Column(db.Integer, unique=False, nullable=True)

agency_club_association = db.Table(
    'agency_club_association',
    db.Column('agency_id', db.Integer, db.ForeignKey('agency_profile.id'), primary_key=True),
    db.Column('club_id', db.Integer, db.ForeignKey('club_profile.id'), primary_key=True)
)


class PlayerProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club_profile.id'))
    agency_id = db.Column(db.Integer, db.ForeignKey('agency_profile.id'))

    name = db.Column(db.String(20))
    season = db.Column(db.String(20))
    age = db.Column(db.Integer)
    nationality = db.Column(db.String(50))
    position = db.Column(db.String(50))
    matches = db.Column(db.Integer)
    minutes = db.Column(db.Integer)
    goals = db.Column(db.Integer)
    assists = db.Column(db.Integer)
    club = db.Column(db.String(100))
    market_value = db.Column(db.Float)
    total_yellow_cards = db.Column(db.Integer)
    total_red_cards = db.Column(db.Integer)

    performance_metrics = db.Column(db.Float)
    media_sentiment = db.Column(db.Float)

    aggression = db.Column(db.Integer)
    reactions = db.Column(db.Integer)
    long_pass = db.Column(db.Integer)
    stamina = db.Column(db.Integer)
    strength = db.Column(db.Integer)
    sprint_speed = db.Column(db.Integer)
    agility = db.Column(db.Integer)
    jumping = db.Column(db.Integer)
    heading = db.Column(db.Integer)
    free_kick_accuracy = db.Column(db.Integer)
    volleys = db.Column(db.Integer)

    gk_positioning = db.Column(db.Integer)
    gk_diving = db.Column(db.Integer)
    gk_handling = db.Column(db.Integer)
    gk_kicking = db.Column(db.Integer)
    gk_reflexes = db.Column(db.Integer)

    score = db.Column(db.Float)
    photo = db.Column(db.String(255))

    user = db.relationship('User', back_populates='player_profile')
    agency = db.relationship('AgencyProfile', back_populates='player_profiles')
    club_profile = db.relationship('ClubProfile', back_populates='player_profiles')


class AgencyProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

    country = db.Column(db.String(80))

    user = db.relationship('User', back_populates='agency_profile')
    player_profiles = db.relationship('PlayerProfile', back_populates='agency')
    agents = db.relationship('AgentProfile', back_populates='agency')
    clubs = db.relationship('ClubProfile', secondary='agency_club_association', back_populates='agencies')


class ClubProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

    country = db.Column(db.String(80))
    competition = db.Column(db.String(100))
    squad_size = db.Column(db.Integer)

    user = db.relationship('User', back_populates='club_profile')
    player_profiles = db.relationship('PlayerProfile', back_populates='club_profile')
    agencies = db.relationship('AgencyProfile', secondary='agency_club_association', back_populates='clubs')
    staff_members = db.relationship('StaffProfile', back_populates='club')
    coaches = db.relationship('CoachProfile', back_populates='club')
    scouts = db.relationship('ScoutProfile', back_populates='club')
    managers = db.relationship('ManagerProfile', back_populates='club')


class AgentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    agency_id = db.Column(db.Integer, db.ForeignKey('agency_profile.id'))

    name = db.Column(db.String(80))
    nationality = db.Column(db.String(80))
    date_of_appointment = db.Column(db.Date)
    date_of_end_contract = db.Column(db.Date)
    years_of_experience = db.Column(db.Integer)
    qualification = db.Column(db.String(120))
    availability = db.Column(db.Boolean, default=True)

    user = db.relationship('User', back_populates='agent_profile')
    agency = db.relationship('AgencyProfile', back_populates='agents')


class CoachProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club_profile.id'))

    name = db.Column(db.String(80), unique=True, nullable=False)
    nationality = db.Column(db.String(80))
    date_of_appointment = db.Column(db.Date)
    date_of_end_contract = db.Column(db.Date)
    years_of_experience = db.Column(db.Integer)
    qualification = db.Column(db.String(120))
    availability = db.Column(db.Boolean, default=True)
    photo = db.Column(db.String(255))

    user = db.relationship('User', back_populates='coach_profile')
    club = db.relationship('ClubProfile', back_populates='coaches')


class StaffProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club_profile.id'))

    name = db.Column(db.String(80))
    nationality = db.Column(db.String(80))
    date_of_appointment = db.Column(db.Date)
    date_of_end_contract = db.Column(db.Date)
    years_of_experience = db.Column(db.Integer)
    qualification = db.Column(db.String(120))
    availability = db.Column(db.Boolean, default=True)

    user = db.relationship('User', back_populates='staff_profile')
    club = db.relationship('ClubProfile', back_populates='staff_members')


class ScoutProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club_profile.id'))

    name = db.Column(db.String(80))
    nationality = db.Column(db.String(80))
    date_of_appointment = db.Column(db.Date)
    date_of_end_contract = db.Column(db.Date)
    years_of_experience = db.Column(db.Integer)
    qualification = db.Column(db.String(120))
    availability = db.Column(db.Boolean, default=True)

    user = db.relationship('User', back_populates='scout_profile')
    club = db.relationship('ClubProfile', back_populates='scouts')


class ManagerProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club_profile.id'))

    name = db.Column(db.String(80))
    nationality = db.Column(db.String(80))
    date_of_appointment = db.Column(db.Date)
    date_of_end_contract = db.Column(db.Date)
    years_of_experience = db.Column(db.Integer)
    qualification = db.Column(db.String(120))
    availability = db.Column(db.Boolean, default=True)

    total_matches = db.Column(db.Integer)
    wins = db.Column(db.Integer)
    draws = db.Column(db.Integer)
    losses = db.Column(db.Integer)
    ppg = db.Column(db.Float)

    user = db.relationship('User', back_populates='manager_profile')
    club = db.relationship('ClubProfile', back_populates='managers')



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
    reaction_type = db.Column(Enum('like', 'love', 'laugh', 'wow', 'angry', 'sad', name="reaction_type_enum"))
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


# Define an Enum for match status using Python's enum
class MatchStatus(enum.Enum):
    UPLOADED = 'uploaded'
    PROCESSING_CAPTIONS = 'processing_captions'
    CAPTIONS_READY = 'captions_ready'
    ANALYSIS_COMPLETE = 'analysis_complete'  # Example, can add more
    ERROR = 'error'

# Define an Enum for tactical analysis status
class TacticalAnalysisStatus(enum.Enum):
    NOT_STARTED = 'not_started'
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=True)  # Optional title for the match/highlight
    team1_name = db.Column(db.String(100), nullable=False)
    team2_name = db.Column(db.String(100), nullable=False)
    team1_score = db.Column(db.Integer, nullable=True)  # Score might not always be known/relevant for highlights
    team2_score = db.Column(db.Integer, nullable=True)
    match_date = db.Column(db.DateTime, nullable=True)  # Date of the match
    competition = db.Column(db.String(100), nullable=True)  # e.g., LALIGA, Premier League
    video_filename = db.Column(db.String(255), nullable=False)  # Just the filename, path constructed dynamically
    srt_filename = db.Column(db.String(255), nullable=True)  # Filename of the generated SRT
    captioned_video_filename = db.Column(db.String(255), nullable=True)  # Filename of the video with overlaid captions
    summary = db.Column(db.Text, nullable=True)  # Store generated summary
    status = db.Column(SQLAlchemyEnum(MatchStatus, name='match_status_enum'), default=MatchStatus.UPLOADED, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    error_message = db.Column(db.Text, nullable=True)  # Store error details if processing fails

    # New fields for tactical analysis
    tactical_analysis_status = db.Column(SQLAlchemyEnum(TacticalAnalysisStatus, name='tactical_analysis_status_enum'), default=TacticalAnalysisStatus.NOT_STARTED, nullable=False)
    tactical_overlay_video_filename = db.Column(db.String(255), nullable=True) # Filename for tactical overlay video, relative to TACTICS_OUTPUT_FOLDER
    heatmaps_generated = db.Column(db.Boolean, default=False, nullable=False) # Flag if heatmaps are generated


    user = db.relationship('User', backref='matches', lazy=True)

    def get_video_url(self):
        # Construct the URL based on the stored filename
        return url_for('uploaded_file', filename=self.video_filename, _external=True) if self.video_filename else None

    def get_srt_url(self):
        # Construct the URL for the SRT file
        return url_for('serve_processed_file', filename=self.srt_filename, _external=True) if self.srt_filename else None

    def get_captioned_video_url(self):
        # Construct the URL for the captioned video file
        return url_for('serve_processed_file', filename=self.captioned_video_filename, _external=True) if self.captioned_video_filename else None

    def get_tactical_overlay_video_url(self):
        if not self.tactical_overlay_video_filename:
            # print(f"Match {self.id}: tactical_overlay_video_filename is None.")
            return None
        
        # Normalize path separators first
        path_from_db = self.tactical_overlay_video_filename.replace('\\', '/')
        
        filename_for_url = path_from_db # Assume it's already relative as per setting logic

        # Defensive check: If path_from_db were an absolute path, try to make it relative
        # This should not be necessary if tactical_overlay_video_filename is always set as f"{match_id}/{filename}"
        if os.path.isabs(path_from_db):
            current_app.logger.warn(f"[Match {self.id}] tactical_overlay_video_filename ('{path_from_db}') was stored as an absolute path. Attempting to make it relative to TACTICS_OUTPUT_FOLDER.")
            abs_tactics_folder = os.path.abspath(TACTICS_OUTPUT_FOLDER)
            # Ensure abs_tactics_folder ends with a separator for correct prefix removal
            abs_tactics_folder_with_sep = os.path.join(abs_tactics_folder, '') 
            
            if path_from_db.startswith(abs_tactics_folder_with_sep):
                filename_for_url = path_from_db[len(abs_tactics_folder_with_sep):]
                current_app.logger.info(f"[Match {self.id}] Converted absolute path to relative: '{filename_for_url}'")
            else:
                current_app.logger.error(f"[Match {self.id}] Absolute path '{path_from_db}' is not within TACTICS_OUTPUT_FOLDER '{abs_tactics_folder}'. Cannot generate valid URL.")
                return None
        
        try:
            # filename_for_url should now be correctly relative (e.g., "1/analysis_output.avi")
            generated_url = url_for('serve_tactics_output_file', filename=filename_for_url, _external=True)
            
            # Enhanced logging
            abs_tactics_output_folder = os.path.abspath(TACTICS_OUTPUT_FOLDER)
            expected_local_file = os.path.join(abs_tactics_output_folder, filename_for_url)
            
            print(f"[Match {self.id}] Filename for URL construction: '{filename_for_url}'")
            # print(f"[Match {self.id}] Base for serving files (TACTICS_OUTPUT_FOLDER): '{abs_tactics_output_folder}'")
            # print(f"[Match {self.id}] Expected local file to be served: '{expected_local_file}'")
            print(f"[Match {self.id}] Generated URL: '{generated_url}'")
            
            return generated_url
        except RuntimeError as e: 
            # This can happen if url_for is called outside app context
            current_app.logger.error(f"Error generating URL for tactical_overlay_video_filename '{filename_for_url}': {str(e)}. Ensure Flask app context.")
            # Fallback or re-raise depending on desired behavior
            raise e 
        except Exception as e:
            current_app.logger.error(f"Unexpected error generating URL for tactical_overlay_video_filename '{filename_for_url}': {str(e)}")
            # import traceback
            # traceback.print_exc()
            return None

    def to_dict(self):
        display_status_value = None

        # Prioritize tactical analysis status if it's active, completed, or failed
        if self.tactical_analysis_status and \
           self.tactical_analysis_status not in [TacticalAnalysisStatus.NOT_STARTED]:
            display_status_value = self.tactical_analysis_status.value
        # Otherwise, use the general match status (captioning, uploaded, etc.)
        elif self.status:
            display_status_value = self.status.value
        # Fallback if neither is set (should ideally not happen if initialized properly)
        else:
            display_status_value = TacticalAnalysisStatus.NOT_STARTED.value 

        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'team1_name': self.team1_name,
            'team2_name': self.team2_name,
            'team1_score': self.team1_score,
            'team2_score': self.team2_score,
            'match_date': self.match_date.strftime('%Y-%m-%d') if self.match_date else None,
            'competition': self.competition,
            'video_url': self.get_video_url(),
            'srt_url': self.get_srt_url(),
            'captioned_video_url': self.get_captioned_video_url(),
            'summary': self.summary,
            'status': display_status_value, # This is the primary status for MatchesList
            'uploaded_at': self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
            'error_message': self.error_message,
            # Keep the specific tactical_analysis_status for detailed views if needed
            'tactical_analysis_status': self.tactical_analysis_status.value if self.tactical_analysis_status else None,
            'tactical_overlay_video_url': self.get_tactical_overlay_video_url(),
            'heatmaps_generated': self.heatmaps_generated
        }
    
def process_new_player_data(career_stats):
    df = pd.DataFrame(career_stats)

    # Convert key statistical columns to numeric types
    # These might come as strings from the frontend form
    numeric_cols = ['age', 'matches', 'minutes', 'goals', 'assists']
    for col in numeric_cols:
        if col in df.columns: # Check if column exists before trying to convert
            df[col] = pd.to_numeric(df[col], errors='coerce') # errors='coerce' will turn unparseable strings into NaN

    df['position'] = df['position'].str.upper().str.strip()
    valid_positions = ['DF', 'MF', 'FW']
    df['position'] = df['position'].apply(lambda x: x if x in valid_positions else 'FW')
    
    # df['minutes'] is now numeric (float64) or contains NaN.
    # Create 'minutes_adj' for division, ensuring it's non-zero and numeric.
    # 1. Fill NaN in 'minutes' with 0.0 (if a player had missing minutes for a season)
    # 2. Replace 0.0 minutes with 1.0 to avoid division by zero.
    df['minutes_adj'] = df['minutes'].fillna(0.0).replace(0.0, 1.0)

    # df['goals'] and df['assists'] are now numeric (float64) or contains NaN.
    # Calculations will propagate NaN, which is fine as the imputer handles it later.
    df['goals_per_90'] = (df['goals'] * 90) / df['minutes_adj']
    df['assists_per_90'] = (df['assists'] * 90) / df['minutes_adj']
    
    primary_position = df['position'].mode()[0] if not df['position'].mode().empty else 'FW'
    pos_DF = 1 if primary_position == 'DF' else 0
    pos_MF = 1 if primary_position == 'MF' else 0
    pos_FW = 1 if primary_position == 'FW' else 0
    
    max_minutes = 5000 # This constant is used for position score calculation
    if primary_position == 'FW':
        df['position_score'] = 0.7 * df['goals_per_90'] + 0.3 * df['assists_per_90']
    elif primary_position == 'MF':
        df['position_score'] = 0.4 * df['goals_per_90'] + 0.6 * df['assists_per_90']
    else: # DF
        # Ensure df['minutes'] is numeric here for the division
        df['position_score'] = 0.2 * df['goals_per_90'] + 0.3 * df['assists_per_90'] + 0.5 * (df['minutes'] / max_minutes)
    
    last_3 = df.iloc[-3:] if len(df) >= 3 else df
    weights = np.arange(1, len(last_3)+1)
    def safe_avg(series): return np.average(series.dropna(), weights=weights[:len(series.dropna())]) if not series.dropna().empty else 0.0

    last_season = df.iloc[-1]
    matches_adj = max(last_season['matches'], 1) if pd.notna(last_season['matches']) else 1
    minutes_adj_last_season = max(last_season['minutes'], 1) if pd.notna(last_season['minutes']) else 1 # Renamed to avoid conflict with df['minutes_adj']

    # Calculate rolling_3season_mins and rolling_3season_mins_pct carefully with potential NaNs
    rolling_3season_mins = df['minutes'].dropna().tail(3).mean() if len(df['minutes'].dropna()) >= 1 else 0.0
    
    # For rolling_3season_mins_pct, ensure 'mp' is also numeric
    if 'mp' not in df.columns or not pd.api.types.is_numeric_dtype(df['mp']): # 'mp' might be named 'matches' in input
        df['mp_numeric'] = pd.to_numeric(df.get('matches', df.get('mp')), errors='coerce').fillna(0) # Use 'matches' if 'mp' not present
    else:
        df['mp_numeric'] = df['mp'].fillna(0)

    possible_minutes_per_season = (df['mp_numeric'] * 90).replace(0, 1) # Avoid division by zero
    minutes_pct_this_season = (df['minutes'].fillna(0) / possible_minutes_per_season)
    rolling_3season_mins_pct = minutes_pct_this_season.dropna().tail(3).mean() if len(minutes_pct_this_season.dropna()) >=1 else 0.0


    features = {
        'age': last_season['age'],
        'pos_DF': pos_DF,
        'pos_MF': pos_MF,
        'pos_FW': pos_FW,
        'team_encoded': 0.5, # Neutral value for new player
        'season_start': 2025, # Assuming prediction for next typical season start
        'goals_per_90': last_season['goals_per_90'],
        'assists_per_90': last_season['assists_per_90'],
        'position_score': last_season['position_score'],
        'goals_per_90_weighted_recent': safe_avg(last_3['goals_per_90']),
        'assists_per_90_weighted_recent': safe_avg(last_3['assists_per_90']),
        'position_score_weighted_recent': safe_avg(last_3['position_score']),
        'minutes_weighted_recent': safe_avg(last_3['minutes']), # This was duplicated, keeping one
        'mins_per_appearance': minutes_adj_last_season / matches_adj,
        'availability': (matches_adj / df['matches'].max()) if pd.notna(df['matches'].max()) and df['matches'].max() > 0 else 1.0,
        'seasons_since_debut': len(df),
        'recent_form': df['position_score'].dropna().tail(3).mean() if len(df['position_score'].dropna()) >=1 else df['position_score'].mean(), # Ensure mean of non-NaN
        'team_strength': 0.5, # Neutral value
        'injury_prone': int((minutes_adj_last_season / (matches_adj * 90)) < 0.6) if matches_adj > 0 else 0,
        'mins_pct_possible': (minutes_adj_last_season / (matches_adj * 90)) if matches_adj > 0 else 1.0,
        'rolling_3season_mins': rolling_3season_mins,
        'rolling_3season_mins_pct': rolling_3season_mins_pct
        # 'minutes_weighted_recent' was listed twice, removed duplicate
    }
    # Fill missing features with 0, ensuring all expected features are present
    for fname in feature_names: # feature_names should be loaded globally
        if fname not in features:
            features[fname] = 0.0
            
    return pd.DataFrame([features])[feature_names] # Ensure column order matches model training

def get_player_features_from_dataset(player_name):
    df = pd.read_csv(DATA_PATH, thousands=',', quotechar='"')
    # Normalize player names for robust matching
    df['player_name_norm'] = df['player_name'].astype(str).str.strip().str.lower()
    player_name_norm = player_name.strip().lower()
    # Feature engineering (must match your training pipeline)
    df['position'] = df['position'].str.upper().str.strip()
    valid_positions = ['DF', 'MF', 'FW']
    df['position'] = df['position'].apply(lambda x: x if x in valid_positions else 'FW')
    df['minutes'] = pd.to_numeric(df['minutes'], errors='coerce')
    df['goals'] = pd.to_numeric(df['goals'], errors='coerce')
    df['assists'] = pd.to_numeric(df['assists'], errors='coerce')
    df['mp'] = pd.to_numeric(df['mp'], errors='coerce')
    df['minutes_adj'] = df['minutes'].replace(0, 1)
    df['goals_per_90'] = (df['goals'] * 90) / df['minutes_adj']
    df['assists_per_90'] = (df['assists'] * 90) / df['minutes_adj']
    # One-hot for position
    for pos in ['DF', 'MF', 'FW']:
        df[f'pos_{pos}'] = (df['position'] == pos).astype(int)
    # Team encoding (neutral for API)
    df['team_encoded'] = 0.5
    # Season start
    df['season_start'] = pd.to_numeric(df['season'].str.split('-').str[0], errors='coerce').fillna(-1).astype(int)
    # Position score
    max_minutes = df['minutes'].max() or 1
    df['position_score'] = (
        0.7 * df['goals_per_90'] + 0.3 * df['assists_per_90']
    ) * df['pos_FW'] + (
        0.4 * df['goals_per_90'] + 0.6 * df['assists_per_90']
    ) * df['pos_MF'] + (
        0.2 * df['goals_per_90'] + 0.3 * df['assists_per_90'] + 0.5 * (df['minutes'] / max_minutes)
    ) * df['pos_DF']
    # Weighted recent features
    player_df = df[df['player_name_norm'] == player_name_norm].sort_values('season_start')
    if player_df.empty:
        return None
    last_3 = player_df.iloc[-3:] if len(player_df) >= 3 else player_df
    weights = np.arange(1, len(last_3)+1)
    def safe_avg(series): return np.average(series, weights=weights[:len(series)]) if len(series) else 0
    last_season = player_df.iloc[-1]
    matches_adj = max(last_season['mp'], 1)
    minutes_adj = max(last_season['minutes'], 1)
    rolling_3season_mins = player_df['minutes'].iloc[-3:].mean() if len(player_df) >= 3 else player_df['minutes'].mean()
    rolling_3season_mins_pct = (player_df['minutes'] / (player_df['mp'] * 90)).replace(0, 1).iloc[-3:].mean() if len(player_df) >= 3 else (player_df['minutes'] / (player_df['mp'] * 90)).replace(0, 1).mean()
    features = {
        'age': last_season['age'],
        'pos_DF': last_season['pos_DF'],
        'pos_MF': last_season['pos_MF'],
        'pos_FW': last_season['pos_FW'],
        'team_encoded': 0.5,
        'season_start': last_season['season_start'] + 1,  # Predict for next season
        'goals_per_90': last_season['goals_per_90'],
        'assists_per_90': last_season['assists_per_90'],
        'position_score': last_season['position_score'],
        'goals_per_90_weighted_recent': safe_avg(last_3['goals_per_90']),
        'assists_per_90_weighted_recent': safe_avg(last_3['assists_per_90']),
        'position_score_weighted_recent': safe_avg(last_3['position_score']),
        'minutes_weighted_recent': safe_avg(last_3['minutes']),
        'mins_per_appearance': minutes_adj / matches_adj,
        'availability': matches_adj / player_df['mp'].max() if player_df['mp'].max() > 0 else 1,
        'seasons_since_debut': len(player_df),
        'recent_form': player_df['position_score'].iloc[-3:].mean() if len(player_df) >= 3 else player_df['position_score'].mean(),
        'team_strength': 0.5,
        'injury_prone': int((minutes_adj / (matches_adj * 90)) < 0.6) if matches_adj > 0 else 0,
        'mins_pct_possible': minutes_adj / (matches_adj * 90) if matches_adj > 0 else 1,
        'rolling_3season_mins': rolling_3season_mins,
        'rolling_3season_mins_pct': rolling_3season_mins_pct,
        'minutes_weighted_recent': safe_avg(last_3['minutes'])
    }
    for fname in feature_names:
        if fname not in features:
            features[fname] = 0.0
    return pd.DataFrame([features])[feature_names]

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
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                # Fallback if "Bearer " prefix is missing
                token = auth_header 
        
        if not token:
            print("Token is missing")
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            print(f"Received token (first 10 chars): {token[:10]}...")
            # Add leeway to account for minor clock differences
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"], leeway=timedelta(seconds=30))
            # Assuming User model is defined and accessible for current_user lookup
            current_user_obj = User.query.filter_by(id=data['public_id']).first()
            if not current_user_obj:
                 return jsonify({'message': 'User for token not found!'}), 401
        except jwt.ExpiredSignatureError:
            print(f"Token verification error: Signature has expired")
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError as e:
            print(f"Token verification error: {str(e)}")
            return jsonify({'message': 'Token is invalid!'}), 401
        except Exception as e:
            print(f"Unexpected error during token verification: {str(e)}")
            print(traceback.format_exc())
            return jsonify({'message': 'Token verification failed due to an unexpected error!'}), 401
            
        return f(current_user_obj, *args, **kwargs) # Pass the fetched user object
    return decorated


# This function contains the core logic for the analysis.
def _execute_tactical_analysis(current_app, match_id):
    with current_app.app_context():
        match = Match.query.get(match_id)
        if not match:
            current_app.logger.error(f"Tactical analysis: Match {match_id} not found.")
            return

        current_app.logger.info(f"Starting tactical analysis for Match ID: {match_id} in a background thread.")
        match.tactical_analysis_status = TacticalAnalysisStatus.PROCESSING
        db.session.commit()

        video_filename_only = match.video_filename
        video_input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], video_filename_only)

        if not os.path.exists(video_input_path):
            match.tactical_analysis_status = TacticalAnalysisStatus.FAILED
            match.error_message = f"Video file {video_filename_only} not found in uploads for tactical analysis."
            db.session.commit()
            current_app.logger.error(match.error_message)
            return

        # This is the base output directory that will be passed to the submodule.
        # demoV2.py will save its outputs directly into this directory or its subdirectories.
        match_specific_tactics_output_dir = os.path.join(TACTICS_OUTPUT_FOLDER, str(match_id))
        os.makedirs(match_specific_tactics_output_dir, exist_ok=True)
        
        # The get_tactical_analysis_details route expects heatmaps in TACTICS_OUTPUT_FOLDER/<match_id>/heatmaps/
        # demoV2.py saves them in TACTICS_OUTPUT_FOLDER/<match_id>/final_heatmaps/
        # We will check demoV2's output path and then potentially list from there or adjust.
        # For now, let's define where app.py expects them for serving.
        heatmaps_serving_dir_name = 'heatmaps' # This is the folder name the frontend/API expects
        heatmaps_serving_path = os.path.join(match_specific_tactics_output_dir, heatmaps_serving_dir_name)
        # We don't necessarily need to create heatmaps_serving_path if demoV2 creates final_heatmaps.
        # The get_tactical_analysis_details will need to be aware of 'final_heatmaps'.

        try:
            module_name = "demoV2_analysis_module"
            base_dir = os.path.dirname(os.path.abspath(__file__))
            path_to_demoV2 = os.path.join(base_dir, 'ml', 'tactics', 'football-analysis', 'demoV2.py')

            if not os.path.exists(path_to_demoV2):
                error_msg = f"Analysis script not found at {path_to_demoV2}"
                current_app.logger.error(error_msg)
                match.tactical_analysis_status = TacticalAnalysisStatus.FAILED
                match.error_message = error_msg
                db.session.commit()
                return

            spec = importlib.util.spec_from_file_location(module_name, path_to_demoV2)
            if spec is None or spec.loader is None:
                error_msg = f"Could not load spec for analysis script at {path_to_demoV2}"
                current_app.logger.error(error_msg)
                match.tactical_analysis_status = TacticalAnalysisStatus.FAILED
                match.error_message = error_msg
                db.session.commit()
                return
            
            analysis_module = importlib.util.module_from_spec(spec)
            
            # Add the directory of demoV2.py to sys.path temporarily so its internal imports (like from src.*) work
            submodule_dir = os.path.dirname(path_to_demoV2)
            if submodule_dir not in sys.path:
                sys.path.insert(0, submodule_dir)

            spec.loader.exec_module(analysis_module)

            # Call the run_dynamic_analysis function from the loaded module
            # It expects: video_path, output_dir (this will be results/match_id/)
            # We let demoV2.py use its default sample_rate.
            current_app.logger.info(f"Calling run_dynamic_analysis with video: {video_input_path} and output_dir: {match_specific_tactics_output_dir}")
            analysis_module.run_dynamic_analysis(video_input_path, match_specific_tactics_output_dir)
            current_app.logger.info(f"run_dynamic_analysis for match {match_id} completed.")

            # Clean up sys.path if we added the submodule_dir
            if submodule_dir == sys.path[0]: # Check if it's the one we added
                sys.path.pop(0)


            # --- Check for output files based on demoV2.py behavior ---

            # 1. Check for overlay video
            # demoV2.py saves it as "analysis_output.avi" directly in match_specific_tactics_output_dir
            original_avi_filename = "analysis_output.avi"
            path_to_original_avi = os.path.join(match_specific_tactics_output_dir, original_avi_filename)
            
            final_video_relative_path = None # This will store the path to the web-friendly video

            if os.path.exists(path_to_original_avi):
                current_app.logger.info(f"Original AVI analysis output found: {path_to_original_avi}")
                
                converted_mp4_filename = "analysis_output.mp4" # Target MP4 filename
                path_to_converted_mp4 = os.path.join(match_specific_tactics_output_dir, converted_mp4_filename)
                
                try:
                    # ffmpeg command to convert AVI to MP4 (H.264 video, AAC audio)
                    command = [
                        'ffmpeg', 
                        '-i', path_to_original_avi,
                        '-c:v', 'libx264',   # H.264 video codec
                        '-preset', 'medium', # Encoding speed/quality trade-off
                        '-crf', '23',        # Constant Rate Factor (quality, lower is better, 18-28 is typical)
                        '-c:a', 'aac',       # AAC audio codec
                        '-b:a', '128k',      # Audio bitrate
                        '-strict', 'experimental', # Needed for some AAC configurations
                        '-y',                # Overwrite output file if it exists
                        path_to_converted_mp4
                    ]
                    current_app.logger.info(f"Attempting to convert AVI to MP4: {' '.join(command)}")
                    
                    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = process.communicate()

                    if process.returncode == 0 and os.path.exists(path_to_converted_mp4):
                        current_app.logger.info(f"Successfully converted '{original_avi_filename}' to '{converted_mp4_filename}'")
                        final_video_relative_path = f"{match_id}/{converted_mp4_filename}"
                        # Optionally, remove the original AVI to save space:
                        # try:
                        #     os.remove(path_to_original_avi)
                        #     current_app.logger.info(f"Removed original AVI file: {path_to_original_avi}")
                        # except OSError as e_remove:
                        #     current_app.logger.error(f"Error removing original AVI file {path_to_original_avi}: {e_remove}")
                    else:
                        error_output = stderr.decode(errors='ignore')
                        current_app.logger.error(f"ffmpeg conversion failed for {path_to_original_avi}. Return code: {process.returncode}")
                        current_app.logger.error(f"ffmpeg stdout: {stdout.decode(errors='ignore')}")
                        current_app.logger.error(f"ffmpeg stderr: {error_output}")
                        # If conversion fails, we don't have a web-playable MP4.
                        # Consider what to do: log error, maybe try to serve AVI (though it won't play).
                        # For now, no video URL will be set if conversion fails.
                        final_video_relative_path = None 
                        match.error_message = (match.error_message or "") + f"; Failed to convert overlay video to MP4. ffmpeg error: {error_output[:250]}"


                except FileNotFoundError:
                    current_app.logger.error("ffmpeg command not found. Ensure ffmpeg is installed and in system PATH.")
                    match.error_message = (match.error_message or "") + "; ffmpeg not found for video conversion."
                    final_video_relative_path = None
                except Exception as e_conv:
                    current_app.logger.error(f"Error during AVI to MP4 conversion: {str(e_conv)}")
                    current_app.logger.error(traceback.format_exc())
                    match.error_message = (match.error_message or "") + f"; Error during video conversion: {str(e_conv)}"
                    final_video_relative_path = None
            else:
                current_app.logger.warn(f"Overlay video file '{original_avi_filename}' not found in {match_specific_tactics_output_dir} after analysis for match {match_id}.")
                final_video_relative_path = None # Ensure it's None if AVI isn't found
            
            match.tactical_overlay_video_filename = final_video_relative_path

            # 2. Check for heatmaps
            # demoV2.py saves final heatmaps in a subfolder "final_heatmaps"
            heatmaps_output_subfolder_by_demoV2 = "final_heatmaps"
            actual_heatmaps_path = os.path.join(match_specific_tactics_output_dir, heatmaps_output_subfolder_by_demoV2)
            
            heatmaps_were_generated = False
            if os.path.exists(actual_heatmaps_path) and os.path.isdir(actual_heatmaps_path):
                if any(f.lower().endswith(('.png', '.jpg', '.jpeg')) for f in os.listdir(actual_heatmaps_path)):
                    heatmaps_were_generated = True
            
            match.heatmaps_generated = heatmaps_were_generated
            if heatmaps_were_generated:
                 current_app.logger.info(f"Heatmaps found in {actual_heatmaps_path} for match {match_id}.")
            else:
                current_app.logger.warn(f"No heatmap images found in {actual_heatmaps_path} for match {match_id}.")

            match.tactical_analysis_status = TacticalAnalysisStatus.COMPLETED
            match.error_message = None # Clear previous errors
            db.session.commit()
            
            current_app.logger.info(f"Tactical analysis processing and file check completed for match {match_id}.")

        except AttributeError as e:
            error_msg = f"Main analysis function (e.g., 'run_dynamic_analysis') not found in analysis script or attribute error: {str(e)}"
            current_app.logger.error(error_msg)
            current_app.logger.error(traceback.format_exc())
            match.tactical_analysis_status = TacticalAnalysisStatus.FAILED
            match.error_message = error_msg
            db.session.commit()
            # Clean up sys.path if it was modified and an error occurred
            if 'submodule_dir' in locals() and submodule_dir == sys.path[0]:
                sys.path.pop(0)
        except Exception as e:
            error_detail = str(e)
            match.tactical_analysis_status = TacticalAnalysisStatus.FAILED
            match.error_message = error_detail
            db.session.commit()
            current_app.logger.error(f"Tactical analysis failed for match {match_id} during submodule execution: {error_detail}")
            current_app.logger.error(traceback.format_exc())
            # Clean up sys.path if it was modified and an error occurred
            if 'submodule_dir' in locals() and submodule_dir == sys.path[0]:
                sys.path.pop(0)


# New route to serve files from TACTICS_OUTPUT_FOLDER
@app.route('/tactics_output/<path:filename>')
def serve_tactics_output_file(filename):
    """Serve files from the TACTICS_OUTPUT_FOLDER directory"""
    # Note: filename here could be "match_id/video.mp4" or "match_id/heatmaps/heatmap.png"
    app.logger.info(f"Attempting to serve tactics output file: '{filename}' from directory: '{TACTICS_OUTPUT_FOLDER}'")
    return send_from_directory(TACTICS_OUTPUT_FOLDER, filename)


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
        if user.role == 'Player':
            user_profile = PlayerProfile.query.filter_by(user_id=user.id).first()
            return jsonify({
                'id': user.id,
                'agency_id': user_profile.agency,
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
                'gk_reflexes': user_profile.gk_reflexes
            }), 200
        elif user.role == 'Coach':
            Coach = CoachProfile.query.filter_by(user_id=user.id).first()
            return jsonify({
                'id': user.id,
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
            Agent = AgentProfile.query.filter_by(user_id=user.id).first()
            return jsonify({
                'id': user.id,
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
            Staff = StaffProfile.query.filter_by(user_id=user.id).first()
            return jsonify({
                'id': user.id,
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
            Scout = ScoutProfile.query.filter_by(user_id=user.id).first()
            return jsonify({
                'id': user.id,
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
            Manager = ManagerProfile.query.filter_by(user_id=user.id).first()
            return jsonify({
                'id': user.id,
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
        clubs = ClubProfile.query.all()
        club_list = [{'id': club.id, 'name': club.country} for club in clubs]  # Replace 'country' with the actual club name field
        return jsonify(club_list), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch clubs', 'details': str(e)}), 500
    
@app.route('/register', methods=['POST'])
def register():
    try:
        # Required fields from form
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        name = request.form.get('name', '').strip()
        role = request.form.get('role', '').strip()

        allowed_roles = ['Player', 'Coach', 'Manager', 'Agent', 'Scout', 'Staff']
        if role not in allowed_roles:
            return jsonify({'message': 'Invalid role selected'}), 400

        # Ethereum address creation
        account = w3.eth.account.create()
        eth_address = account.address
        private_key = account._private_key.hex()  # hex for DB/json compatibility

        if not Web3.is_address(eth_address):
            return jsonify({"message": "Invalid Ethereum address"}), 400

        # Uniqueness checks
        if User.query.filter((User.username == username) | (User.email == email)).first():
            return jsonify({'message': 'Username or email already exists'}), 409

        # Profile image
        profile_image = request.files.get('profile_image')
        profile_image_path = None
        if profile_image and allowed_file(profile_image.filename):
            filename = secure_filename(profile_image.filename)
            profile_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_image.save(profile_image_path)

        # Password hash
        hashed_password = generate_password_hash(password, method='scrypt')

        # User creation
        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
            name=name,
            profile_image=profile_image_path,
            eth_address=eth_address,
            private_key=private_key,
            role=role
        )
        db.session.add(new_user)
        db.session.commit()

        # Role-based profile creation
        if role == 'Player':
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
                score=0.0,
                performance_metrics=0.0,
                media_sentiment=0.0,
                aggression=0,
                reactions=0,
                long_pass=0,
                stamina=0,
                strength=0,
                sprint_speed=0,
                agility=0,
                jumping=0,
                heading=0,
                free_kick_accuracy=0,
                volleys=0,
                gk_positioning=0,
                gk_diving=0,
                gk_handling=0,
                gk_kicking=0,
                gk_reflexes=0
            )
            db.session.add(player_profile)

        elif role == 'Coach':
            coach_profile = CoachProfile(
                user_id=new_user.id,
                name=new_user.name,
                photo=new_user.profile_image,
                nationality='',
                date_of_appointment=None,
                date_of_end_contract=None,
                years_of_experience=0,
                qualification='',
                availability=True
            )
            db.session.add(coach_profile)

        elif role == 'Manager':
            manager_profile = ManagerProfile(
                user_id=new_user.id,
                name=new_user.name,
                nationality='',
                date_of_appointment=None,
                date_of_end_contract=None,
                years_of_experience=0,
                qualification='',
                availability=True,
                total_matches=0,
                wins=0,
                draws=0,
                losses=0,
                ppg=0.0
            )
            db.session.add(manager_profile)

        elif role == 'Agent':
            agent_profile = AgentProfile(
                user_id=new_user.id,
                name=new_user.name,
                nationality='',
                date_of_appointment=None,
                date_of_end_contract=None,
                years_of_experience=0,
                qualification='',
                availability=True
            )
            db.session.add(agent_profile)

        elif role == 'Scout':
            scout_profile = ScoutProfile(
                user_id=new_user.id,
                name=new_user.name,
                nationality='',
                date_of_appointment=None,
                date_of_end_contract=None,
                years_of_experience=0,
                qualification='',
                availability=True
            )
            db.session.add(scout_profile)

        elif role == 'Staff':
            staff_profile = StaffProfile(
                user_id=new_user.id,
                name=new_user.name,
                nationality='',
                date_of_appointment=None,
                date_of_end_contract=None,
                years_of_experience=0,
                qualification='',
                availability=True
            )
            db.session.add(staff_profile)

        # Final commit for profile
        db.session.commit()

        # Send welcome email
        msg = MailMessage("Welcome to MetaScout!",
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
        return jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500

    
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
@token_required
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
            'exp': datetime.utcnow() + timedelta(days=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token}), 200
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
    df['Nationality'] = df['Nationality'].map(nationality_freq).fillna(-1)
    df['Team_Name'] = df['Team_Name'].map(teamname_freq).fillna(-1)
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

    # Ensure a different random value each time by using a dynamic seed
    random.seed(time.time())  # Use the current time to seed the random number generator
    df_scaled['Injury_Grouped_Encoded'] = random.randint(0, 9)  # Random value for Injury_Grouped_Encoded

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


    
@app.route('/update_profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.json  # Use request.json to handle JSON data

    # Debug: Log incoming data
    print(f"Request data: {data}")

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

    # Handle profile image upload (if applicable)
    if 'profile_image' in request.files:
        profile_image = request.files['profile_image']
        if profile_image and allowed_file(profile_image.filename):
            filename = secure_filename(profile_image.filename)
            profile_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_image.save(profile_image_path)
            current_user.profile_image = profile_image_path

    try:
        # Fetch the user's profile
        if current_user.role == 'Player':
            user_profile = PlayerProfile.query.filter_by(user_id=current_user.id).first()

            if not user_profile:
                return jsonify({'error': 'Player profile not found'}), 404

            # Update PlayerProfile fields
            if 'season' in data:
                user_profile.season = data['season']
            if 'age' in data:
                user_profile.age = data['age']
            if 'nationality' in data:
                user_profile.nationality = data['nationality']
            if 'position' in data:
                user_profile.position = data['position']
            if 'matches' in data:
                user_profile.matches = data['matches']
            if 'minutes' in data:
                user_profile.minutes = data['minutes']
            if 'goals' in data:
                user_profile.goals = data['goals']
            if 'assists' in data:
                user_profile.assists = data['assists']
            if 'club' in data:
                user_profile.club = data['club']
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
            user_profile = CoachProfile.query.filter_by(user_id=current_user.id).first()

            if not user_profile:
                return jsonify({'error': 'Coach profile not found'}), 404

            # Update Coach_Profile fields
            if 'nationality' in data:
                user_profile.nationality = data['nationality']
            if 'date_of_appointment' in data:
                user_profile.date_of_appointment = data['date_of_appointment']
            if 'date_of_end_contract' in data:
                user_profile.date_of_end_contract = data['date_of_end_contract']
            if 'years_of_experience' in data:
                user_profile.years_of_experience = data['years_of_experience']
            if 'qualification' in data:
                user_profile.qualification = data['qualification']
            if 'availability' in data:
                user_profile.availability = data['availability']

        elif current_user.role == 'Agent':
            user_profile = AgentProfile.query.filter_by(user_id=current_user.id).first()

            if not user_profile:
                return jsonify({'error': 'Agent profile not found'}), 404

            # Update Agent_Profile fields
            if 'nationality' in data:
                user_profile.nationality = data['nationality']
            if 'date_of_appointment' in data:
                user_profile.date_of_appointment = data['date_of_appointment']
            if 'date_of_end_contract' in data:
                user_profile.date_of_end_contract = data['date_of_end_contract']
            if 'years_of_experience' in data:
                user_profile.years_of_experience = data['years_of_experience']
            if 'qualification' in data:
                user_profile.qualification = data['qualification']
            if 'availability' in data:
                user_profile.availability = data['availability']

        elif current_user.role == 'Staff':
            user_profile = StaffProfile.query.filter_by(user_id=current_user.id).first()

            if not user_profile:
                return jsonify({'error': 'Staff profile not found'}), 404

            # Update Staff_Profile fields
            if 'nationality' in data:
                user_profile.nationality = data['nationality']
            if 'date_of_appointment' in data:
                user_profile.date_of_appointment = data['date_of_appointment']
            if 'date_of_end_contract' in data:
                user_profile.date_of_end_contract = data['date_of_end_contract']
            if 'years_of_experience' in data:
                user_profile.years_of_experience = data['years_of_experience']
            if 'qualification' in data:
                user_profile.qualification = data['qualification']
            if 'availability' in data:
                user_profile.availability = data['availability']

        elif current_user.role == 'Scout':
            user_profile = ScoutProfile.query.filter_by(user_id=current_user.id).first()

            if not user_profile:
                return jsonify({'error': 'Scout profile not found'}), 404

            # Update Scout_Profile fields
            if 'nationality' in data:
                user_profile.nationality = data['nationality']
            if 'date_of_appointment' in data:
                user_profile.date_of_appointment = data['date_of_appointment']
            if 'date_of_end_contract' in data:
                user_profile.date_of_end_contract = data['date_of_end_contract']
            if 'years_of_experience' in data:
                user_profile.years_of_experience = data['years_of_experience']
            if 'qualification' in data:
                user_profile.qualification = data['qualification']
            if 'availability' in data:
                user_profile.availability = data['availability']

        elif current_user.role == 'Manager':
            user_profile = ManagerProfile.query.filter_by(user_id=current_user.id).first()

            if not user_profile:
                return jsonify({'error': 'Manager profile not found'}), 404

            # Update Manager_Profile fields
            if 'nationality' in data:
                user_profile.nationality = data['nationality']
            if 'date_of_appointment' in data:
                user_profile.date_of_appointment = data['date_of_appointment']
            if 'date_of_end_contract' in data:
                user_profile.date_of_end_contract = data['date_of_end_contract']
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
    model.load_state_dict(torch.load('marketValuemodel/market_value_predictor.pth'))

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
        prediction_list = prediction.numpy().tolist()
        return jsonify({'prediction': prediction_list})
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
    elif current_user.role == "Player":
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



@app.route('/api/transcribe', methods=['POST'])
@token_required
def transcribe_video(current_user):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Save the uploaded video temporarily
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(video_path)
    
    try:
        # Extract audio
        audio_path = extract_audio(video_path)
        
        # Transcribe audio
        result = transcriber.transcribe_audio(audio_path)
        
        # Generate SRT file
        srt_path = os.path.join(PROCESSED_FOLDER, f"{os.path.splitext(file.filename)[0]}.srt")
        transcriber.generate_srt(result, srt_path)
        
        return jsonify({
            'transcript': result['text'],
            'srt_url': f"/processed_videos/{os.path.basename(srt_path)}"
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


@app.route('/api/transcribe-from-path', methods=['POST'])
@token_required
def transcribe_from_path(current_user):
    data = request.json
    if not data or 'video_path' not in data:
        return jsonify({'error': 'No video path provided'}), 400
    
    video_path = data['video_path']
    if not video_path.startswith('uploads/'):
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_path)
    else:
        video_path = os.path.join(os.getcwd(), video_path)
    
    if not os.path.exists(video_path):
        return jsonify({'error': f'Video file not found: {video_path}'}), 404

    try:
        # Extract audio
        audio_path = extract_audio(video_path)
        
        # Transcribe audio
        result = transcriber.transcribe_audio(audio_path)
        
        # Generate SRT file
        base_filename = os.path.splitext(os.path.basename(video_path))[0]
        srt_path = os.path.join(PROCESSED_FOLDER, f"{base_filename}.srt")
        transcriber.generate_srt(result, srt_path)
        
        # Generate captioned video
        captioned_video_path = os.path.join(PROCESSED_FOLDER, f"{base_filename}_captioned.mp4")
        overlay_subtitles(video_path, srt_path, captioned_video_path)
        
        return jsonify({
            'transcript': result['text'],
            'srt_url': f"/processed_videos/{base_filename}.srt",
            'captioned_video_url': f"/processed_videos/{base_filename}_captioned.mp4"
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        


@app.route('/api/tts', methods=['POST'])
@token_required
def text_to_speech(current_user):
    if not request.json or 'text' not in request.json:
        return jsonify({'error': 'No text provided'}), 400
    
    text = request.json['text']
    voice_id = request.json.get('voice_id', '21m00Tcm4TlvDq8ikWAM')  # Default voice
    
    try:
        # Generate speech using TTS
        audio_path = tts_engine.generate_speech(text, voice_id)
        
        # Create a unique filename
        unique_filename = f"tts_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
        target_path = os.path.join(PROCESSED_FOLDER, unique_filename)
        
        # Copy the audio to accessible location
        import shutil
        shutil.copy(audio_path, target_path)
        
        return jsonify({
            'audio_url': f"/processed_videos/{unique_filename}"
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/enhance-captions', methods=['POST'])
@token_required
def enhance_captions(current_user):
    if 'srt_file' not in request.files:
        return jsonify({'error': 'No SRT file provided'}), 400
    
    srt_file = request.files['srt_file']
    if srt_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        # Save the uploaded SRT file
        srt_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(srt_file.filename))
        srt_file.save(srt_path)
        
        # Enhance captions
        enhanced_path = caption_enhancer.enhance_srt(srt_path)
        
        # Make the file accessible
        unique_filename = f"enhanced_{os.path.basename(enhanced_path)}"
        target_path = os.path.join(PROCESSED_FOLDER, unique_filename)
        
        import shutil
        shutil.copy(enhanced_path, target_path)
        
        return jsonify({
            'enhanced_srt_url': f"/processed_videos/{unique_filename}"
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/overlay-subtitles', methods=['POST'])
@token_required
def add_subtitles_to_video(current_user):
    if 'video' not in request.files or 'srt' not in request.files:
        return jsonify({'error': 'Both video and SRT files are required'}), 400
    
    video_file = request.files['video']
    srt_file = request.files['srt']
    
    if video_file.filename == '' or srt_file.filename == '':
        return jsonify({'error': 'No selected files'}), 400
    
    try:
        # Save the uploaded files
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(video_file.filename))
        srt_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(srt_file.filename))
        
        video_file.save(video_path)
        srt_file.save(srt_path)
        
        # Get style parameters
        font_size = request.form.get('font_size', 24)
        position = request.form.get('position', 'bottom')
        color = request.form.get('color', 'white')
        
        # Overlay subtitles
        from ml.video.overlay import overlay_subtitles_with_style
        output_path = overlay_subtitles_with_style(video_path, srt_path, 
                                                 font_size=int(font_size), 
                                                 position=position, 
                                                 color=color)
        
        # Make the file accessible
        filename = os.path.basename(output_path)
        target_path = os.path.join(PROCESSED_FOLDER, filename)
        
        import shutil
        if output_path != target_path:
            shutil.copy(output_path, target_path)
        
        return jsonify({
            'video_url': f"/processed_videos/{filename}"
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500   
    

# Add route to serve processed files
@app.route('/processed_videos/<path:filename>')
def serve_processed_file(filename):
    """Serve files from the processed_videos directory"""
    return send_from_directory(PROCESSED_FOLDER, filename)


# Add at the end of app.py
@app.route('/api/test-transcribe', methods=['POST'])
def test_transcribe():
    """Test endpoint without authentication for debugging"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Save the uploaded video temporarily
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(video_path)
    
    try:
        # Extract audio
        audio_path = extract_audio(video_path)
        
        # Transcribe audio
        result = transcriber.transcribe_audio(audio_path)
        
        # Generate SRT file
        srt_path = os.path.join(PROCESSED_FOLDER, f"{os.path.splitext(file.filename)[0]}.srt")
        transcriber.generate_srt(result, srt_path)
        
        return jsonify({
            'transcript': result['text'],
            'srt_url': f"/processed_videos/{os.path.basename(srt_path)}"
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/public-transcribe', methods=['POST', 'OPTIONS'])
def public_transcribe():
    """Public endpoint for transcription without auth"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.json
        if not data or 'video_path' not in data:
            return jsonify({'error': 'No video path provided'}), 400
        
        video_filename = data['video_path']
        print(f"Looking for video: {video_filename}")
        
        # Try multiple possible paths for the file
        possible_paths = [
            # Direct path as provided
            os.path.join(app.config['UPLOAD_FOLDER'], video_filename),
            
            # Try with absolute path to uploads folder
            os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], video_filename),
            
            # Try with parent directory
            os.path.join(os.path.dirname(os.getcwd()), app.config['UPLOAD_FOLDER'], video_filename)
        ]
        
        # Find the first path that exists
        video_path = None
        for path in possible_paths:
            print(f"Checking path: {path}")
            if os.path.exists(path):
                video_path = path
                print(f"Found file at: {video_path}")
                break
        
        if not video_path:
            # File not found - generate demo SRT file
            print("Video file not found in any location - using debug captions")
            base_filename = os.path.splitext(video_filename)[0]
            
            # Make sure the processed folder exists
            os.makedirs(PROCESSED_FOLDER, exist_ok=True)
            
            # Create a dummy SRT file for testing
            srt_path = os.path.join(PROCESSED_FOLDER, f"{base_filename}.srt")
            with open(srt_path, 'w') as f:
                f.write("1\n00:00:01,000 --> 00:00:05,000\nThis is a test caption\n\n")
                f.write("2\n00:00:06,000 --> 00:00:10,000\nYour video is now captioned\n\n")
                f.write("3\n00:00:11,000 --> 00:00:15,000\nThe analysis feature works!\n\n")
            
            return jsonify({
                'transcript': "This is a test caption. Your video is now captioned. The analysis feature works!",
                'srt_url': f"/processed_videos/{base_filename}.srt"
            }), 200
        
        # Create directories if they don't exist
        os.makedirs(PROCESSED_FOLDER, exist_ok=True)
        
        # ACTUAL TRANSCRIPTION PROCESS
        try:
            # Extract base filename here to avoid scoping issues
            base_filename = os.path.splitext(os.path.basename(video_path))[0]
            print(f"Base filename: {base_filename}")
            
            # 1. Extract audio from video
            print(f"Starting audio extraction from {video_path}")
            audio_path = extract_audio(video_path)
            print(f"Audio extracted to {audio_path}")
            
            # 2. Use Whisper to transcribe the audio
            print("Starting transcription with Whisper...")
            result = transcriber.transcribe_audio(audio_path)
            print(f"Transcription complete, length: {len(result['text'])} chars")
            
            # 3. Generate SRT file from transcription
            srt_path = os.path.join(PROCESSED_FOLDER, f"{base_filename}.srt")
            print(f"Generating SRT file at {srt_path}")
            transcriber.generate_srt(result, srt_path)
            print(f"SRT file generated successfully")
            
            # 4. Return the transcript and SRT URL
            return jsonify({
                'transcript': result['text'],
                'srt_url': f"/processed_videos/{base_filename}.srt"
            }), 200
            
        except Exception as e:
            # Log the error and fall back to debug captions
            import traceback
            print(f"ERROR DURING TRANSCRIPTION: {str(e)}")
            print(traceback.format_exc())
            
            # Create a fallback SRT on error
            base_filename = os.path.splitext(os.path.basename(video_path))[0]
            srt_path = os.path.join(PROCESSED_FOLDER, f"{base_filename}.srt")
            with open(srt_path, 'w') as f:
                f.write("1\n00:00:01,000 --> 00:00:05,000\nTranscription encountered an error\n\n")
                f.write("2\n00:00:06,000 --> 00:00:10,000\nPlease check the server logs\n\n")
                f.write("3\n00:00:11,000 --> 00:00:15,000\nUsing fallback captions\n\n")
            
            return jsonify({
                'transcript': f"Transcription error: {str(e)}. Using fallback captions.",
                'srt_url': f"/processed_videos/{base_filename}.srt"
            }), 200
    
    except Exception as e:
        import traceback
        print(f"Error in public_transcribe: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# Add this helper function for SRT timestamp formatting
def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format: HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    seconds %= 3600
    minutes = int(seconds // 60)
    seconds %= 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"
    

@app.route('/api/public-tts', methods=['POST', 'OPTIONS'])
def public_text_to_speech():
    """Public TTS endpoint without authentication"""
    if request.method == 'OPTIONS':
        return '', 200
        
    if not request.json or 'text' not in request.json:
        return jsonify({'error': 'No text provided'}), 400
    
    text = request.json['text']
    voice_id = request.json.get('voice_id', '21m00Tcm4TlvDq8ikWAM')  # Default voice
    
    try:
        # Generate speech using TTS
        audio_path = tts_engine.generate_speech(text, voice_id)
        
        # Create a unique filename
        unique_filename = f"tts_summary_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
        target_path = os.path.join(PROCESSED_FOLDER, unique_filename)
        
        # Copy the audio to accessible location
        shutil.copy(audio_path, target_path)
        
        return jsonify({
            'audio_url': f"/processed_videos/{unique_filename}"
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500 
    

@app.route('/api/file-debug', methods=['GET'])
def file_debug():
    """Endpoint to debug file paths"""
    uploads_dir = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])
    files = os.listdir(uploads_dir)
    return jsonify({
        'upload_folder': uploads_dir,
        'current_directory': os.getcwd(),
        'files_in_upload_folder': files
    })

@app.route('/api/check-caption-exists', methods=['POST'])
def check_caption_exists():
    """Check if an SRT caption file exists"""
    try:
        data = request.json
        if not data or 'filename' not in data:
            return jsonify({'error': 'No filename provided'}), 400
        
        base_filename = data['filename']
        srt_path = os.path.join(PROCESSED_FOLDER, f"{base_filename}.srt")
        
        print(f"Checking if caption exists: {srt_path}")
        print(f"File exists: {os.path.exists(srt_path)}")
        
        return jsonify({
            'exists': os.path.exists(srt_path),
            'url': f"/processed_videos/{base_filename}.srt" if os.path.exists(srt_path) else None
        })
    except Exception as e:
        print(f"Error checking caption existence: {str(e)}")
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/get-caption', methods=['GET'])
def get_caption():
    """Get caption text for a specific post"""
    try:
        post_id = request.args.get('postId')
        if not post_id:
            return jsonify({'error': 'No post ID provided'}), 400
            
        # Get the video filename from post
        post = Post.query.get(post_id)
        if not post or not post.video_url:
            return jsonify({'error': 'Post not found or no video'}), 404
            
        video_filename = os.path.basename(post.video_url)
        base_filename = os.path.splitext(video_filename)[0]
        
        # List all SRT files that might match
        srt_files = [f for f in os.listdir(PROCESSED_FOLDER) if f.endswith('.srt')]
        
        # Try to find a matching SRT file
        matching_file = None
        for srt_file in srt_files:
            if srt_file.startswith(base_filename) or base_filename in srt_file:
                matching_file = srt_file
                break
                
        if not matching_file:
            return jsonify({'error': 'No caption file found'}), 404
            
        # Read the SRT file
        srt_path = os.path.join(PROCESSED_FOLDER, matching_file)
        with open(srt_path, 'r', encoding='utf-8') as f:
            srt_text = f.read()
            
        return jsonify({
            'srt_text': srt_text,
            'srt_url': f"/processed_videos/{matching_file}"
        })
        
    except Exception as e:
        print(f"Error getting caption: {str(e)}")
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/analyze-transcript', methods=['POST'])
def analyze_transcript():
    """Analyze a transcript to generate summary and sentiment analysis without OpenAI"""
    try:
        data = request.json
        if not data or 'transcript' not in data:
            return jsonify({'error': 'No transcript provided'}), 400
            
        transcript = data['transcript']
        
        # Import necessary libraries
        import re
        import nltk
        from nltk.tokenize import sent_tokenize
        from nltk.corpus import stopwords
        from nltk.probability import FreqDist
        from ml.speech.caption import CaptionEnhancer
        
        # Download NLTK resources if not available
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
        
        # 1. Clean filler words using existing CaptionEnhancer
        enhancer = CaptionEnhancer()
        cleaned_transcript = enhancer.clean_transcript(transcript)
        
        # 2. Generate summary using extractive summarization (NLTK)
        # Tokenize the text into sentences
        sentences = sent_tokenize(cleaned_transcript)
        
        # Tokenize words and remove stopwords
        stop_words = set(stopwords.words('english'))
        words = [word.lower() for sentence in sentences for word in nltk.word_tokenize(sentence) 
                if word.isalnum() and word.lower() not in stop_words]
        
        # Find most frequent words
        freq_dist = FreqDist(words)
        most_freq = [word for word, freq in freq_dist.most_common(20)]
        
        # Score sentences based on word frequency and position
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = 0
            # Position score - first and last sentences are often important
            if i == 0 or i == len(sentences) - 1:
                score += 0.5
                
            # Word frequency score
            for word in nltk.word_tokenize(sentence.lower()):
                if word in most_freq:
                    score += 0.1
                    
            # Length score - favor medium length sentences
            words_count = len(nltk.word_tokenize(sentence))
            if 5 <= words_count <= 20:
                score += 0.5
                
            scored_sentences.append((sentence, score))
        
        # Sort sentences by score and select top ones for summary
        summary_sentences = sorted(scored_sentences, key=lambda x: x[1], reverse=True)[:5]
        # Sort back by original position for readability
        summary_sentences = sorted(summary_sentences, 
                                   key=lambda x: sentences.index(x[0]))
        
        # Join sentences into summary
        summary = ' '.join([sentence for sentence, score in summary_sentences])
        
        # 3. Find key moments with excitement detection (keep this part as is)
        key_moments = []
        
        # Simple excitement detection regex patterns
        excitement_patterns = [
            r'\b(goal|score|scores|scored|shot|shots|save|saves|saved)\b',
            r'\b(amazing|incredible|fantastic|brilliant|excellent|extraordinary)\b',
            r'\b(wow|unbelievable|spectacular|stunning|remarkable)\b',
            r'!{2,}',  # Multiple exclamation marks
        ]
        
        for i, sentence in enumerate(sentences):
            # Calculate excitement score
            excitement_score = 0
            for pattern in excitement_patterns:
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                excitement_score += len(matches) * 0.5
                
            # Add timing context if available
            timing_match = re.search(r'\b(\d{1,2}:\d{2}|\d{1,2}\'|\d{1,2} minutes?)\b', sentence)
            match_time = timing_match.group(1) if timing_match else None
            
            # If this is an exciting sentence
            if excitement_score >= 1.0:
                key_moments.append({
                    'text': sentence,
                    'excitement': min(excitement_score, 5),  # Cap at 5
                    'time': match_time
                })
        
        # Sort by excitement level
        key_moments.sort(key=lambda x: x['excitement'], reverse=True)
        
        # Take top 5 key moments
        key_moments = key_moments[:5]
        
        return jsonify({
            'summary': summary,
            'key_moments': key_moments
        })
        
    except Exception as e:
        print(f"Error analyzing transcript: {str(e)}")
        return jsonify({'error': str(e)}), 500
    

# Initialize the summarizer (lazy loading will occur on first use)
gemma_summarizer = GemmaSummarizerService(use_8bit=True)

@app.route('/api/summarize-transcript', methods=['POST', 'OPTIONS'])
def summarize_transcript():
    """Endpoint to generate a summary of a soccer match transcript"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.json
        print(f"Received data: {data}")
        
        if not data or 'video_id' not in data:
            return jsonify({'error': 'No video ID provided'}), 400
        
        video_id = data['video_id']
        print(f"Looking for SRT file with video_id: {video_id}")
        
        # Find the corresponding SRT file
        srt_filename = f"{video_id}.srt"
        srt_path = os.path.join(PROCESSED_FOLDER, srt_filename)
        print(f"Full SRT path: {srt_path}")
        
        if not os.path.exists(srt_path):
            print(f"SRT file not found at: {srt_path}")
            # Try to find by matching pattern in processed_videos directory
            print(f"Trying to find match for: {video_id}")
            matching_files = [f for f in os.listdir(PROCESSED_FOLDER) 
                             if f.endswith('.srt') and video_id in f]
            
            if matching_files:
                print(f"Found matching file: {matching_files[0]}")
                srt_path = os.path.join(PROCESSED_FOLDER, matching_files[0])
            else:
                return jsonify({'error': f'Transcript file not found: {srt_path}'}), 404
            
        # Generate summary using the gemma_summarizer
        print(f"Generating summary from: {srt_path}")
        summary = gemma_summarizer.summarize_from_file(srt_path)
        
        return jsonify({
            'summary': summary,
            'video_id': video_id
        })
        
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/matches/upload', methods=['POST'])
@token_required
def upload_match(current_user):
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    video_file = request.files['video']
    if video_file.filename == '' or not allowed_file(video_file.filename):
        return jsonify({'error': 'Invalid or no selected video file'}), 400

    # --- Get form data ---
    title = request.form.get('title')
    team1_name = request.form.get('team1_name')
    team2_name = request.form.get('team2_name')
    team1_score_str = request.form.get('team1_score')
    team2_score_str = request.form.get('team2_score')
    match_date_str = request.form.get('match_date')  # Expect YYYY-MM-DD
    competition = request.form.get('competition')

    print(f"[UPLOAD_MATCH] Received score strings: team1='{team1_score_str}', team2='{team2_score_str}'") # DEBUG

    if not team1_name or not team2_name:
        return jsonify({'error': 'Team names are required'}), 400

    # --- Process optional fields ---
    team1_score = int(team1_score_str) if team1_score_str and team1_score_str.isdigit() else None
    team2_score = int(team2_score_str) if team2_score_str and team2_score_str.isdigit() else None
    match_date = None
    if match_date_str:
        try:
            match_date = datetime.strptime(match_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    print(f"[UPLOAD_MATCH] Processed scores (int/None): team1={team1_score}, team2={team2_score}") # DEBUG

    # --- Save video file ---
    video_filename = secure_filename(f"{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{video_file.filename}")
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
    try:
        video_file.save(video_path)
    except Exception as e:
        print(f"Error saving video: {e}")
        return jsonify({'error': f'Failed to save video file: {str(e)}'}), 500

    # --- Create Match record ---
    new_match = Match(
        user_id=current_user.id,
        title=title,
        team1_name=team1_name,
        team2_name=team2_name,
        team1_score=team1_score,
        team2_score=team2_score,
        match_date=match_date,
        competition=competition,
        video_filename=video_filename,  # Store only filename
        status=MatchStatus.UPLOADED
    )
    db.session.add(new_match)
    try:
        print(f"[UPLOAD_MATCH] Before commit: Match object scores: team1={new_match.team1_score}, team2={new_match.team2_score}") # DEBUG
        db.session.commit()
        print(f"[UPLOAD_MATCH] After commit: Match record created with ID: {new_match.id}")

        # --- Trigger transcription in background ---
        # Using threading for simplicity
        thread = threading.Thread(target=run_transcription_task, args=(app, new_match.id))
        thread.start()

        return jsonify(new_match.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        print(f"[UPLOAD_MATCH] Error creating match record: {e}") # DEBUG
        # Clean up saved video file if DB commit fails
        if os.path.exists(video_path):
            os.remove(video_path)
        return jsonify({'error': f'Failed to create match record: {str(e)}'}), 500

@app.route('/api/match/<int:match_id>/trigger-tactical-analysis', methods=['POST'])
@token_required
def trigger_tactical_analysis_endpoint(current_user, match_id):
    match = Match.query.get(match_id)
    if not match:
        return jsonify({'error': 'Match not found'}), 404
    
    # Optional: Check if the current user owns the match or has permission
    # if match.user_id != current_user.id:
    #     return jsonify({'error': 'Forbidden. You do not own this match.'}), 403

    if match.tactical_analysis_status in [TacticalAnalysisStatus.PENDING, TacticalAnalysisStatus.PROCESSING]:
        return jsonify({'message': 'Tactical analysis is already in progress.'}), 409
    
    # Optionally allow re-triggering for COMPLETED or FAILED states
    # if match.tactical_analysis_status == TacticalAnalysisStatus.COMPLETED:
    #     return jsonify({'message': 'Tactical analysis is already completed. Re-trigger if needed.'}), 200

    try:
        # Use app._get_current_object() to pass the current app instance to the thread
        # This is important for the thread to have the correct application context.
        thread_app_context = current_app._get_current_object()
        thread = threading.Thread(target=_execute_tactical_analysis, args=(thread_app_context, match_id))
        thread.start()
        
        # Update status to PENDING immediately
        match.tactical_analysis_status = TacticalAnalysisStatus.PENDING
        db.session.commit()
        
        # No task_id to return, as it's a simple thread.
        return jsonify({'message': 'Tactical analysis triggered.'}), 202 
    except Exception as e:
        app.logger.error(f"Failed to trigger tactical analysis for match {match_id}: {str(e)}")
        return jsonify({'error': f"Could not trigger analysis task: {str(e)}"}), 500

@app.route('/api/match/<int:match_id>/tactical-analysis', methods=['GET'])
@token_required
def get_tactical_analysis_details(current_user, match_id):
    match = Match.query.get_or_404(match_id)
    
    response_data = {
        'match_id': match.id,
        'title': match.title,
        'team1_name': match.team1_name,
        'team2_name': match.team2_name,
        'competition': match.competition,
        'match_date': match.match_date.strftime('%Y-%m-%d') if match.match_date else None,
        'status': match.tactical_analysis_status.value if match.tactical_analysis_status else TacticalAnalysisStatus.NOT_STARTED.value,
        'overlay_video_url': match.get_tactical_overlay_video_url() if match.tactical_analysis_status == TacticalAnalysisStatus.COMPLETED and match.tactical_overlay_video_filename else None,
        'error_message': match.error_message if match.tactical_analysis_status == TacticalAnalysisStatus.FAILED else None,
        'heatmaps_final': [],
        'heatmaps_intermediate': [] 
    }

    if match.tactical_analysis_status == TacticalAnalysisStatus.COMPLETED and match.heatmaps_generated:
        heatmaps_final_subfolder = "final_heatmaps"
        # Use f-string for URL-safe path component
        heatmaps_folder_relative_final_url = f"{match_id}/{heatmaps_final_subfolder}"
        # For os.path.exists, use os.path.join
        full_heatmaps_path_final_os = os.path.join(TACTICS_OUTPUT_FOLDER, str(match_id), heatmaps_final_subfolder)


        if os.path.exists(full_heatmaps_path_final_os) and os.path.isdir(full_heatmaps_path_final_os):
            try:
                heatmap_files = [f for f in os.listdir(full_heatmaps_path_final_os) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                heatmap_files.sort() 
                response_data['heatmaps_final'] = [
                    url_for('serve_tactics_output_file', filename=f"{heatmaps_folder_relative_final_url}/{hf}", _external=True)
                    for hf in heatmap_files
                ]
            except Exception as e:
                app.logger.error(f"Error listing final heatmaps for match {match_id} from {full_heatmaps_path_final_os}: {str(e)}")
        else:
            app.logger.warn(f"Final heatmaps folder not found for completed analysis of match {match_id} at {full_heatmaps_path_final_os}")

        match_output_dir_full_path_os = os.path.join(TACTICS_OUTPUT_FOLDER, str(match_id)) 
        if os.path.exists(match_output_dir_full_path_os) and os.path.isdir(match_output_dir_full_path_os):
            sorted_items = sorted(os.listdir(match_output_dir_full_path_os)) 
            for item_name in sorted_items:
                if item_name.startswith("heatmaps_") and os.path.isdir(os.path.join(match_output_dir_full_path_os, item_name)):
                    frame_label_part = item_name.split('_')[-1] 
                    intermediate_set = {
                        "label": f"Frames segment around {frame_label_part}", 
                        "images": []
                    }
                    current_intermediate_path_full_os = os.path.join(match_output_dir_full_path_os, item_name)
                    # Use f-string for URL-safe path component
                    current_intermediate_path_relative_url = f"{match_id}/{item_name}"
                    try:
                        img_files = [f for f in os.listdir(current_intermediate_path_full_os) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                        img_files.sort()
                        for img_f in img_files:
                            img_file_relative_path_url = f"{current_intermediate_path_relative_url}/{img_f}"
                            intermediate_set["images"].append(
                                url_for('serve_tactics_output_file', filename=img_file_relative_path_url, _external=True)
                            )
                        if intermediate_set["images"]:
                            response_data['heatmaps_intermediate'].append(intermediate_set)
                    except Exception as e:
                        app.logger.error(f"Error listing intermediate heatmaps for match {match_id} from {current_intermediate_path_full_os}: {str(e)}")
            
    return jsonify(response_data), 200



def run_transcription_task(flask_app, match_id):
    """Function to run transcription in a background thread."""
    with flask_app.app_context():  # Need app context for DB operations
        match = Match.query.get(match_id)
        if not match:
            print(f"Transcription Task: Match {match_id} not found.")
            return

        video_path = os.path.join(flask_app.config['UPLOAD_FOLDER'], match.video_filename)
        if not os.path.exists(video_path):
            match.status = MatchStatus.ERROR
            match.error_message = f"Video file not found at {video_path}"
            db.session.commit()
            print(f"Transcription Task: Video file not found for Match {match_id}")
            return

        print(f"Starting transcription for Match ID: {match_id}, Video: {match.video_filename}")
        match.status = MatchStatus.PROCESSING_CAPTIONS
        db.session.commit()

        try:
            # --- Transcription Logic (adapted from public_transcribe) ---
            audio_path = extract_audio(video_path)
            print(f"Audio extracted to {audio_path} for Match {match_id}")

            result = transcriber.transcribe_audio(audio_path)
            print(f"Transcription complete for Match {match_id}")

            base_filename = os.path.splitext(match.video_filename)[0]
            srt_filename = f"{base_filename}.srt"
            srt_path = os.path.join(PROCESSED_FOLDER, srt_filename)
            transcriber.generate_srt(result, srt_path)
            print(f"SRT file generated at {srt_path} for Match {match_id}")

            # --- Update Match record on success ---
            match.srt_filename = srt_filename
            match.status = MatchStatus.CAPTIONS_READY
            match.error_message = None  # Clear any previous error
            db.session.commit()
            print(f"Match {match_id} status updated to CAPTIONS_READY")

            # Clean up temporary audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)

        except Exception as e:
            # --- Update Match record on error ---
            print(f"ERROR during transcription for Match {match_id}: {str(e)}")
            traceback.print_exc()
            match.status = MatchStatus.ERROR
            match.error_message = f"Transcription failed: {str(e)}"
            db.session.commit()
            print(f"Match {match_id} status updated to ERROR")


@app.route('/api/matches', methods=['GET'])
@token_required
def get_matches(current_user):
    # Optionally filter by user: matches = Match.query.filter_by(user_id=current_user.id).order_by(Match.uploaded_at.desc()).all()
    matches = Match.query.order_by(Match.uploaded_at.desc()).all()
    return jsonify([match.to_dict() for match in matches]), 200


@app.route('/api/matches/<int:match_id>', methods=['GET'])
@token_required
def get_match(current_user, match_id):
    match = Match.query.get(match_id)
    if not match:
        return jsonify({'error': 'Match not found'}), 404
    # Optional: Check if current_user owns the match if needed
    # if match.user_id != current_user.id:
    #     return jsonify({'error': 'Forbidden'}), 403
    return jsonify(match.to_dict()), 200


@app.route('/api/matches/<int:match_id>/summarize', methods=['POST'])
@token_required
def summarize_match(current_user, match_id):
    match = Match.query.get(match_id)
    if not match:
        return jsonify({'error': 'Match not found'}), 404

    # Optional: Check ownership
    # if match.user_id != current_user.id:
    #     return jsonify({'error': 'Forbidden'}), 403

    if match.status not in [MatchStatus.CAPTIONS_READY, MatchStatus.ANALYSIS_COMPLETE]:  # Ensure captions exist
        return jsonify({'error': 'Captions not ready or failed for this match'}), 400

    if not match.srt_filename:
        return jsonify({'error': 'SRT filename missing for this match'}), 500

    srt_path = os.path.join(PROCESSED_FOLDER, match.srt_filename)
    if not os.path.exists(srt_path):
        return jsonify({'error': f'SRT file not found: {match.srt_filename}'}), 404

    try:
        print(f"Generating summary for Match {match_id} from: {srt_path}")
        summary = gemma_summarizer.summarize_from_file(srt_path)

        # Save the summary to the match record
        match.summary = summary
        # Optionally update status if needed, e.g., match.status = MatchStatus.ANALYSIS_COMPLETE
        db.session.commit()

        return jsonify({
            'summary': summary,
            'match_id': match_id
        })

    except Exception as e:
        print(f"Error generating summary for Match {match_id}: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'Failed to generate summary: {str(e)}'}), 500
    
@app.route('/predict/player/<player_name>', methods=['GET'])
def predict_player(player_name):
    features_df = get_player_features_from_dataset(player_name)
    if features_df is None:
        return jsonify({"error": f"Player '{player_name}' not found in dataset"}), 404
    features_imputed = imputer.transform(features_df)
    perf_pred = performance_model.predict(features_imputed)[0]
    longevity_prob = longevity_model.predict_proba(features_imputed)[0][1]
    return jsonify({
        "player_name": player_name,
        "predictions": {
            "goals": float(perf_pred[0]),
            "assists": float(perf_pred[1]),
            "matches": float(perf_pred[2]),
            "minutes": float(perf_pred[3])
        },
        "probability_playing_next_season": float(longevity_prob)
    })

@app.route('/predict/new_player', methods=['POST'])
def predict_new_player():
    data = request.json
    if not data or 'career_stats' not in data:
        return jsonify({"error": "Missing 'career_stats' in request"}), 400
    features_df = process_new_player_data(data['career_stats'])
    features_imputed = imputer.transform(features_df)
    perf_pred = performance_model.predict(features_imputed)[0]
    longevity_prob = longevity_model.predict_proba(features_imputed)[0][1]
    return jsonify({
        "player_name": data.get('name', 'New Player'),
        "predictions": {
            "goals": float(perf_pred[0]),
            "assists": float(perf_pred[1]),
            "matches": float(perf_pred[2]),
            "minutes": float(perf_pred[3])
        },
        "probability_playing_next_season": float(longevity_prob)
    })

@app.route('/players', methods=['GET'])
def get_players2():
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip()
    df['season_start'] = df['season'].astype(str).str.extract(r'(\d{4})')[0]
    df['season_start'] = pd.to_numeric(df['season_start'], errors='coerce').fillna(0).astype(int)
    latest = df.sort_values('season_start').groupby('player_name').tail(1)
    players = [
        {
            "name": row['player_name'],
            "age": int(row['age']) if pd.notnull(row['age']) else None,
            "position": row['position'],
            "team": row['team']
        }
        for _, row in latest.iterrows()
    ]
    return jsonify(players)

@app.route('/player/<name>/career', methods=['GET'])
def player_career(name):
    import pandas as pd
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip()
    player_df = df[df['player_name'] == name]
    if player_df.empty:
        return jsonify({"error": "Player not found"}), 404
    player_df = player_df.sort_values('season')
    info = player_df.iloc[-1][['player_name', 'age', 'position', 'team']].to_dict()
    career = player_df[['season', 'goals', 'assists', 'minutes', 'mp']].to_dict(orient='records')
    return jsonify({'info': info, 'career': career})

#app.app_context().push()
if __name__ == '__main__':
    app.run(debug=True)
