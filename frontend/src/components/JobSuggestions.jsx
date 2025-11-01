import React, { useState } from 'react';
import { useAuth } from '../AuthContext'; // Import useAuth to get the user
import { API_URL } from '../api/config';   // Import API_URL
import './JobSuggestions.css';

function JobSuggestions({ v2Result, onAnalysis }) {
  // Destructure from v2Result as it comes from HomePage
  const { suggestions, parsed_skills } = v2Result;
  const { currentUser } = useAuth(); // Get the current user
  const [feedbackSent, setFeedbackSent] = useState({});
  const sortedSuggestions = [...(suggestions || [])].sort((a, b) => b.match_score - a.match_score);
  const handleFeedback = async (suggestion, rating) => {
    if (!currentUser) {
      alert("Please log in to submit feedback.");
      return;
    }

    if (feedbackSent[suggestion.suggestion_id]) return;

    try {
      const token = await currentUser.getIdToken();
      const response = await fetch(`${API_URL}/api/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          suggestion_id: suggestion.suggestion_id,
          job_title: suggestion.job_title,
          rating: rating
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send feedback.');
      }

      setFeedbackSent(prev => ({ ...prev, [suggestion.suggestion_id]: true }));
      console.log(`Feedback sent for ${suggestion.job_title}: ${rating}`);

    } catch (error) {
      alert(`Error sending feedback: ${error.message}`);
    }
  };

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

              {/* Check if feedback has been sent */}
              {feedbackSent[job.suggestion_id] ? (
                <span>Thanks!</span>
              ) : (
                <>
                  {/* Feedback Button: Helpful */}
                  <button
                    onClick={() => handleFeedback(job, 'helpful')}
                    title="Helpful">👍
                  </button>
                  {/* Feedback Button: Not Helpful */}
                  <button
                    onClick={() => handleFeedback(job, 'not_helpful')}
                    title="Not Helpful">👎
                  </button>
                </>
              )}

              {/* Analysis Button */}
              <button
                className="analyze-path-button"
                onClick={() => onAnalysis(job.job_title, parsed_skills)}
                title="Analyze Skill Gap & Career Path">
                Analyze Path
              </button>

            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default JobSuggestions;