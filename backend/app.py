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
import joblib
import pandas as pd
import numpy as np
import json

app = Flask(__name__,template_folder='templates')
CORS(app, 
     origins=["http://localhost:3000"], 
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
     allow_headers=["Content-Type", "Authorization"], 
     supports_credentials=True
)
app.config['SECRET_KEY'] = '59c9d8576f920846140e2a8985911bec588c08aebf4c7799ba0d5ae388393703'  
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:0000@localhost:5432/metascout"
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

class SavedPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('saved_posts_assoc', lazy=True))
    post = db.relationship('Post', backref=db.backref('savers_assoc', lazy=True))

    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='_user_post_uc'),)

    def __repr__(self):
        return f'<SavedPost user_id={self.user_id} post_id={self.post_id}>'

def process_new_player_data(career_stats):
    df = pd.DataFrame(career_stats)
    # Convert relevant columns to numeric
    for col in ['goals', 'assists', 'minutes', 'matches', 'age']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
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
        token_header = request.headers.get('Authorization')
        print(f"--- Token Debug: Authorization Header = {token_header} ---")

        if not token_header:
            print("--- Token Debug: Token is missing from header! ---")
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            parts = token_header.split(" ")
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                print(f"--- Token Debug: Invalid token format. Header: {token_header} ---")
                return jsonify({'message': 'Invalid token format. "Bearer " prefix missing or malformed.'}), 401
            
            token_value = parts[1]
            print(f"--- Token Debug: Token value to decode = {token_value} ---")
            
            decoded_token = jwt.decode(token_value, app.config['SECRET_KEY'], algorithms=['HS256'])
            print(f"--- Token Debug: Decoded payload = {decoded_token} ---")
            
            user_id_from_token = decoded_token.get('user_id') # Use .get() for safer access
            if user_id_from_token is None:
                print(f"--- Token Debug: 'user_id' key not found in decoded token payload: {decoded_token} ---")
                return jsonify({'message': "Invalid token payload: 'user_id' missing."}), 401
            
            print(f"--- Token Debug: User ID from token = {user_id_from_token} ---")
            current_user = User.query.get(user_id_from_token)
            print(f"--- Token Debug: User from DB = {current_user} ---")

        except jwt.ExpiredSignatureError:
            print("--- Token Debug: Token has expired! ---")
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError as e_invalid:
            print(f"--- Token Debug: JWT InvalidTokenError: {e_invalid} ---") # Log specific JWT error
            return jsonify({'message': 'Token is invalid!'}), 401 # This is what you're seeing
        except KeyError as e_key:
            print(f"--- Token Debug: KeyError accessing payload (e.g., 'user_id' missing): {e_key} ---")
            return jsonify({'message': 'Invalid token payload structure.'}), 401
        except Exception as e_generic: 
            print(f"--- Token Debug: Generic token processing error: {e_generic} ---") 
            return jsonify({'message': 'Token processing error!'}), 401

        if not current_user: 
            print(f"--- Token Debug: User not found in DB for user_id {user_id_from_token}! ---")
            return jsonify({'message': 'User not found for token!'}), 401
            
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
        
        profile_image_filename = None
        if user.profile_image:
            # Assuming user.profile_image stores just the filename like "avatar.jpg"
            # and it's served from your UPLOAD_FOLDER
            profile_image_filename = user.profile_image.replace("\\", "/")
        # If you intend to return a full URL, construct it here using url_for
        # e.g., profile_image_url = url_for('uploaded_file', filename=profile_image_filename, _external=True) if profile_image_filename else None

        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'name': user.name,
            'profile_image': profile_image_filename # Send the filename or full URL
        }), 200
    except Exception as e: # Consider more specific exceptions if possible
        print(f"Error fetching user data for ID {user_id}: {e}")
        # Ensure a JSON response for errors too, if not handled by a global error handler
        return jsonify({'message': 'User not found or error fetching data'}), 404

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
        if profile_image:
            filename = secure_filename(profile_image.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_image.save(save_path)
            profile_image_path = filename  # or save_path if you want the full path 
        hashed_password = generate_password_hash(password, method='sha256')

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
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=1) 
        }, app.config['SECRET_KEY'], algorithm='HS256') 
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
    db.session.commit()

    return jsonify({
        'message': 'Post created successfully',
        'post_content': post_content,
        'image_url': uploaded_image,
        'video_url': uploaded_video
    })

