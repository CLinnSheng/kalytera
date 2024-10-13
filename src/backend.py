from flask import Flask, request, jsonify
from flask_cors import CORS
from ai import ai
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DATABASE = 'kalytera.db'

def init_db():
    # Delete the database file if it exists, starting fresh
    if os.path.exists(DATABASE):
        os.remove(DATABASE)

    # Create a new database and table
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_inputs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  current_position TEXT,
                  skills TEXT,
                  desired_position TEXT)''')
    conn.commit()
    conn.close()

# Initialize the database (clearing it and starting fresh)
init_db()

@app.route('/submit', methods=['POST'])
def submit_data():
    data = request.json
    username = data.get('username')
    current_position = data.get('currentPosition')
    skills = data.get('skills')
    desired_position = data.get('desiredPosition')

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''INSERT INTO user_inputs (username, current_position, skills, desired_position)
                 VALUES (?, ?, ?, ?)''', (username, current_position, skills, desired_position))
    conn.commit()
    conn.close()

    return jsonify({"message": "Data submitted successfully"}), 200

@app.route('/get_data', methods=['GET'])
def get_data():
    username = request.args.get('username')
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''SELECT * FROM user_inputs WHERE username = ?''', (username,))
    data = c.fetchall()
    conn.close()

    if data:
        result = [
            {
                "id": row[0],
                "username": row[1],
                "current_position": row[2],
                "skills": row[3],
                "desired_position": row[4],
                'ai_response': ai(data[0][2], data[0][3], data[0][4])
            }
            for row in data
        ]
        return jsonify(result), 200
    else:
        return jsonify({"message": "No data found for this username"}), 404

if __name__ == '__main__':
    app.run(debug=True)
