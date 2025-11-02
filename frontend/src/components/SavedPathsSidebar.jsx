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

  const handleDeletePath = async (pathId) => {
    if (!currentUser || !pathId) return;

    if (!window.confirm("Are you sure you want to delete this career path? This action cannot be undone.")) {
      return;
    }

    try {
      const token = await currentUser.getIdToken();
      const response = await fetch(`${API_URL}/api/my-paths/${pathId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Failed to delete path.");
      }

      // On success, update UI
      setSavedPaths(prevPaths => prevPaths.filter(p => p.path_id !== pathId));
      handleReturnToList(); // Go back to the list

    } catch (err) {
      console.error("Delete path error:", err);
      setError(err.message); // Show error in the sidebar
    }
  };

  if (!isOpen) return null;

  return (
    <div className="sidebar-overlay" onClick={onClose}>
      <div className="sidebar-content" onClick={(e) => e.stopPropagation()}>
        <button className="sidebar-close-button" onClick={onClose}>&times;</button>

        {selectedPath ? (
          <div className="sidebar-fullscreen-view">
            {/* --- MODIFICATION 2: Add header container --- */}
            <div className="sidebar-view-header">
              <button className="sidebar-return-button" onClick={handleReturnToList}>
                &larr; Return to List
              </button>
              {/* --- MODIFICATION 3: Add Delete Button --- */}
              <button
                className="sidebar-delete-button"
                onClick={() => handleDeletePath(selectedPath.path_id)}
              >
                Delete Path
              </button>
            </div>

            <CareerPathDisplay
              pathData={selectedPath.path_data}
              targetJob={selectedPath.target_job}
              showSaveButton={false} // <-- MODIFICATION 4: Hide save button
            />
          </div>
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
                {savedPaths.map((path) => (
                  <li
                    key={path.path_id} // <-- MODIFICATION 5: Use path_id as key
                    className="saved-path-item"
                    onClick={() => handleSelectPath(path)}
                  >
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