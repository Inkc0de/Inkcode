import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import firebase_admin
from firebase_admin import credentials
from flask_cors import CORS

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
    # Get code, user input, and programming language from the request
    code = request.json.get('code')
    user_input = request.json.get('userInput', '')
    language = request.json.get('language', 'python').lower()

    # Map common languages to JDoodle's expected language and version index
    language_map = {
        'python': ('python3', '3'),  # JDoodle uses 'python3'
        'javascript': ('nodejs', '3'),  # JDoodle uses 'nodejs'
        'c': ('c', '5'),  # Use version 5 for C
        'cpp': ('cpp17', '0'),  # JDoodle uses 'cpp17'
        'java': ('java', '4'),  # JDoodle uses 'java'
        # Add more languages here as needed
    }

    if language not in language_map:
        return jsonify({'error': f"Unsupported language: {language}"}), 400

    jdoodle_language, version_index = language_map[language]

    # Prepare payload for JDoodle submission
    payload = {
        'clientId': jdoodle_client_id,
        'clientSecret': jdoodle_client_secret,
        'script': code,
        'stdin': user_input,
        'language': jdoodle_language,
        'versionIndex': version_index  # Use correct version for the language
    }

    try:
        # Submit the code to JDoodle
        response = requests.post(jdoodle_api_url, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        result = response.json()  # Parse the JSON response

        # Return output
        return jsonify({
            'output': result.get('output', ''),
            'error': result.get('error', ''),
            'requiresInput': False  # Modify if JDoodle indicates that input is required
        })

    except requests.exceptions.HTTPError as err:
        output = f"HTTP error occurred: {err}"
        return jsonify({'error': output}), 500
    except Exception as e:
        output = str(e)
        return jsonify({'error': output}), 500

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
        session['user_username'] = email.split('@')[0]  # Example username; modify as needed

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

@app.route('/logout')
def logout():
    # Clear session data
    session.clear()
    # Redirect to the login page
    return redirect(url_for('signin'))

if __name__ == '__main__':
    app.run(debug=True)
