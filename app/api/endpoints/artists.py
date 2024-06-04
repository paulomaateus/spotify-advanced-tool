from fastapi import APIRouter, Depends
from app.services.spotify_worker import SpotifyWorker

router = APIRouter()


@router.get("/{url_artista}/albuns")
def request_artist_albums(
    artist_id: str,
    categories: str = "album",
    country: str = "BR",
    quantity: int = 50,
    offset: int = 0,
    spotify_service: SpotifyWorker = Depends(),
):
    try:
        albuns = spotify_service.request_artist_albums(
            artist_id=artist_id,
            categories=categories,
            country=country,
            quantity=quantity,
            offset=offset,
        )
    except Exception as e:
        return {"error": str(e)}
    return albuns


@router.get("/{url_artista}/melhores-musicas")
def request_artist_popular_tracks(
    artist_id: str, spotify_service: SpotifyWorker = Depends()
):
    try:
        musicas = spotify_service.request_artist_top_tracks(artist_id=artist_id)
    except Exception as e:
        return {"error": str(e)}
    return musicas
