// frontend/src/pages/LoginPage.jsx
import React, { useRef } from 'react';
import { useAuth } from '../AuthContext';
import { useNavigate, Link } from 'react-router-dom';

export default function LoginPage() {
  const emailRef = useRef();
  const passwordRef = useRef();
  const { login, googleLogin } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      await login(emailRef.current.value, passwordRef.current.value);
      navigate("/");
    } catch {
      alert("Failed to log in. Please check your email and password.");
    }
  }

  async function handleGoogleSignIn() {
    try {
      await googleLogin();
      navigate("/"); 
    } catch (error) {
      console.error("Google sign-in error:", error);
      alert(error.message);
    }
  }

  return (
    <div className="form-container">
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <label>Email</label>
          <input type="email" ref={emailRef} required />
        </div>
        <div className="input-group">
          <label>Password</label>
          <input type="password" ref={passwordRef} required />
        </div>
        <button className="analyze-button" type="submit">Log In</button>
      </form>

      <button
        className="secondary-button"
        onClick={handleGoogleSignIn}
        style={{ width: '100%', maxWidth: '400px', marginTop: '1rem' }}
      >
        Sign In with Google
      </button>

      <div style={{ marginTop: '1rem' }}>
        Need an account? <Link to="/signup">Sign Up</Link>
      </div>
    </div>
  );
}