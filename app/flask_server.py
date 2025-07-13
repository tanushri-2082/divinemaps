# app/flask_server.py

from flask import Flask, request, jsonify, session
from flask_session import Session
import mysql.connector
from werkzeug.security import check_password_hash

app = Flask(__name__)

# Configure session
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a secure key
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="divinemaps"
    )

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['user_id']
            # Ensure religion is a valid string
            religion = user.get('religion', 'No Preference')
            if religion is None or not isinstance(religion, str):
                religion = 'No Preference'
                print(f"Warning: User {username} has invalid religion value: {user.get('religion')}")
            session['religion'] = religion
            print(f"Session set: user_id={session['user_id']}, religion={session['religion']}")  # Debug
            return jsonify({"religion": religion}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        print(f"Error in login: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('religion', None)
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/get_sites', methods=['GET'])
def get_sites():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check if user is logged in
        if 'user_id' in session:
            religion = session.get('religion', 'No Preference')
        else:
            religion = request.args.get('religion', 'No Preference')

        print(f"Fetching sites for religion: {religion}")  # Debug
        sites = []
        if religion == 'No Preference':
            query = "SELECT * FROM sites"
            cursor.execute(query)
            sites = cursor.fetchall()
        else:
            query = "SELECT * FROM sites WHERE religion = %s"
            cursor.execute(query, (religion,))
            sites = cursor.fetchall()

        cursor.close()
        conn.close()
        print(f"Returning {len(sites)} sites for religion: {religion}")
        return jsonify(sites)
    except Exception as e:
        print(f"Error in get_sites: {e}")
        return jsonify({"error": str(e), "sites": []}), 500

if __name__ == '__main__':
    app.run(debug=True)