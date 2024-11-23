import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_socketio import SocketIO
import firebase_admin
from firebase_admin import credentials, firestore, auth
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)  # Generate a random secret key

# Initialize Firebase Admin SDK
cred = credentials.Certificate(r'D:\College Work\Assignments, Projects & Extra\inkcode\src\inkcode-cadec-firebase-adminsdk-m8ngo-4d5ebae0e7.json') # Update this path
firebase_admin.initialize_app(cred)

# Your Firebase project credentials
FIREBASE_API_KEY = 'AIzaSyAsAjxes6vzJr0gfVz69dpLXtjabzIxVo0'

# JDoodle API details
jdoodle_client_id = "e2f8c7250c07b7bf14fea810bc6ceff1"  # Replace with your JDoodle Client ID
jdoodle_client_secret = "9575227e01787e956de013e81defdce647af43c9be0cdb9032d770b0f88524c1"  # Replace with your JDoodle Client Secret
jdoodle_api_url = "https://api.jdoodle.com/v1/execute"

@app.route('/')
def index():
    return render_template('LandingPage.html')

@app.route('/process_input', methods=['POST'])
def process_input():
    # Receive user input from JavaScript
    user_input = request.json.get('user_input')
    response_message = f"Hello, {user_input}!"
    return jsonify({"response": response_message})

# Flask route to fetch the code content by project ID or file name
@app.route('/get_code/<project_id>', methods=['GET'])
def get_code(project_id):
    try:
        # Assuming projects are stored with IDs or names and in a dictionary or database
        code_content = load_code_from_storage(project_id)  # Replace with your actual storage retrieval
        return jsonify({'status': 'success', 'code': code_content})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

db = firestore.client()

@app.route('/contact')
def contact():
    return render_template('contactus.html')

@app.route('/notification', methods=['GET', 'POST'])
def notification():
    # Fetch user email from session
    user_email = session.get('user_email')

    if not user_email:
        return redirect(url_for('signin'))  # Redirect to login page if user is not authenticated

    # If the request is a POST (mark as read)
    if request.method == 'POST':
        notification_id = request.json.get('notification_id')
        
        if not notification_id:
            return jsonify({"status": "error", "message": "Invalid request"}), 400
        
        # Fetch the notification from the database using notification_id
        notification_ref = db.collection('notifications').document(notification_id)
        notification = notification_ref.get()

        if notification.exists:
            # Mark the notification as read
            notification_ref.update({'readStatus': True})
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "error", "message": "Notification not found"}), 404
    
    # If the request is a GET (fetch notifications)
    notifications_ref = db.collection('notifications').where('userEmail', '==', user_email)
    notifications = notifications_ref.stream()

    # Build a list of notifications
    notifications_list = [
        {**n.to_dict(), 'id': n.id, 'readStatus': n.to_dict().get('readStatus', False)} for n in notifications
    ]

    # Fetch user details from session
    user_username = session.get('user_username')

    # Return the notifications to the template
    return render_template('notification.html', 
                           email=user_email, 
                           username=user_username, 
                           notifications=notifications_list)

