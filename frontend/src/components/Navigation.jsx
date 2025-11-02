import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';

// We now accept onOpenSidebar as a prop
function Navigation({ onOpenSidebar }) {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login'); // Redirect to login after logout
    } catch {
      alert("Failed to log out.");
    }
  };

  return (
    <nav className="main-nav">
      <Link to="/" className="nav-logo">Career Craft</Link>
      <div className="nav-links">
        {currentUser ? (
          <>
            {/* --- THIS IS THE NEW BUTTON --- */}
            <button onClick={onOpenSidebar} className="nav-button">
              Saved Paths
            </button>
            {/* --- END OF NEW BUTTON --- */}

            <span className="user-email">{currentUser.email}</span>
            <button onClick={handleLogout} className="nav-button">Logout</button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/signup">Sign Up</Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navigation;
