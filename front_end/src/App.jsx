import React from 'react';
import './App.css'; // For styling

function App() {
  return (
    <div className="App">
      <LoginPage />
    </div>
  );
}

function LoginPage() {
  return (
    <div className="login-container">
      <div className="login-left">
        <img src="src/assets/PSA_Logo.jpg" alt="PSA Logo" className="logo" />
        <h2>LOGIN</h2>
        <form>
          <input type="text" placeholder="COMPANY EMAIL" /><br />
          <input type="Password" placeholder="PASSWORD" /><br />
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
