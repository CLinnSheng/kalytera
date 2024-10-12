import React, { useState } from 'react';
import './App.css'; // For styling

function App() {
  return (
    <div className="App">
      <LoginPage />
    </div>
  );
}

function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState(''); // State to hold the message
  const [messageType, setMessageType] = useState(''); // State for message type (success/error)

  const handleSubmit = (e) => {
    e.preventDefault(); // Prevent page reload on form submission

    // Send the email and password to the backend
    fetch('http://localhost:5000/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }), // Sending the email and password as JSON
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok'); // Handle non-200 responses
      }
      return response.json();
    })
    .then(data => {
      console.log('Success:', data);
      setMessage(data.message); // Set the message from the backend
      setMessageType('success'); // Set message type for styling
    })
    .catch((error) => {
      console.error('Error:', error);
      setMessage('An error occurred. Please try again.'); // Set a generic error message
      setMessageType('error'); // Set message type for styling
    });
  };

  return (
    <div className="login-container">
      <div className="login-left">
        <img src="src/assets/PSA_Logo.jpg" alt="PSA Logo" className="logo" />
        <h2>LOGIN</h2>
        <form onSubmit={handleSubmit}>
          <input 
            type="text" 
            placeholder="COMPANY EMAIL" 
            value={email} 
            onChange={(e) => setEmail(e.target.value)} 
            required // Adding required field
          /><br />
          <input 
            type="password" 
            placeholder="PASSWORD" 
            value={password} 
            onChange={(e) => setPassword(e.target.value)} 
            required // Adding required field
          /><br />
          <button type="submit">LOGIN</button>
        </form>
        
        {/* Display the message here */}
        {message && (
          <div className={`message ${messageType}`}>{message}</div>
        )}
      </div>
      <div className="login-right">
        <img src="src/assets/PSA_company_image2.jpg" alt="Company img" />
      </div>
    </div>
  );
}

export default App;
