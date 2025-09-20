import React from 'react';
import './JobSuggestions.css';

function JobSuggestions({ suggestions, apiUrl }) {
  const handleFeedback = async (suggestion, rating) => {
    // This is a simple feedback handler. In a real app, you'd get the user_id from a login.
    const feedbackData = {
      suggestion_id: suggestion.suggestion_id,
      job_title: suggestion.job_title,
      user_id: "demo_user_123", // Placeholder user ID
      rating: rating,
    };
    try {
      await fetch(`${apiUrl}/api/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(feedbackData),
      });
      // You could add a visual cue here to show feedback was sent
      alert("Thanks for your feedback!"); 
    } catch (error) {
      console.error("Failed to send feedback:", error);
    }
  };

  if (!suggestions || suggestions.length === 0) {
    return <p>No job suggestions found.</p>;
  }

  return (
    <div className="suggestions-container">
      <h2>Recommended Roles</h2>
      <ul className="suggestions-list">
        {suggestions.map((job) => (
          <li key={job.suggestion_id} className="suggestion-item">
            <div className="job-info">
              <span className="job-title">{job.job_title}</span>
              <span className="match-score">Match: {job.match_score}%</span>
            </div>
            <div className="feedback-buttons">
              <button onClick={() => handleFeedback(job, 'helpful')}>👍</button>
              <button onClick={() => handleFeedback(job, 'not_helpful')}>👎</button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default JobSuggestions;