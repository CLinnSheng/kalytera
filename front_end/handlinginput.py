from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    print(f"Received login attempt - Email: {email}, Password: {password}")
    
    # Simple validation (replace with your actual authentication logic)
    if email == "admin@example.com" and password == "password123":
        response = {
            "status": "success",
            "message": "Login successful",
            "user": {
                "email": email,
                "name": "Admin User"
            }
        }
    else:
        response = {
            "status": "failed",
            "message": "Invalid credentials"
        }
    
    print(f"Sending response: {response}")
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)