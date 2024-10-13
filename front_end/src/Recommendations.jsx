import React, { useState, useEffect } from "react";
import './Recommendations.css';  // Import CSS for styling
import Avatar from './assets/avatar.png'; // Import your image

export default function Recommendations({username}){
    // const username = 'xxxx';  // Replace with actual username logic

    //
    const [userData, setUserData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    useEffect(() => {
        const fetchUserData = async () => {
          try {
            const response = await fetch(`http://localhost:5000/get_data?username=${username}`);
            if (!response.ok) {
              throw new Error('Failed to fetch user data');
            }
            const data = await response.json();
            setUserData(data[0]); // Assuming we're only displaying one user's data
            setLoading(false);
          } catch (err) {
            setError(err.message);
            setLoading(false);
          }
        };
    
        if (username) {
          fetchUserData();
        } else {
          setError('No username provided');
          setLoading(false);
        }
      }, [username]);
    
      if (loading) return <div className="container">Loading...</div>;
      if (error) return <div className="container">Error: {error}</div>;
      if (!userData) return <div className="container">No data found for this user.</div>;
    //

    return (
        <div className="container">

            <div className="recommendations-header">
                <img src={Avatar} alt="avatar" className="avatar" />
                <div className = "welcome-text">
                <span className="welcome-text">Welcome, {userData.username}</span>
                <div className="current-position">{userData.current_position}</div>
                </div>
            </div>

            <div className="input-container">
                <h2>Your Information:</h2>
                    <p><strong>Skills:</strong> {userData.skills}</p>
                    <p><strong>Desired Position:</strong> {userData.desired_position}</p>
                    <p><strong>Advices:</strong> {userData.ai_response}</p>
            </div>
        </div>
    );
}