@app.route('/get_posts', methods=['GET'])
def get_posts():
    # Try to get token for current user, but don't require it
    current_user_id = None
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(" ")[1]
        try:
            decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = decoded_token.get('user_id') # Ensure your token has 'user_id'
        except jwt.ExpiredSignatureError:
            pass # Token expired, treat as anonymous
        except jwt.InvalidTokenError:
            pass # Invalid token, treat as anonymous

    posts = Post.query.order_by(Post.created_at.desc()).all() # Order by most recent
    posts_data = []

    # Fetch all reactions in a single query to optimize performance
    reactions_data = db.session.query(
        Reaction.post_id,
        Reaction.reaction_type,
        db.func.count(Reaction.reaction_id)
    ).group_by(Reaction.post_id, Reaction.reaction_type).all()

    reactions_dict = {}
    for post_id_rx, reaction_type, count in reactions_data:
        if post_id_rx not in reactions_dict:
            reactions_dict[post_id_rx] = {}
        reactions_dict[post_id_rx][reaction_type] = count

    saved_posts_by_current_user = set()
    if current_user_id:
        saved_posts_by_current_user = {sp.post_id for sp in SavedPost.query.filter_by(user_id=current_user_id).all()}

    for post in posts:
        post_reactions = reactions_dict.get(post.post_id, {})

        comments = Comment.query.filter_by(post_id=post.post_id).all()
        comments_data = [{
            'user_id': comment.user_id,
            # 'user_name': User.query.get(comment.user_id).name if User.query.get(comment.user_id) else "Unknown", # Consider fetching user names efficiently
            'comment_text': comment.comment_text,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for comment in comments]

        posts_data.append({
            'id': post.post_id,
            'user_id': post.user_id,
            'user_name': post.user.name, # Assuming post.user relationship is eager/efficiently loaded
            'user_profile_image': post.user.profile_image, # Add this
            'content': post.content,
            'image_url': post.image_url,
            'video_url': post.video_url,
            'likes': post_reactions.get('like', 0),
            'loves': post_reactions.get('love', 0),
            'laughs': post_reactions.get('laugh', 0),
            'wows': post_reactions.get('wow', 0),
            'angrys': post_reactions.get('angry', 0),
            'sads': post_reactions.get('sad', 0),
            'created_at': post.created_at.strftime('%Y-%m-%d %H:%M:%S'), # Ensure consistent formatting
            'comments_count': len(comments_data), # Send count instead of full comments here for main feed
            'is_saved': post.post_id in saved_posts_by_current_user if current_user_id else False
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

@app.route('/posts/<int:post_id>/save', methods=['POST'])
@token_required
def save_post(current_user, post_id):
    post = Post.query.get_or_404(post_id)
    existing_save = SavedPost.query.filter_by(user_id=current_user.id, post_id=post_id).first()

    if existing_save:
        return jsonify({'message': 'Post already saved'}), 409

    new_save = SavedPost(user_id=current_user.id, post_id=post_id)
    db.session.add(new_save)
    db.session.commit()
    return jsonify({'message': 'Post saved successfully'}), 201

@app.route('/posts/<int:post_id>/unsave', methods=['DELETE'])
@token_required
def unsave_post(current_user, post_id):
    saved_post = SavedPost.query.filter_by(user_id=current_user.id, post_id=post_id).first()

    if not saved_post:
        return jsonify({'message': 'Post not saved by this user'}), 404

    db.session.delete(saved_post)
    db.session.commit()
    return jsonify({'message': 'Post unsaved successfully'}), 200

@app.route('/users/<int:user_id>/saved_posts', methods=['GET'])
@token_required # Or remove if you want this to be public for any user
def get_saved_posts(current_user, user_id):
    # Ensure the logged-in user can only see their own saved posts,
    # or adjust logic if admins/other users can see them.
    if current_user.id != user_id:
         # If you want to allow fetching for other users, ensure they exist
        target_user = User.query.get_or_404(user_id)
        # Add any permission checks here if needed
    else:
        target_user = current_user

    saved_post_associations = SavedPost.query.filter_by(user_id=target_user.id).order_by(SavedPost.created_at.desc()).all()
    
    posts_data = []
    for assoc in saved_post_associations:
        post = assoc.post 
        if post: # Check if post still exists
             # You might want to reuse the post serialization logic from get_posts
            user_who_posted = User.query.get(post.user_id) # Get the user who made the post
            posts_data.append({
                'id': post.post_id,
                'user_id': post.user_id,
                'user_name': user_who_posted.name if user_who_posted else "Unknown User",
                'user_profile_image': user_who_posted.profile_image if user_who_posted else None,
                'content': post.content,
                'image_url': post.image_url,
                'video_url': post.video_url,
                'created_at': post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_saved': True # Since we are fetching saved posts
                # Add other relevant post details like reactions, comments count if needed
            })
    return jsonify(posts_data), 200

@app.route('/predict/player/<player_name>', methods=['GET'])
def predict_player(player_name):
    features_df = get_player_features_from_dataset(player_name)
    if features_df is None:
        return jsonify({"error": f"Player '{player_name}' not found in dataset"}), 404
    features_imputed = imputer.transform(features_df)
    perf_pred = performance_model.predict(features_imputed)[0]
    longevity_prob = longevity_model.predict_proba(features_imputed)[0][1]

    # Clip negative predictions to zero
    goals = max(0, float(perf_pred[0]))
    assists = max(0, float(perf_pred[1]))
    matches = max(0, float(perf_pred[2]))
    minutes = max(0, float(perf_pred[3]))

    return jsonify({
        "player_name": player_name,
        "predictions": {
            "goals": goals,
            "assists": assists,
            "matches": matches,
            "minutes": minutes
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

    # Clip negative predictions to zero
    goals = max(0, float(perf_pred[0]))
    assists = max(0, float(perf_pred[1]))
    matches = max(0, float(perf_pred[2]))
    minutes = max(0, float(perf_pred[3]))

    return jsonify({
        "player_name": data.get('name', 'New Player'),
        "predictions": {
            "goals": goals,
            "assists": assists,
            "matches": matches,
            "minutes": minutes
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
    df = pd.read_csv(DATA_PATH,  thousands=',', quotechar='"')
    df.columns = df.columns.str.strip()
    player_df = df[df['player_name'] == name]
    if player_df.empty:
        return jsonify({"error": "Player not found"}), 404

    # Filter out rows where 'season' is NaN
    player_df = player_df[player_df['season'].notna()]

    # Handle missing values and convert data types
    player_df['age'] = player_df['age'].fillna(0).astype(int)
    player_df['team'] = player_df['team'].fillna('Unknown')

    player_df = player_df.sort_values('season')
    # Extract info after handling missing values
    info = player_df.iloc[-1][['player_name', 'age', 'position', 'team']].to_dict()


    player_df['goals'] = pd.to_numeric(player_df['goals'], errors='coerce').fillna(0)
    player_df['assists'] = pd.to_numeric(player_df['assists'], errors='coerce').fillna(0)
    player_df['minutes'] = player_df['minutes'].astype(str).str.replace(',', '').astype(float).fillna(0).astype(int)
    player_df['mp'] = pd.to_numeric(player_df['mp'], errors='coerce').fillna(0)

    career = player_df[['season', 'goals', 'assists', 'minutes', 'mp']].to_dict(orient='records')
    return jsonify({'info': info, 'career': career})

app.app_context().push()
if __name__ == '__main__':
    with app.app_context(): # This is correct for ensuring context
        print("Attempting to create database tables...")
        db.create_all()
        print("Database tables should be created (if they didn't exist).")
    app.run(debug=True)

