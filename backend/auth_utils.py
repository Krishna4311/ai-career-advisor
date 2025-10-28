import firebase_admin
from firebase_admin import credentials, auth
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK initialized in auth_utils.")
    except Exception as e:
        print(f"!!! ERROR initializing Firebase Admin in auth_utils: {e} !!!")


bearer_scheme = HTTPBearer()

async def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """
    A dependency that verifies the Firebase ID token from the Authorization header
    and returns the user data.
    """
    if not firebase_admin._apps:
         raise HTTPException(
             status_code=500,
             detail="Firebase Admin SDK not initialized correctly."
         )

    token = creds.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )