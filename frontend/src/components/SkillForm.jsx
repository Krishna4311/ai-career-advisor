import React from 'react';
import './SkillForm.css'; // You should already have this CSS file

function SkillForm({ skills, setSkills, jobTitle, setJobTitle, onSubmit }) {
  return (
    <form className="form-container" onSubmit={onSubmit}>
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
      <button type="submit" className="analyze-button">
        Analyze My Skills
      </button>
    </form>
  );
}

export default SkillForm;