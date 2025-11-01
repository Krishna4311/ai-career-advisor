from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import firebase_admin
from firebase_admin import auth
from firebase_admin.auth import EmailAlreadyExistsError, InvalidIdTokenError, UserNotFoundError

# --- Pydantic Models for Request Bodies ---
class UserCredentials(BaseModel):
    email: str
    password: str

router = APIRouter()

# --- Email/Password Endpoint ---
@router.post("/signup")
async def signup(credentials: UserCredentials):
    """
    Handles new user creation.
    Uses the Firebase Admin SDK to create a user, then mints a
    custom token for them to be signed in on the client.
    """
    try:
        user = auth.create_user(
            email=credentials.email,
            password=credentials.password
        )
        
        custom_token = auth.create_custom_token(user.uid)
        
        return {"customToken": custom_token.decode('utf-8')}

    except EmailAlreadyExistsError:
        raise HTTPException(status_code=400, detail="Email already in use.")
    except Exception as e:
        print(f"Error during admin signup: {e}")
        raise HTTPException(status_code=500, detail="Could not create user.")


class GoogleToken(BaseModel):
    idToken: str

@router.post("/google-login")
async def google_login(token: GoogleToken):
    """
    Handles Google Sign-In.
    Verifies the Google ID token and mints a custom token.
    """
    try:
        decoded_token = auth.verify_id_token(token.idToken)
        uid = decoded_token['uid']
        
        try:
            auth.get_user(uid)
        except UserNotFoundError:
            raise HTTPException(status_code=404, detail="User not found in Firebase.")

        custom_token = auth.create_custom_token(uid)
        
        return {"customToken": custom_token.decode('utf-8')}

    except InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid Google ID token.")
    except Exception as e:
        print(f"Error during Google login: {e}")
        raise HTTPException(status_code=500, detail="Could not process Google login.")