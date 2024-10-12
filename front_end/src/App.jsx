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

  const handleSubmit = (e) => {
    e.preventDefault(); // Prevent page reload on form submission
    // Send the email and password to the backend
    fetch('http://127.0.0.1:5000/login', {  // Updated to include '/login'
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    })
      .then(response => response.json())
      .then(data => {
        console.log('Success:', data);
        // You can handle success (e.g., redirect or show a message)
      })
      .catch((error) => {
        console.error('Error:', error);
        // You can handle error (e.g., display an error message)
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
          /><br />
          <input
            type="password"
            placeholder="PASSWORD"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          /><br />
          <button type="submit">LOGIN</button>
        </form>
      </div>
      <div className="login-right">
        <img src="src/assets/PSA_company_image2.jpg" alt="Company img" />
      </div>
    </div>
  );
}

export default App;