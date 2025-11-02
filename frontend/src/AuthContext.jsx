import React, { createContext, useState, useContext, useEffect } from 'react';
import { auth, provider } from './firebase';
import {
  onAuthStateChanged,
  signOut,
  signInWithCustomToken,
  signInWithEmailAndPassword,
  signInWithPopup
} from 'firebase/auth';
import { API_URL } from "./api/config";

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  async function signup(email, password) {
    const response = await fetch(`${API_URL}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to sign up.");
    }

    const data = await response.json();

    return signInWithCustomToken(auth, data.customToken);
  }

  async function login(email, password) {
    return signInWithEmailAndPassword(auth, email, password);
  }

  async function googleLogin() {
    try {
      // 1. Sign in with Google on the client
      const result = await signInWithPopup(auth, provider);
      const user = result.user;
      const idToken = await user.getIdToken();

      // 2. Verify token with our backend
      const response = await fetch(`${API_URL}/auth/google-login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ idToken }),
      });

      if (!response.ok) {
        await signOut(auth);
        throw new Error('Backend verification failed.');
      }

      const data = await response.json();
      
      return signInWithCustomToken(auth, data.customToken);

    } catch (error) {
      console.error("Google sign-in error:", error);
      throw new Error("Failed to sign in with Google.");
    }
  }

  function logout() {
    return signOut(auth);
  }

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, user => {
      setCurrentUser(user);
      setLoading(false);
    });
    return unsubscribe;
  }, []);

  const value = { currentUser, signup, login, googleLogin, logout, loading };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}