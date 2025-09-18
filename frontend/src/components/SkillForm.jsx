import React from 'react';
import './SkillForm.css';

// The component now receives props from its parent (App.jsx)
function SkillForm({ skills, setSkills, jobTitle, setJobTitle, handleSubmit }) {
  return (
    <div className="form-container">
      <div className="input-group">
        <label htmlFor="skills">Your Skills (comma-separated)</label>
        <input
          type="text"
          id="skills"
          placeholder="e.g., Python, React, SQL"
          value={skills}
          onChange={(e) => setSkills(e.target.value)}
        />
      </div>
      <div className="input-group">
        <label htmlFor="job">Target Job</label>
        <input
          type="text"
          id="job"
          placeholder="e.g., Software Engineer"
          value={jobTitle}
          onChange={(e) => setJobTitle(e.target.value)}
        />
      </div>
      <button className="analyze-button" onClick={handleSubmit}>
        Analyze My Skills
      </button>
    </div>
  );
}

export default SkillForm;