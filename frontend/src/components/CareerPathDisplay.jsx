import React from 'react';
import './CareerPathDisplay.css';

function CareerPathDisplay({ pathData, targetJob }) {
  return (
    <div className="path-container">
      <div className="path-header">
        <h2>Your Generated Career Path to "{targetJob}"</h2>
      </div>
      <div className="path-columns">
        <div className="path-column">
          <h3>Next Skills to Learn </h3>
          <ul>
            {pathData.next_skills?.map((skill, index) => <li key={index}>{skill}</li>)}
          </ul>
        </div>
        <div className="path-column">
          <h3>Career Milestones </h3>
          <ul>
            {pathData.milestones?.map((milestone, index) => <li key={index}>{milestone}</li>)}
          </ul>
        </div>
        <div className="path-column">
          <h3>Recommended Actions </h3>
          <ul>
            {pathData.recommended_actions?.map((action, index) => <li key={index}>{action}</li>)}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default CareerPathDisplay;
