from fastapi import APIRouter
from app.services.spotify_worker import SpotifyWorker

router = APIRouter()
spotify_service = SpotifyWorker()


@router.get("/{musica_id}")
def track_info(track_id: str):
    try:
        track = spotify_service.request_track_info(track_id=track_id)
    except Exception as e:
        return {"error": str(e)}

    return track