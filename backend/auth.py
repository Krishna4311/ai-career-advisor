from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
import pyrebase

# --- Pydantic Models for Request Bodies ---
class UserCredentials(BaseModel):
    email: str
    password: str

# --- Firebase Configuration ---
# This config is for the CLIENT-side SDK wrapper (Pyrebase)
firebase_config = {
  "apiKey": "AIzaSyClm9wt5G8l6B1bzydl7dYzD97LttPngjQ",
  "authDomain": "pcsr-v2.firebaseapp.com",
  "projectId": "pcsr-v2",
  "storageBucket": "pcsr-v2.firebasestorage.app",
  "messagingSenderId": "200369475119",
  "appId": "1:200369475119:web:124e32f8485acab77800da",
  "databaseURL": "https://pcsr-v2-default-rtdb.firebaseio.com"
}

# Initialize Pyrebase (for user sign-in)
firebase = pyrebase.initialize_app(firebase_config)
auth_pyrebase = firebase.auth()

# Initialize Firebase Admin SDK (for custom token generation)
if not firebase_admin._apps:
    # This will use the serviceAccountKey.json file in the same directory
    cred = credentials.Certificate("serviceAccountKey.json") 
    firebase_admin.initialize_app(cred)

# Create a new router
router = APIRouter()

# --- Email/Password Endpoints ---
@router.post("/signup")
async def signup(credentials: UserCredentials):
    try:
        # 1. Create the user using the REST API wrapper
        user = auth_pyrebase.create_user_with_email_and_password(credentials.email, credentials.password)
        uid = user['localId']
        
        # 2. Generate a custom token for the new user using the Admin SDK
        custom_token = firebase_auth.create_custom_token(uid)
        
        return {"message": "User created successfully", "customToken": custom_token.decode('utf-8')}
    except Exception as e:
        # The error from pyrebase is generic, so we return a generic message
        raise HTTPException(status_code=400, detail=f"Could not create user. The email might already be in use. Error: {e}")

@router.post("/login")
async def login(credentials: UserCredentials):
    try:
        # 1. Authenticate the user with email and password
        user = auth_pyrebase.sign_in_with_email_and_password(credentials.email, credentials.password)
        uid = user['localId']
        
        # 2. If successful, create a custom token for that user's UID
        custom_token = firebase_auth.create_custom_token(uid)
        
        # 3. Return the custom token to the client
        return {"message": "Login successful", "customToken": custom_token.decode('utf-8')}
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid email or password. Error: {e}")
