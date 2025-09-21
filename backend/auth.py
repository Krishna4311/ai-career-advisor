import pyrebase
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials

# --- Pydantic Models for Request Bodies ---
class UserCredentials(BaseModel):
    email: str
    password: str

class GoogleTokenRequest(BaseModel):
    idToken: str

# --- Firebase Configuration for Pyrebase ---
firebase_config = {
  "apiKey": "AIzaSyClm9wt5G8l6B1bzydl7dYzD97LttPngjQ",
  "authDomain": "pcsr-v2.firebaseapp.com",
  "projectId": "pcsr-v2",
  "storageBucket": "pcsr-v2.firebasestorage.app",
  "messagingSenderId": "200369475119",
  "appId": "1:200369475119:web:124e32f8485acab77800da",
  "measurementId": "G-JG7H5V6143",
  "databaseURL": "https://pcsr-v2-default-rtdb.firebaseio.com"
}

# Initialize Pyrebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# Initialize Firebase Admin SDK (for verifying ID tokens)
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

# Create a new router
router = APIRouter()

# --- Email/Password Endpoints ---
@router.post("/signup")
async def signup(credentials: UserCredentials):
    try:
        user = auth.create_user_with_email_and_password(credentials.email, credentials.password)
        return {"message": "User created successfully", "userId": user['localId']}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Could not create user. The email might already be in use.")

@router.post("/login")
async def login(credentials: UserCredentials):
    try:
        user = auth.sign_in_with_email_and_password(credentials.email, credentials.password)
        return {"message": "Login successful", "idToken": user['idToken']}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid email or password")

# --- Google Sign-In Endpoint ---
@router.post("/google-login")
async def google_login(token_request: GoogleTokenRequest):
    """
    Verify Google ID token and return user info.
    """
    try:
        decoded_token = firebase_auth.verify_id_token(token_request.idToken)
        uid = decoded_token.get("uid")
        email = decoded_token.get("email")
        return {"status": "success", "uid": uid, "email": email}
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")