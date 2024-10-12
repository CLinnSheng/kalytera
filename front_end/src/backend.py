from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This allows all origins. In production, you should specify allowed origins.

@app.route('/submit-info', methods=['POST'])
def submit_info():
    data = request.json
    
    # Extract data from the request
    current_position = data.get('currentPosition')
    skills = data.get('skills')
    desired_position = data.get('desiredPosition')
    
    # Here you would typically process the data, maybe save it to a database
    # For this example, we'll just print it and send it back
    print(f"Received data: Current Position: {current_position}, Skills: {skills}, Desired Position: {desired_position}")
    
    # You could add some processing logic here
    
    # Send a response back to the frontend
    response = {
        "message": "Information received successfully",
        "data": {
            "currentPosition": current_position,
            "skills": skills,
            "desiredPosition": desired_position
        }
    }
    
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True)