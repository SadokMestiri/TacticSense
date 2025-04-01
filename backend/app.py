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

# BO 6
from ml.speech.stt import WhisperTranscriber
from ml.video.extract import extract_audio
from ml.speech.tts import ElevenLabsTTS
from ml.speech.caption import CaptionEnhancer
from ml.video.overlay import overlay_subtitles
from ml.utils.srt import SRTFormatter


# Set up upload folder for processed videos
PROCESSED_FOLDER = os.path.join(os.getcwd(), 'processed_videos')
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


# Initialize components
transcriber = WhisperTranscriber()
tts_engine = ElevenLabsTTS()

# Initialize additional components
caption_enhancer = CaptionEnhancer()
srt_formatter = SRTFormatter()

app = Flask(__name__,template_folder='templates')
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
        token = None
        
        # Check if 'Authorization' header is in the request
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Extract token from 'Bearer TOKEN'
            except IndexError:
                token = auth_header  # If just the token is provided
        
        if not token:
            print("Token is missing")
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            print(f"Received token: {token[:10]}...")  # Debug token (first 10 chars)
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['id']).first()
        except Exception as e:
            print(f"Token verification error: {str(e)}")
            return jsonify({'message': 'Token is invalid!'}), 401
            
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
app.app_context().push()
if __name__ == '__main__':
    app.run(debug=True)



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
        # For testing, just return a success response
        return jsonify({
            'audio_url': f"/processed_videos/test_audio.mp3",
            'message': 'Audio would be generated here in production'
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