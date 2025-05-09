import os
from flask import Flask, request, jsonify, send_from_directory, url_for, make_response
from flask_mail import Message as MailMessage
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import Enum
from sqlalchemy import Enum as SQLAlchemyEnum  # Renamed to avoid conflict
import jwt
from functools import wraps
from datetime import datetime, timedelta
from flask_mail import Mail
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


from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
import json

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
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:admin@localhost/metascout"
db = SQLAlchemy(app)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'layouni.nourelhouda@gmail.com'
app.config['MAIL_PASSWORD'] = 'kvni phac wprf smll'
mail = Mail(app)

app.config['UPLOAD_FOLDER'] = 'uploads' 

# Set up folder for tactical analysis outputs
TACTICS_OUTPUT_FOLDER = os.path.join(os.getcwd(), 'results')
os.makedirs(TACTICS_OUTPUT_FOLDER, exist_ok=True)
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  

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
    profile_image = db.Column(db.String(255), nullable=True) 



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
    df['position'] = df['position'].str.upper().str.strip()
    valid_positions = ['DF', 'MF', 'FW']
    df['position'] = df['position'].apply(lambda x: x if x in valid_positions else 'FW')
    df['minutes_adj'] = df['minutes'].replace(0, 1)
    df['goals_per_90'] = (df['goals'] * 90) / df['minutes_adj']
    df['assists_per_90'] = (df['assists'] * 90) / df['minutes_adj']
    primary_position = df['position'].mode()[0] if not df['position'].mode().empty else 'FW'
    pos_DF = 1 if primary_position == 'DF' else 0
    pos_MF = 1 if primary_position == 'MF' else 0
    pos_FW = 1 if primary_position == 'FW' else 0
    max_minutes = 5000
    if primary_position == 'FW':
        df['position_score'] = 0.7 * df['goals_per_90'] + 0.3 * df['assists_per_90']
    elif primary_position == 'MF':
        df['position_score'] = 0.4 * df['goals_per_90'] + 0.6 * df['assists_per_90']
    else:
        df['position_score'] = 0.2 * df['goals_per_90'] + 0.3 * df['assists_per_90'] + 0.5 * (df['minutes'] / max_minutes)
    last_3 = df.iloc[-3:] if len(df) >= 3 else df
    weights = np.arange(1, len(last_3)+1)
    def safe_avg(series): return np.average(series, weights=weights[:len(series)]) if len(series) else 0
    last_season = df.iloc[-1]
    matches_adj = max(last_season['matches'], 1)
    minutes_adj = max(last_season['minutes'], 1)
    rolling_3season_mins = df['minutes'].iloc[-3:].mean() if len(df) >= 3 else df['minutes'].mean()
    rolling_3season_mins_pct = (df['minutes'] / (df['matches'] * 90)).replace(0, 1).iloc[-3:].mean() if len(df) >= 3 else (df['minutes'] / (df['matches'] * 90)).replace(0, 1).mean()
    features = {
        'age': last_season['age'],
        'pos_DF': pos_DF,
        'pos_MF': pos_MF,
        'pos_FW': pos_FW,
        'team_encoded': 0.5,
        'season_start': 2025,
        'goals_per_90': last_season['goals_per_90'],
        'assists_per_90': last_season['assists_per_90'],
        'position_score': last_season['position_score'],
        'goals_per_90_weighted_recent': safe_avg(last_3['goals_per_90']),
        'assists_per_90_weighted_recent': safe_avg(last_3['assists_per_90']),
        'position_score_weighted_recent': safe_avg(last_3['position_score']),
        'minutes_weighted_recent': safe_avg(last_3['minutes']),
        'mins_per_appearance': minutes_adj / matches_adj,
        'availability': matches_adj / df['matches'].max() if df['matches'].max() > 0 else 1,
        'seasons_since_debut': len(df),
        'recent_form': df['position_score'].iloc[-3:].mean() if len(df) >= 3 else df['position_score'].mean(),
        'team_strength': 0.5,
        'injury_prone': int((minutes_adj / (matches_adj * 90)) < 0.6) if matches_adj > 0 else 0,
        'mins_pct_possible': minutes_adj / (matches_adj * 90) if matches_adj > 0 else 1,
        'rolling_3season_mins': rolling_3season_mins,
        'rolling_3season_mins_pct': rolling_3season_mins_pct,
        'minutes_weighted_recent': safe_avg(last_3['minutes'])
    }
    # Fill missing features with 0
    for fname in feature_names:
        if fname not in features:
            features[fname] = 0.0
    return pd.DataFrame([features])[feature_names]

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
    
    # Check if user exists and password matches
    if user and check_password_hash(user.password, password):
        # Create JWT token with expiration of 24 hours
        token = jwt.encode({
            'public_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=1)  # Changed from hours=1 to days=1
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
def get_players():
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