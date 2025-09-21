// src/firebase.js
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyClm9wt5G8l6B1bzydl7dYzD97LttPngjQ",
  authDomain: "pcsr-v2.firebaseapp.com",
  projectId: "pcsr-v2",
  storageBucket: "pcsr-v2.firebasestorage.app",
  messagingSenderId: "200369475119",
  appId: "1:200369475119:web:124e32f8485acab77800da",
  measurementId: "G-JG7H5V6143",
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

export { auth, provider };
