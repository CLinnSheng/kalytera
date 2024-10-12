from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    # Here you can add your authentication logic
    # For this example, let's assume the username is 'user' and the password is 'password'
    if username == 'user' and password == 'password':
        return jsonify({'status': 'success', 'message': 'Login successful'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid username or password'})

# Endpoint to handle welcome page data
@app.route('/submit_data', methods=['POST'])
def submit_data():
    data = request.json
    current_position = data.get('current_position')
    skills = data.get('skills')
    desired_position = data.get('desired_position')

    # Process the received data (e.g., store in database)
    print(f'Current position: {current_position}, Skills: {skills}, Desired position: {desired_position}')

    return jsonify({'status': 'success', 'message': 'Data submitted successfully!'})

if __name__ == '__main__':
    app.run(debug=True)
