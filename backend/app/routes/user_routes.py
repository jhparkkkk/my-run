from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
# from app import dependencies, services
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User

import os
import requests

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/signup")
def signup():
    client_id = os.getenv("STRAVA_CLIENT_ID")
    redirect_uri = os.getenv("STRAVA_REDIRECT_URI")
    scope = "read,activity:read"
    auth_url = f"http://www.strava.com/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&approval_prompt=force&scope=read"
    print(f"authentication url: {auth_url}")
    return RedirectResponse(auth_url)

@router.get("/callback")
def strava_callback(code: str, db: Session = Depends(get_db)):
    print('----------- strava_callback --------------')
    token_url = "https://www.strava.com/oauth/token"
    data = {
        'client_id': os.getenv("STRAVA_CLIENT_ID"),
        'client_secret': os.getenv("STRAVA_CLIENT_SECRET"),
        'code': code,
        'grant_type': 'authorization_code'
    }
    response = requests.post(token_url, data=data).json()

    print(response)
    
    access_token = response.get('access_token')
    strava_id = response.get('athlete', {}).get('id')
    refresh_token = response.get('refresh_token')
    expires_at = response.get('expires_at')

    print(f'strava_callback: retrieve access token {access_token}')
    print(f"strava id: {strava_id}")

    if not access_token:
        raise HTTPException(status_code=400, detail="Strava authentication failed.")
    
    user = db.query(User).filter_by(strava_id=str(strava_id)).first()
    if user:
        user.strava_access_token = access_token
        user.strava_refresh_token = refresh_token
        user.strava_expires_at = expires_at
    else:
        user = User(
            username=f"strava_{strava_id}",
            email='',
            hashed_password="dummy",
            strava_id=strava_id,
            strava_access_token = access_token,
            strava_refresh_token = refresh_token,
            strava_expires_at = expires_at
        )
        db.add(user)
    db.commit()

    return {"message": "Strava authentication is successful"}



