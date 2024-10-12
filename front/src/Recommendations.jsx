import React from "react";
import './Recommendations.css';  // Import CSS for styling
import Avatar from './assets/avatar.png'; // Import your image

export default function Recommendations(){
    const username = localStorage.getItem('username');
    const currentPosition = localStorage.getItem('currentPosition');

    return (
        <div className="container">

            <div className="recommendations-header">
                <img src={Avatar} alt="avatar" className="avatar" />
                <div className="sentence">
                    <span className="welcome-text">Welcome {username}!</span>
                    <div className="current-position">
                        {currentPosition === '-- Select position --' ? '' : currentPosition}
                    </div>
                </div>
            </div>

            <div className="input-container">
                <p>INSERT TEXT HERE</p> 
            </div>
        </div>
    );
}