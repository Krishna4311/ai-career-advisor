import React, { useRef } from 'react';
import { useAuth } from '../AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { auth, provider } from '../firebase'; // Firebase setup
import { signInWithPopup } from 'firebase/auth';
import './LoginPage.css';

export default function LoginPage() {
  const emailRef = useRef();
  const passwordRef = useRef();
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      await login(emailRef.current.value, passwordRef.current.value);
      navigate("/"); // Redirect to home on success
    } catch {
      alert("Failed to log in. Please check your email and password.");
    }
  }

  async function handleGoogleSignIn() {
    try {
      await signInWithPopup(auth, provider);
      navigate("/"); // Redirect to home after login
    } catch (error) {
      console.error("Google sign-in error:", error);
      alert("Failed to sign in with Google.");
    }
  }

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>Login</h2>
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <input type="email" ref={emailRef} required placeholder="Email" />
          </div>
          <div className="input-group">
            <input type="password" ref={passwordRef} required placeholder="Password" />
          </div>
          <button className="login-button" type="submit">Log In</button>
        </form>
        <button className="google-login-button" onClick={handleGoogleSignIn}>Sign in with Google</button>
        <div className="signup-link">
          Need an account? <Link to="/signup">Sign Up</Link>
        </div>
      </div>
    </div>
  );
}