import React from 'react';
import { Link } from 'react-router-dom';
import './HomePage.css';

function HomePage() {
  return (
    <div className="hero">
      <h1>Start building your tomorrow, today</h1>
      <p>Whether you're all-in on AI, just want to brush up on the latest, or you're here to skill up your team—welcome to Google Cloud Skills Boost.</p>
      <Link to="/signup" className="cta-button">Get started</Link>
    </div>
  );
}

export default HomePage;