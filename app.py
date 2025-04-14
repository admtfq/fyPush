from flask import Flask, render_template, request, jsonify, redirect, url_for
import tensorflow as tf
import librosa
import numpy as np
import speech_recognition as sr
import random  
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database file
app.config['SECRET_KEY'] = 'DysarthriaSecretKey' 
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Create a User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    age = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)    

# Initialize the database
with app.app_context():
    db.create_all()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the trained model
model = tf.keras.models.load_model('models/model.h5')

# Allowed audio file types
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a'}

# List of target words
TARGET_WORDS = [
    "cat", "dog", "apple", "banana", "orange",
    "mom", "dad", "ball", "car", "hat",
    "sun", "moon", "baby", "bird", "duck",
    "yes", "no", "hi", "bye", "go",
    "up", "down", "red", "blue", "green",
    "milk", "book", "chair", "shoe", "fish",
    "hug", "jump", "sit", "run", "eat"
]


# Helper function to check file type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to pick a random word
def get_random_word():
    return random.choice(TARGET_WORDS)

# Preprocessing function for audio
def preprocess_audio(audio_file):
    """
    Preprocess audio file for dysarthria prediction.
    """
    x, sr = librosa.load(audio_file.stream, sr=22050)
    mfccs = np.mean(librosa.feature.mfcc(y=x, sr=sr, n_mfcc=128), axis=1)
    return mfccs.reshape(1, 16, 8, 1)

# Routes
@app.before_request
def log_request_info():
    logger.info(f"Request received: {request.method} {request.path}")

@app.route('/')
def home():
    return render_template('welcome.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Query the database for the user
        user = User.query.filter_by(username=username).first()

        # Check if user exists and the password is correct
        if user and bcrypt.check_password_hash(user.password, password):
            flash('Login successful', 'success')
            return redirect(url_for('mode'))  # Redirect to the homepage after successful login
        else:
            flash('Login failed. Check your username and password', 'danger')
            return redirect(url_for('error'))  # Stay on the login page if credentials are incorrect

    return render_template('login.html')

@app.route('/error')
def error():
    message = request.args.get('message', 'An unknown error occurred.')
    return render_template('error.html', message=message)

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/validate-signup', methods=['POST'])
def validate_signup():
    username = request.form['username']
    age = request.form['age']
    email = request.form['email']
    password = request.form['password']

    # Check if the username or email already exists
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        flash('Username or Email already exists', 'danger')
        return redirect(url_for('signup'))
    
    # Hash the password before storing
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Create a new user in the database
    new_user = User(username=username, age=age, email=email, password=hashed_password)

    # Add the user to the database and commit
    db.session.add(new_user)
    db.session.commit()

    flash('Your account has been created!', 'success')
    return redirect(url_for('login'))

@app.route('/get-word', methods=['GET'])
def get_target_word():
    word = get_random_word()
    return jsonify({'word': word})

@app.route('/predict', methods=['POST'])
def predict():
    if 'audio' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    audio_file = request.files['audio']
    target_word = request.form.get('target_word', '')
    feedback = analyze_speech(audio_file, target_word)
    return jsonify({'result': feedback})

@app.route('/Dysarthria')
def dysarthria_page():
    return render_template('Dysarthria.html')

@app.route('/mode')
def mode():
    return render_template('mode.html')  # Render your training page

@app.route('/training')
def training():
    return render_template('training.html')  # Render your training page

@app.route('/trainingYT')
def trainingYT():
    return render_template('trainingYT.html')  # Render your training page

@app.route('/detection')
def detection():
    return render_template('detection.html')  # Render your detection page


@app.route('/dysarthria-detect', methods=['POST'])
def dysarthria_detect():
    if 'audio' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    audio_file = request.files['audio']
    if not allowed_file(audio_file.filename):
        return jsonify({'error': 'Invalid file type. Only audio files are allowed.'}), 400
    try:
        features = preprocess_audio(audio_file)
        prediction = model.predict(features)[0][0]
        result = "Dysarthria Detected!" if prediction >= 0.5 else "No Dysarthria Detected!"
        probability = round(prediction * 100, 2) if prediction >= 0.5 else round((1 - prediction) * 100, 2)
        return jsonify({'result': result, 'probability': probability})
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

def analyze_speech(audio_file, target_word):
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
    try:
        recognized_text = r.recognize_google(audio).lower()
        if target_word.lower() in recognized_text:
            return "Correct!"
        else:
            return "Try again!"
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand."
    except sr.RequestError as e:
        return f"Error: {e}"

if __name__ == '__main__':
    app.run(debug=True)
