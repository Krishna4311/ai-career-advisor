from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pyrebase
from dotenv import load_dotenv
import os

# --- Load Firebase Config from .env ---
load_dotenv() # Make sure this is called to load variables

FB_API_KEY = os.getenv("FB_API_KEY")
FB_AUTH_DOMAIN=os.getenv("FB_AUTH_DOMAIN")
FB_PROJECT_ID=os.getenv("FB_PROJECT_ID")
FB_STORAGE_BUCKET=os.getenv("FB_STORAGE_BUCKET")
FB_MESSAGIN_SENDER_ID=os.getenv("FB_MESSAGIN_SENDER_ID") # Check spelling: MESSAGING_SENDER_ID
FB_APP_ID=os.getenv("FB_APP_ID")

# --- Pydantic Models for Request Bodies ---
class UserCredentials(BaseModel):
    email: str
    password: str

# --- Firebase Configuration ---
firebase_config = {
  "apiKey": FB_API_KEY,
  "authDomain": FB_AUTH_DOMAIN,
  "projectId": FB_PROJECT_ID,
  "storageBucket": FB_STORAGE_BUCKET,
  "messagingSenderId": FB_MESSAGIN_SENDER_ID, # Check spelling if needed
  "appId": FB_APP_ID,
  "databaseURL": "" # Usually empty
}

# --- Initialize Pyrebase ---
# Check if config values are loaded correctly
if not all([FB_API_KEY, FB_AUTH_DOMAIN, FB_PROJECT_ID]):
    raise ValueError("Firebase configuration environment variables are missing!")

firebase = pyrebase.initialize_app(firebase_config)
auth_pyrebase = firebase.auth()

# Create a new router
router = APIRouter()

# --- Standard Email/Password Endpoints ---
@router.post("/signup")
async def signup(credentials: UserCredentials):
    try:
        # Create the user using Pyrebase
        auth_pyrebase.create_user_with_email_and_password(credentials.email, credentials.password)
        
        # Immediately sign the user in to get the standard ID Token
        user = auth_pyrebase.sign_in_with_email_and_password(credentials.email, credentials.password)
        
        # Return the standard idToken
        return {"message": "User created successfully", "idToken": user['idToken']}
    except Exception as e:
        # Try to provide a more specific error if possible
        error_message = str(e)
        if "EMAIL_EXISTS" in error_message:
            detail = "Email already in use."
        else:
            detail = "Could not create user."
        raise HTTPException(status_code=400, detail=detail)

@router.post("/login")
async def login(credentials: UserCredentials):
    try:
        # Sign in the user using Pyrebase
        user = auth_pyrebase.sign_in_with_email_and_password(credentials.email, credentials.password)
        
        # Return the standard idToken
        return {"message": "Login successful", "idToken": user['idToken']}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid email or password.")