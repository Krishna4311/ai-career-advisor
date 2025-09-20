import React from 'react';
import './Tabs.css';

function Tabs({ activeTab, setActiveTab }) {
  return (
    <div className="tabs-container">
      <button
        className={`tab-button ${activeTab === 'gapAnalysis' ? 'active' : ''}`}
        onClick={() => setActiveTab('gapAnalysis')}
      >
        Skill Gap Analysis
      </button>
      <button
        className={`tab-button ${activeTab === 'jobSuggestions' ? 'active' : ''}`}
        onClick={() => setActiveTab('jobSuggestions')}
      >
        Job Suggestions
      </button>
    </div>
  );
}

export default Tabs;