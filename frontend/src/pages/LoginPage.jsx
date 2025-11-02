import React, { useRef } from 'react';
import { useAuth } from '../AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { auth, provider } from '../firebase'; 
import { signInWithPopup } from 'firebase/auth';
import { API_URL } from '../api/config'; 

export default function LoginPage() {
  const emailRef = useRef();
  const passwordRef = useRef();
  const { login } = useAuth();
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
      const result = await signInWithPopup(auth, provider);
      const user = result.user;
      const idToken = await user.getIdToken(); 

      const response = await fetch(`${API_URL}/auth/google-login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ idToken }),
      });

      if (!response.ok) throw new Error('Backend verification failed.');
      
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