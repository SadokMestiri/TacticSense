import os
from flask import Flask, request, jsonify, send_from_directory, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy import Enum



app = Flask(__name__,template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:0000@localhost/metascout"
db = SQLAlchemy(app)
CORS(app, supports_credentials=True)
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

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    last_message_time = db.Column(db.DateTime, default=db.func.current_timestamp())


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
    
    new_message = Message(
        sender_id=data['sender_id'],
        receiver_id=data['receiver_id'],
        message=data['message']
    )
    
    db.session.add(new_message)
    db.session.commit()
    
    return jsonify({'message': 'Message sent successfully'}), 201
@app.route('/get_messages/<int:user1_id>/<int:user2_id>', methods=['GET'])
def get_messages(user1_id, user2_id):
    messages = Message.query.filter(
        (Message.sender_id == user1_id and Message.receiver_id == user2_id) |
        (Message.sender_id == user2_id and Message.receiver_id == user1_id)
    ).all()
    
    message_list = []
    for msg in messages:
        message_list.append({
            'sender_id': msg.sender_id,
            'receiver_id': msg.receiver_id,
            'message': msg.message,
            'timestamp': msg.timestamp
        })
    
    return jsonify(message_list), 200
@app.route('/create_conversation', methods=['POST'])
def create_conversation():
    data = request.get_json()
    
    conversation = Conversation.query.filter(
        ((Conversation.user1_id == data['user1_id']) & (Conversation.user2_id == data['user2_id'])) |
        ((Conversation.user1_id == data['user2_id']) & (Conversation.user2_id == data['user1_id']))
    ).first()
    
    if not conversation:
        new_conversation = Conversation(
            user1_id=data['user1_id'],
            user2_id=data['user2_id']
        )
        db.session.add(new_conversation)
        db.session.commit()
    
    return jsonify({'message': 'Conversation created successfully'}), 201

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

        hashed_password = generate_password_hash(password, method='sha256')

        new_user = User(username=username, email=email, password=hashed_password, name=name, profile_image=profile_image_path)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred. Please try again.'}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

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

