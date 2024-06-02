from fastapi import APIRouter
from app.services.spotify_worker import SpotifyWorker

router = APIRouter()
spotify_service = SpotifyWorker()


@router.get("/{url_album}")
def request_album_tracks(url_album: str, order_by: str | None):
    try:
        musicas = spotify_service.request_album_tracks(
            album_id=url_album, order_by=order_by
        )
    except Exception as e:
        return {"error": str(e)}
    return musicas
