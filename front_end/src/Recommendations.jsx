import React from "react";
import './Recommendations.css';  // Import CSS for styling
import Avatar from './assets/avatar.png'; // Import your image

export default function Recommendations(){
    // const username = 'xxxx';  // Replace with actual username logic

    return (
        <div className="container">

            <div className="recommendations-header">
                <img src={Avatar} alt="avatar" className="avatar" />
                <div className = "welcome-text">
                <span className="welcome-text">Welcome, Karen</span>
                <div className="current-position">IT Manager</div>
                </div>
            </div>

            <div className="input-container">
                <p>INSERT TEXT HERE</p> 
            </div>
        </div>
    );
}