import React from 'react';
import './SkillGapResults.css';

function SkillGapResults({ result }) {
  return (
    <div className="results-container">
      <h2>Analysis Complete</h2>
      <div className="skills-columns">
        <div className="skills-column">
          <h3>Matching Skills</h3>
          <ul>
            {result.matching_skills?.map((skill, index) => <li key={index}>{skill}</li>)}
          </ul>
        </div>
        <div className="skills-column">
          <h3>Missing Skills</h3>
          <ul>
            {result.missing_skills?.map((skill, index) => <li key={index}>{skill}</li>)}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default SkillGapResults;