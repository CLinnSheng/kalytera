import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate, useNavigate } from 'react-router-dom';
import './App.css'; // For styling
import Recommendations from './Recommendations'; // Adjust the path as needed


function App() {

  //
  const [username, setUsername] = useState('');

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<LoginPage setUsername={setUsername}/>} /> {/* Changed component prop to element */}
          <Route path="/welcome" element={<WelcomePage username={username}/>} /> {/* Changed component prop to element */}
          <Route path="/recommendations" element={<Recommendations username={username} />} /> {/* Recommendations Page */}
          <Route path="*" element={<Navigate to="/" />} /> {/* Redirect to the login page if no route matches */}
        </Routes>
      </div>
    </Router>
  );
}

function LoginPage({setUsername}) {
  const navigate = useNavigate(); // Get navigate function
  //
  const [localUsername, setLocalUsername] = useState('');
  const [password, setPassword] = useState('')
  //

  const handleLogin = (event) => {
    event.preventDefault(); // Prevent form submission
    //
    setUsername(localUsername);
    //
    // Navigate to the welcome page using navigate
    navigate('/welcome'); // Use navigate instead of history.push
  };

  // return (
  //   <div className="login-container">
  //     <div className="login-left">
  //       <img src="src/assets/PSA_Logo.jpg" alt="PSA Logo" className="logo" />
  //       <h2>LOGIN</h2>
  //       <form onSubmit={handleLogin}>
  //         <input type="text" placeholder="Username" required /><br />
  //         <input type="password" placeholder="Password" required /><br />
  //         <button type="submit">Login</button>
  //       </form>
  //     </div>
  //     <div className="login-right">
  //       <img src="src/assets/PSA_company_image2.jpg" alt="Company img" />
  //     </div>
  //   </div>
  // );

  return (
    <div className="login-container">
      <div className="login-left">
        <img src="src/assets/PSA_Logo.jpg" alt="PSA Logo" className="logo" />
        <h2>LOGIN</h2>
        <form onSubmit={handleLogin}>
          <input 
            type="text" 
            placeholder="Username" 
            required 
            value={localUsername}
            onChange={(e) => setLocalUsername(e.target.value)}
          /><br />
          <input 
            type="password" 
            placeholder="Password" 
            required 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          /><br />
          <button type="submit">Login</button>
        </form>
      </div>
      <div className="login-right">
        <img src="src/assets/PSA_company_image2.jpg" alt="Company img" />
      </div>
    </div>
  );  
}

