import React, { useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import Footer from './components/Footer';
import Navigation from './components/Navigation'; // <-- Import Navigation
import SavedPathsSidebar from './components/SavedPathsSidebar'; // <-- Import Sidebar
import './App.css';

// ProtectedRoute component to guard routes
function ProtectedRoute({ children }) {
  const { currentUser, loading } = useAuth();

  if (loading) {
    // You can return a loading spinner here if you want
    return <div className="loading-container"><p>Loading...</p></div>;
  }

  if (!currentUser) {
    return <Navigate to="/login" />;
  }

  return children;
}

function App() {
  // State for controlling the sidebar
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="app-container">
      <header className="app-header">
        {/* Pass the function to open the sidebar as a prop */}
        <Navigation onOpenSidebar={() => setIsSidebarOpen(true)} />
      </header>
      
      <main className="app-main">
        <Routes>
          <Route 
            path="/" 
            element={
              <ProtectedRoute>
                <HomePage />
              </ProtectedRoute>
            } 
          />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          {/* The /profile route is no longer needed */}
        </Routes>
      </main>
      <Footer />
      
      {/* Render the sidebar component */}
      <SavedPathsSidebar 
        isOpen={isSidebarOpen} 
        onClose={() => setIsSidebarOpen(false)} 
      />
    </div>
  );
}

export default App;
