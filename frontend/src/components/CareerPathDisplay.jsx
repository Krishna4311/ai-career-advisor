import React from 'react';
import { useAuth } from '../AuthContext'; 
import './CareerPathDisplay.css';
import { API_URL } from "../api/config";

function CareerPathDisplay({ pathData, targetJob }) {
  const { currentUser } = useAuth();

  const handleSavePath = async () => {
    if (!currentUser) {
      alert("Please log in to save your path.");
      return;
    }

    try {
      const token = await currentUser.getIdToken(); 

      const response = await fetch(`${API_URL}/api/save-path`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify({
          target_job: targetJob,
          path_data: pathData, 
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to save the path. Please try again.");
      }

      alert('Path saved successfully!');

    } catch (error) {
      console.error("Failed to save path:", error);
      alert(`Failed to save path: ${error.message}`);
    }
  };

  return (
    <div className="path-container">
      <div className="path-header">
        <h2>Your Generated Career Path to "{targetJob}"</h2>
        {currentUser && (
          <button className="save-button" onClick={handleSavePath}>
            Save this Path
          </button>
        )}
      </div>
      <div className="path-columns">
        <div className="path-column">
          <h3>Next Skills to Learn</h3>
          <ul>
            {(pathData?.next_skills || []).map((skill, index) => <li key={index}>{skill}</li>)}
          </ul>
        </div>
        <div className="path-column">
          <h3>Career Milestones</h3>
          <ul>
            {(pathData?.milestones || []).map((milestone, index) => <li key={index}>{milestone}</li>)}
          </ul>
        </div>
        <div className="path-column">
          <h3>Recommended Actions</h3>
          <ul>
            {(pathData?.recommended_actions || []).map((action, index) => <li key={index}>{action}</li>)}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default CareerPathDisplay;