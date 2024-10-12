from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Route to handle login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()  # Get JSON data from the request
    email = data.get('email')
    password = data.get('password')
    
    # You can now process the email and password, for example, by checking them against a database
    print(f"Email: {email}, Password: {password}")
    
    # Dummy logic for demonstration
    if email == "admin@example.com" and password == "password123":
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

if __name__ == '__main__':
    app.run(debug=True)