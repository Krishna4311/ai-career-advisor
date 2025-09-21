import React, { useRef } from 'react';
import { useAuth } from '../AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { auth, provider } from '../firebase'; // Firebase setup
import { signInWithPopup } from 'firebase/auth';

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
      const result = await signInWithPopup(auth, provider);
      const user = result.user;
      const idToken = await user.getIdToken(); // Firebase ID token

      // Send ID token to backend for verification
      const response = await fetch("/auth/google-login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ idToken }),
      });

      const data = await response.json();
      console.log("Backend verified user:", data);

      navigate("/"); // Redirect to home after login
    } catch (error) {
      console.error("Google sign-in error:", error);
      alert("Failed to sign in with Google.");
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

      <div style={{ marginTop: '1rem' }}>
        <button
          className="analyze-button"
          style={{ marginTop: '1rem', backgroundColor: "#4285F4", color: "white" }}
          onClick={handleGoogleSignIn}
        >
          Sign in with Google
        </button>
      </div>

      <div style={{ marginTop: '1rem' }}>
        Need an account? <Link to="/signup">Sign Up</Link>
      </div>
    </div>
  );
}
