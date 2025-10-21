// frontend/src/components/LoadingSpinner.jsx
import React from 'react';
import './LoadingSpinner.css';

function LoadingSpinner({ message }) {
  return (
    <div className="loading-spinner-overlay">
      <div className="loading-spinner"></div>
      {message && <p className="loading-message">{message}</p>}
    </div>
  );
}

export default LoadingSpinner;