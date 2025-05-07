from fastapi import Depends, HTTPException, Request
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

GOOGLE_CLIENT_ID = "532104143303-07qs7nvu5247ldae6u5bj7gp1ovgi6f3.apps.googleusercontent.com"

def verify_token(token: str):
    try:
        # Verify the token with Google's public keys
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)

        # Check if the token is issued to your app
        if idinfo['aud'] != GOOGLE_CLIENT_ID:
            raise ValueError('Could not verify audience.')

        # (Optional) Check if email is verified
        if not idinfo.get("email_verified"):
            raise ValueError("Email not verified.")

        return idinfo  # Contains user's info (email, sub, name, etc.)
    
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
