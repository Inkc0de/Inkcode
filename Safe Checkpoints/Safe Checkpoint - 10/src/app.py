import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_socketio import SocketIO
import firebase_admin
from firebase_admin import credentials
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)  # Generate a random secret key

# Initialize Firebase Admin SDK
cred = credentials.Certificate('D:\\College Work\\Assignments, Projects & Extra\\College Projects\\Inkcode\\src\\inkcode-cadec-firebase-adminsdk-m8ngo-4d5ebae0e7.json')  # Update this path
firebase_admin.initialize_app(cred)

# Your Firebase project credentials
FIREBASE_API_KEY = 'AIzaSyAsAjxes6vzJr0gfVz69dpLXtjabzIxVo0'

# JDoodle API details
jdoodle_client_id = "1bd6ce41f902b6dc01acf08400013691"  # Replace with your JDoodle Client ID
jdoodle_client_secret = "f40f639b7460a4988e1f29f7f01eb035f4c0af0022a5aa71cf60abe88ae9a295"  # Replace with your JDoodle Client Secret
jdoodle_api_url = "https://api.jdoodle.com/v1/execute"

@app.route('/')
def index():
    return render_template('signin.html')

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

@app.route('/editor_collab')
def editor_collab():
    user_username = session.get('user_username')  # Retrieve the username from session
    print("Username from session:", user_username)  # Debugging line
    return render_template('editor_collab.html', username=user_username)  # Pass the username to the template


@app.route('/editor(2)')  # New route for the HTML editor
def editor_html():
    return render_template('editor(2).html')  # Updated to the new filename


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
