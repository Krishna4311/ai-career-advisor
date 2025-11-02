// frontend/src/components/SavedPathsSidebar.jsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { API_URL } from '../api/config';
import LoadingSpinner from './LoadingSpinner';
import CareerPathDisplay from './CareerPathDisplay';
import './SavedPathsSidebar.css';

function SavedPathsSidebar({ isOpen, onClose }) {
  const { currentUser } = useAuth();
  const [savedPaths, setSavedPaths] = useState([]);
  const [selectedPath, setSelectedPath] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch paths only when the sidebar is opened
    if (isOpen && currentUser) {
      const fetchSavedPaths = async () => {
        setIsLoading(true);
        setError(null);
        setSelectedPath(null); // Reset view on open
        try {
          const token = await currentUser.getIdToken();
          const response = await fetch(`${API_URL}/api/my-paths`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          if (!response.ok) throw new Error("Failed to load saved paths.");
          const data = await response.json();
          setSavedPaths(data.paths || []);
        } catch (err) {
          setError(err.message);
        } finally {
          setIsLoading(false);
        }
      };
      fetchSavedPaths();
    }
  }, [isOpen, currentUser]); // Re-run effect if isOpen changes

  const handleSelectPath = (path) => {
    setSelectedPath(path);
  };

  const handleReturnToList = () => {
    setSelectedPath(null);
  };

  // Don't render anything if not open
  if (!isOpen) return null;

  return (
    // Overlay covers the whole screen
    <div className="sidebar-overlay" onClick={onClose}>
      {/* Content stops click propagation */}
      <div className="sidebar-content" onClick={(e) => e.stopPropagation()}>
        <button className="sidebar-close-button" onClick={onClose}>&times;</button>
        
        {/* VIEW 1: Full Screen Path Display */}
        {selectedPath ? (
          <div className="sidebar-fullscreen-view">
            <button className="sidebar-return-button" onClick={handleReturnToList}>
              &larr; Return to List
            </button>
            {/* We re-use the component you already built */}
            <CareerPathDisplay 
              pathData={selectedPath.path_data} 
              targetJob={selectedPath.target_job} 
            />
          </div>
        
        /* VIEW 2: List of Saved Paths */
        ) : (
          <div className="sidebar-list-view">
            <h2>My Saved Paths</h2>
            {isLoading && <LoadingSpinner message="Loading..." />}
            {error && <p className="error-message">{error}</p>}
            
            {!isLoading && !error && savedPaths.length === 0 && (
              <p>You haven't saved any career paths yet.</p>
            )}

            {!isLoading && !error && savedPaths.length > 0 && (
              <ul className="saved-paths-list">
                {savedPaths.map((path, index) => (
                  // We need to handle potential missing data safely
                  <li key={index} className="saved-path-item" onClick={() => handleSelectPath(path)}>
                    <span className="saved-path-job">{path.target_job || 'Saved Path'}</span>
                    <span className="saved-path-skills">
                      {(path.path_data?.next_skills || []).slice(0, 3).join(', ') + '...'}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default SavedPathsSidebar;
