from fastapi import APIRouter, Depends, Request
from app.services.spotify_worker import SpotifyWorker

router = APIRouter()


@router.get("/login")
def login(spotify_service: SpotifyWorker = Depends()):
    return spotify_service._authorize_user()

@router.get("/callback")
async def callback(query_params: Request, spotify_service: SpotifyWorker = Depends()):
    
    code = query_params.query_params.get("code")
    error = query_params.query_params.get("error")
    if error:
        return error
    
    return await spotify_service._login(code)