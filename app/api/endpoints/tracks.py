from fastapi import APIRouter, Depends
from app.services.spotify_worker import SpotifyWorker

router = APIRouter()



@router.get("/{musica_id}")
def track_info(track_id: str, spotify_service:SpotifyWorker = Depends()):
    try:
        track = spotify_service.request_track_info(track_id=track_id)
    except Exception as e:
        return {"error": str(e)}

    return track