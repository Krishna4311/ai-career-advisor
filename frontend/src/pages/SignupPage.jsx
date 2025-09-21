import React, { useRef } from 'react';
import { useAuth } from '../AuthContext';
import { useNavigate, Link } from 'react-router-dom';

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
    <div className="form-container">
      <h2>Sign Up</h2>
      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <label>Email</label>
          <input type="email" ref={emailRef} required />
        </div>
        <div className="input-group">
          <label>Password</label>
          <input type="password" ref={passwordRef} required />
        </div>
        <div className="input-group">
          <label>Password Confirmation</label>
          <input type="password" ref={passwordConfirmRef} required />
        </div>
        <button className="analyze-button" type="submit">Sign Up</button>
      </form>
      <div style={{ marginTop: '1rem' }}>
        Already have an account? <Link to="/login">Log In</Link>
      </div>
    </div>
  );
}
