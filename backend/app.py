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


app.app_context().push()
if __name__ == '__main__':
    app.run(debug=True)

