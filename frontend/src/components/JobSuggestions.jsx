import React from 'react';
import './JobSuggestions.css';

function JobSuggestions({ suggestions, onAnalysis }) {

  // Create a sorted copy of the suggestions array
  const sortedSuggestions = [...suggestions].sort((a, b) => b.match_score - a.match_score);

  return (
    <div className="suggestions-container">
      <h2>Recommended Roles</h2>
      <ul className="suggestions-list">
        {sortedSuggestions.map((job) => (
          <li key={job.suggestion_id} className="suggestion-item">
            <div className="job-info">
              <span className="job-title">{job.job_title}</span>
              <span className="match-score">Match: {job.match_score}%</span>
            </div>
            <div className="feedback-buttons">
              {/* This button now triggers the new analysis workflow */}
              <button onClick={() => onAnalysis(job.job_title)} title="Analyze Skill Gap & Career Path">👍</button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default JobSuggestions;