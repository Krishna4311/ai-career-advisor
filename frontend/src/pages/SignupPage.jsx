import React, { useRef } from 'react';
import { useAuth } from '../AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import './SignupPage.css';

export default function SignupPage() {
  const emailRef = useRef();
  const passwordRef = useRef();
  const passwordConfirmRef = useRef();
  const { signup } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();

    if (passwordRef.current.value !== passwordConfirmRef.current.value) {
      return alert("Passwords do not match");
    }

    try {
      await signup(emailRef.current.value, passwordRef.current.value);
      navigate("/"); // Redirect to home on success
    } catch (error) {
      console.error(error);
      alert("Failed to create an account. The email may already be in use.");
    }
  }

  return (
    <div className="signup-container">
      <div className="signup-box">
        <h2>Sign Up</h2>
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <input type="email" ref={emailRef} required placeholder="Email" />
          </div>
          <div className="input-group">
            <input type="password" ref={passwordRef} required placeholder="Password" />
          </div>
          <div className="input-group">
            <input type="password" ref={passwordConfirmRef} required placeholder="Confirm Password" />
          </div>
          <button className="signup-button" type="submit">Sign Up</button>
        </form>
        <div className="login-link">
          Already have an account? <Link to="/login">Log In</Link>
        </div>
      </div>
    </div>
  );
}