function WelcomePage({username}) {
  // Define your roles in an array
  const navigate = useNavigate();  // Initialize the hook

  //
  const [currentPosition, setCurrentPosition] = useState('');
  const [skills, setSkills] = useState('');
  const [desiredPosition, setDesiredPosition] = useState('');
  //

  const roles = [
    '-- Select position --',
    'Assistant Operations Executive (Depot Management)',
    'Operations Executive / Senior Operations Executive (Port Ecosystem)',
    'Senior Procurement Executive / Assistant Manager (Engineering Procurement)',
    'Manager / Deputy Manager (OT Security Governance & Compliance)',
    'Manager/Senior Manager (Commercial)',
    'Assistant Manager/Deputy Manager (Commercial)',
    'ITE Scholarship - Infocomm Technology Track',
    'Polytechnic Scholarship - Infocomm Technology Tack',
    'Management Executive (Shared Services)',
    'Deputy Manager (Port Ecosystem Commercial)',
    'Assistant Manager/Deputy Manager (Corporate & Direct Purchase)',
    'AI Analyst (Simulation)',
    'Procurement Assistant',
    'Assistant Manager/Deputy Manager (Depot Management)',
    'Deputy Manager / Manager (Automobile Terminal)',
    'Deputy Manager (Identity and Access Management)',
    'Civil Engineer (Tuas Construction Project Management)',
    'Lead High-Voltage Engineer',
    'Operations Supervisor (Depot Management)',
    'Management Executive/Deputy Management Executive',
    'ITE Scholarship – Operations Track',
    'Polytechnic Scholarship – Operations Track',
    'Polytechnic Scholarship - Engineering Track',
    'ITE Scholarship - Engineering Track',
    'Service Engineer (Digital Systems)',
    'Senior/Executive Service Engineer (M&E Services – Mechanical)',
    'Assistant/ Deputy Manager (Enterprise Risk & Resilience)',
    'Senior Service Engineer (Power Infrastructure)',
    'Senior Service Engineer (M&E Infrastructure)',
    'Assistant Management Executive / Deputy Management Executive (Payroll)',
    'Electrical Engineer (Power Infrastructure)',
    'Electrical Engineer (M&E Services)',
    'Executive Planner (Civil Engineering)',
    'Port+ Assistant (Warehouse Operations Assistant)',
    'Manager / Deputy Manager (Cybersecurity Incident Management)',
    'Assistant Port+ Executive (Warehouse/ Freight) [With Joining Bonus]',
    'Company Driver',
    'Global Management Associate',
    'Port+ Billing & Documentation Supervisor',
    'Principal/Senior Engineer (Battery Energy Storage System)',
    'Senior Engineer / Engineer (System)',
    'Container Handling Specialist (Prime Mover Driver)',
    'Technical Specialist (Digital Systems)- Card Repair Section [With Joining Bonus]',
    'Engineer (Autonomous Vehicle)',
    'Service Engineer (Equipment Engineering)',
    'Inventory Planner',
    'BIM Modeller',
    'Deputy Manager / Manager (Green Mobility)',
    'Deputy Manager (Sustainability)',
    'HSS Duty Manager',
    'Engineer (Smart System Solutions – Smart Engineering)',
    'Civil Engineer / Architect',
    'Operations Assistant (Tuas Customer Service Coordinator)',
    'Container Equipment Specialist (Yard Crane)',
    'Accounts Executive (Billing)',
    'Chemist',
    'Assistant Manager / Deputy Manager (IT Procurement)',
    'Assistant HR Executive / Deputy HR Executive (HR Excellence)',
    'Operations Supervisor (ChemCare)',
    'HR Recruitment Coordinator (6 months contract with possible extension/conversion)',
    'Data Engineer',
    'Systems Engineer / Assistant Manager / Deputy Manager (Systems)',
    'Operations Supervisor (Gate Operations)',
    'Senior Human Resource Executive (Staff Benefits)',
    'IT Technician',
    'Port+ Operations Operator (with warehouse forklift license / reach truck experience)',
    'Inventory Management Assistant',
    'Port+ Assistant (Warehouse Operations Assistant)',
    'Operations Supervisor (Yard Planning)',
    'Lashing Specialist',
    'Operations Executive',
    'Senior Manager (Business Development/M&A - SEA Indonesia)',
    'Emergency Response Specialist',
    'Container Handling Specialist (Prime Mover Driver)',
    'Inventory Planner',
    'Civil Technical Officer (Building Management)',
    'Dormitory Supervisor',
    'Undergraduate Scholarship - Infocomm Technology (ICT) Track',
    'Mechanical Engineer (M&E services)',
    'Technical Officer (Infrastructure Management)',
  ];
  
  // const handleNextClick = (event) => {
  //   event.preventDefault();  // Prevent form submission behavior
  //   navigate('/recommendations');  // Use the navigate function to go to recommendations page
  // };

  const handleNextClick = async (event) => {
    event.preventDefault();
    try {
      const response = await fetch('http://localhost:5000/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username,
          currentPosition,
          skills,
          desiredPosition,
        }),
      });
      if (response.ok) {
        navigate('/recommendations');
      } else {
        console.error('Failed to submit data');
      }
    } catch (error) {
      console.error('Error: ', error);
    }
  };

  // return (
  //   <div className="pagetwo-container">
  //     <div className="header">
  //       <h1>Welcome to Kalytera</h1>
  //       <img src="src/assets/PSA_Logo.jpg" alt="PSA Logo" className="logo" />
  //     </div>

  //     <form onSubmit={handleNextClick}>
  //       <h2>What is your current position?</h2>
  //       <select value={currentPosition} onChange={(e) => setCurrentPosition(e.target.value)}>
  //         {roles.map((role, index) => (
  //           <option key={index} value={role}>
  //             {role}
  //           </option>
  //         ))}
  //       </select>

  //       <h2>What are your current skills?</h2>
  //       <input
  //         type="text"
  //         placeholder="Enter your skills"
  //         value={skills}
  //         onChange={(e) => setSkills(e.target.value)}
  //       />

  //       <h2>What is your desired position?</h2>
  //       <select value={desiredPosition} onChange={(e) => setDesiredPosition(e.target.value)}>
  //         {roles.map((role, index) => (
  //           <option key={index} value={role}>
  //             {role}
  //           </option>
  //         ))}
  //       </select>

  //       <button type="submit">Next</button>
  //     </form>
  //   </div>
  // );

  return (
    <div className="pagetwo-container">
      <div className="header">
        <h1>Welcome to Kalytera</h1>
        <img src="src/assets/PSA_Logo.jpg" alt="PSA Logo" className="logo" />
      </div>

      <form onSubmit={handleNextClick}>
        <h2>What is your current position?</h2>
        <select value={currentPosition} onChange={(e) => setCurrentPosition(e.target.value)}>
          {roles.map((role, index) => (
            <option key={index} value={role}>
              {role}
            </option>
          ))}
        </select>

        <h2>What are your current skills?</h2>
        <input
          type="text"
          placeholder="Enter your skills"
          value={skills}
          onChange={(e) => setSkills(e.target.value)}
        />

        <h2>What is your desired position?</h2>
        <select value={desiredPosition} onChange={(e) => setDesiredPosition(e.target.value)}>
          {roles.map((role, index) => (
            <option key={index} value={role}>
              {role}
            </option>
          ))}
        </select>

        <button type="submit">Next</button>
      </form>
    </div>
  );

}


export default App;