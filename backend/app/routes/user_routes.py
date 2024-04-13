from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.responses import JSONResponse

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
    """
    Redirects to Strava's OAuth page using client credentials.

    Returns:
        RedirectResponse: Redirects to the Strava OAuth page
        JSONResponse: Returns an error JSON response if environment variables are missing.
    """
    try:
        client_id = os.getenv("STRAVA_CLIENT_ID")
        if not client_id:
            raise ValueError("Strava Client ID is required.")

        redirect_uri = os.getenv("STRAVA_REDIRECT_URI")
        if not redirect_uri:
            raise ValueError("Could not find callback url.")

        scope = "read,activity:read"

        auth_url = f"http://www.strava.com/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&approval_prompt=force&scope={scope}"

        return RedirectResponse(auth_url)

    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


@router.get("/callback")
def strava_callback(code: str, db: Session = Depends(get_db)):
    token_url = "https://www.strava.com/oauth/token"
    data = {
        "client_id": os.getenv("STRAVA_CLIENT_ID"),
        "client_secret": os.getenv("STRAVA_CLIENT_SECRET"),
        "code": code,
        "grant_type": "authorization_code",
    }

    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"HTTP error occurred: {e}")
    except ValueError:
        raise HTTPException(status_code=500, detail="Error decoding JSON response")

    access_token = data.get("access_token")
    strava_id = data.get("athlete", {}).get("id")
    refresh_token = data.get("refresh_token")
    expires_at = data.get("expires_at")
    first_name = data.get("athlete", {}).get("firstname", "Default First Name")
    print(f"strava_callback: retrieve access token {access_token}")
    print(f"strava id: {strava_id}")

    if not access_token:
        raise HTTPException(status_code=400, detail="Strava authentication failed.")

    user = db.query(User).filter_by(strava_id=str(strava_id)).first()
    with db.begin():
        if user:
            user.strava_access_token = access_token
            user.strava_refresh_token = refresh_token
            user.strava_expires_at = expires_at
        else:
            user = User(
                username=f"strava_{strava_id}",
                first_name=first_name,
                email="",
                hashed_password="dummy",
                strava_id=strava_id,
                strava_access_token=access_token,
                strava_refresh_token=refresh_token,
                strava_expires_at=expires_at,
            )
            db.add(user)
        db.commit()

    return {"message": "Strava authentication is successful"}
