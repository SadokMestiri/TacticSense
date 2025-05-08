import os
from flask import Flask, request, jsonify, send_from_directory, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy import Enum
from flask_mail import Mail, Message 


app = Flask(__name__,template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:0000@localhost/metascout"
db = SQLAlchemy(app)
CORS(app, supports_credentials=True)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'nourhene.benhamida25@gmail.com'
app.config['MAIL_PASSWORD'] = 'ioom bhbb kirq fafx'
mail = Mail(app)

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
        role = request.form['role']
        
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return jsonify({'message': 'Username or email already exists'}), 409

        profile_image = request.files.get('profile_image')
        profile_image_path = None
        if profile_image and allowed_file(profile_image.filename):
            filename = secure_filename(profile_image.filename)
            profile_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_image.save(profile_image_path) 

        hashed_password = generate_password_hash(password, method='sha256')

        new_user = User(username=username, email=email, password=hashed_password, name=name, profile_image=profile_image_path, role=role)

        db.session.add(new_user)
        db.session.commit()

        if role == 'Player':
            print("Creating player profile for:", name)
            player_profile = PlayerProfile(
                user_id=new_user.id,
                name=new_user.name,
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
                total_red_cards=0
            )
            db.session.add(player_profile)

        elif role == 'Coach':
            print("Creating coach profile for:", name)
            coach_profile = Coach_Profile(
                user_id=new_user.id,
                name=new_user.name,
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
        #msg = Message("Welcome to MetaScout!",
        #              sender=app.config['MAIL_USERNAME'],
        #              recipients=[email])
        #msg.html = f"""
        #    <p>Hello {name},</p>
        #    <p>Thank you for signing up on MetaScout. We’re excited to have you with us!</p>
        #    <p>Best regards,<br>The MetaScout Team</p>
        #"""
        #mail.send(msg)

        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        print("Registration failed:", str(e))
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return jsonify({'message': 'Login successful','user_id': user.id }), 200
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

