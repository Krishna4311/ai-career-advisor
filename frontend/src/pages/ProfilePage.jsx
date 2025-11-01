import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import LoadingSpinner from '../components/LoadingSpinner'; 
import CareerPathDisplay from '../components/CareerPathDisplay'; 
import { API_URL } from "../api/config"; 

function ProfilePage() {
  const { currentUser } = useAuth();
  const [savedPaths, setSavedPaths] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSavedPaths = async () => {
      if (!currentUser) return;

      setIsLoading(true);
      setError(null);
      try {
        const token = await currentUser.getIdToken();
        const response = await fetch(`${API_URL}/api/my-paths`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        if (!response.ok) throw new Error("Failed to load saved paths.");

        const data = await response.json();
        setSavedPaths(data.paths || []);

      } catch (err) {
        setError(err.message);
        console.error("Error fetching paths:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSavedPaths();
  }, [currentUser]);

  return (
    <div className="profile-page">
      <h2>My Saved Career Paths</h2>
      {isLoading && <LoadingSpinner message="Loading paths..." />}
      {error && <p className="error-message">{error}</p>}

      {!isLoading && !error && savedPaths.length === 0 && (
        <p>You haven't saved any career paths yet.</p>
      )}

      {!isLoading && !error && savedPaths.length > 0 && (
        <div className="saved-paths-list">
          {savedPaths.map((path, index) => (
            <CareerPathDisplay
              key={path.userId + index}
              pathData={path.path_data}
              targetJob={path.target_job}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default ProfilePage;