@app.route('/run_code', methods=['POST'])
def run_code():
    code = request.json.get('code')
    user_input = request.json.get('userInput', '')
    language = request.json.get('language', 'python').lower()

    language_map = {
        'python': ('python3', '3'),
        'javascript': ('nodejs', '3'),
        'c': ('c', '5'),
        'cpp': ('cpp17', '0'),
        'java': ('java', '4'),
        'html': ('html', '1'),  # Added HTML to the language map
    }

    if language not in language_map:
        return jsonify({'error': f"Unsupported language: {language}"}), 400

    jdoodle_language, version_index = language_map[language]

    # If the language is C and there is no user input, prompt for it
    if language == 'c' and 'scanf' in code and not user_input:
        return jsonify({
            'output': '',
            'error': '',
            'requiresInput': True,
            'message': 'This code requires input. Please provide the necessary input.'
        })

    # If the language is javascript and there is no user input, prompt for it
    elif language == 'javascript' and 'prompt' in code and not user_input:
        return jsonify({
            'output': '',
            'error': '',
            'requiresInput': True,
            'message': 'This code requires input. Please provide the necessary input.'
        })

    # If the language is javascript and there is no user input, prompt for it
    elif language == 'python' and 'input' in code and not user_input:
        return jsonify({
            'output': '',
            'error': '',
            'requiresInput': True,
            'message': 'This code requires input. Please provide the necessary input.'
        })

    # If the language is javascript and there is no user input, prompt for it
    elif language == 'cpp' and 'cin' in code and not user_input:
        return jsonify({
            'output': '',
            'error': '',
            'requiresInput': True,
            'message': 'This code requires input. Please provide the necessary input.'
        })

    elif language == 'java' and 'scanner' in code and not user_input:
        return jsonify({
            'output': '',
            'error': '',
            'requiresInput': True,
            'message': 'This code requires input. Please provide the necessary input.'
        })
        

    # Prepare payload for JDoodle API
    payload = {
        'clientId': jdoodle_client_id,
        'clientSecret': jdoodle_client_secret,
        'script': code,
        'stdin': user_input,
        'language': jdoodle_language,
        'versionIndex': version_index
    }

    try:
        response = requests.post(jdoodle_api_url, json=payload)
        response.raise_for_status()
        result = response.json()

        return jsonify({
            'output': result.get('output', ''),
            'error': result.get('error', ''),
            'requiresInput': False
        })

    except requests.exceptions.HTTPError as err:
        return jsonify({'error': f"HTTP error occurred: {err}"}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return redirect(url_for('index'))

        url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}'
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        response = requests.post(url, json=payload)
        data = response.json()

        if 'error' in data:
            flash('Invalid email or password. Please try again.', 'danger')
            return redirect(url_for('index'))

        # Store user info in session
        session['user_email'] = email
        session['user_username'] = email.split('@')[0] 

        flash('Sign in successful!', 'success')
        return redirect(url_for('homepage'))

    return render_template('signin.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return redirect(url_for('signup'))

        url = f'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}'
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        response = requests.post(url, json=payload)
        data = response.json()

        if 'error' in data:
            flash(f'Error creating account: {data["error"]["message"]}', 'danger')
            return redirect(url_for('signup'))

        flash('Account created successfully! You can now sign in.', 'success')
        return redirect(url_for('index'))

    return render_template('signup.html')

@app.route('/homepage')
def homepage():
    user_email = session.get('user_email')
    user_username = session.get('user_username')

    return render_template('homepage.html', email=user_email, username=user_username)

@app.route('/editor')
def editor():
    return render_template('editor.html')

@app.route('/editor(2)_collab')
def editor_html_collab():
    return render_template('editor(2)_collab.html')  # Updated to the new filename

@app.route('/editor_collab')
def editor_collab():
    user_username = session.get('user_username')  # Retrieve the username from session
    if not user_username:
        return redirect(url_for('signin')) 
    print("Username from session:", user_username)  # Debugging line
    return render_template('editor_collab.html', username=user_username)  # Pass the username to the template  # Pass the username to the template

@app.route('/editor(2)')  # New route for the HTML editor
def editor_html():
    return render_template('editor(2).html')  # Updated to the new filename

@app.route('/Future_plans')
def future_plans():
    user_email = session.get('user_email')
    user_username = session.get('user_username')
    return render_template('Future_plans.html', email=user_email, username=user_username)

@app.route('/community')
def community():
    user_email = session.get('user_email')
    user_username = session.get('user_username')
    return render_template('community.html', email=user_email, username=user_username)

@app.route('/trash')
def trash():
    user_email = session.get('user_email')
    user_username = session.get('user_username')
    return render_template('trash.html', email=user_email, username=user_username)

@app.route('/logout')
def logout():
    # Clear session data
    session.clear()
    # Redirect to the login page
    return redirect(url_for('signin'))

chats = {}

# POST endpoint to send a message
@app.route('/api/send_message', methods=['POST'])
def send_message():
    data = request.json
    project_id = data['project_id']
    user = data['user']
    message = data['message']
    timestamp = datetime.now().isoformat()

    if project_id not in chats:
        chats[project_id] = []
    
    chats[project_id].append({
        'user': user,
        'message': message,
        'timestamp': timestamp
    })
    return jsonify({'status': 'Message sent'}), 200

# GET endpoint to retrieve chat messages for a project
@app.route('/api/get_messages/<project_id>', methods=['GET'])
def get_messages(project_id):
    project_chats = chats.get(project_id, [])
    return jsonify({'messages': project_chats}), 200

@app.route('/test')  # test route
def test():
    return render_template('test-1.html') 

if __name__ == '__main__':
    app.run(debug=True)
