from fastapi import APIRouter, Request, Response
from app.services.spotify_worker import SpotifyWorker
from app.models.track import TrackResponse
from app.models.schemas import Error
from app.models.playlist import AddArtistTracksToPlaylistBody

router = APIRouter()

spotify_service = SpotifyWorker()


# Authorization routes
@router.get("/login", tags=["Authorization"])
def login():
    return spotify_service._authorize_user()


@router.get("/callback", tags=["Authorization"])
async def callback(request: Request):
    code = request.query_params.get("code")
    error = request.query_params.get("error")
    if error:
        return {"error": error}

    return await spotify_service._login(code)


# Track routes
@router.get("/track/{track_id}", tags=["Tracks"])
def track_info(track_id: str, response: Response) -> TrackResponse | Error:
    try:
        result = spotify_service.request_track_info(track_id=track_id)
    except Exception as e:
        response.status_code = 500
        return Error(message=str(e), status=500)
    if isinstance(result, Error):
        response.status_code = result.status

    return result


# Album routes
@router.get("/album/{album_id}", tags=["Albums"])
def request_album_tracks(
    album_id: str, detail: bool = False
):
    try:
        tracks = spotify_service.request_album_tracks(
            album_id=album_id, detail=detail
        )
    except Exception as e:
        return {"error": str(e)}
    return tracks


# Artist routes
@router.get("/artist/{artist_id}/albums", tags=["Artists"])
def request_artist_albums(
    artist_id: str,
    categories: str = "album",
    country: str = "BR",
    quantity: int = 50,
    offset: int = 0,
):
    try:
        albums = spotify_service.request_artist_albums(
            artist_id=artist_id,
            categories=categories,
            country=country,
            quantity=quantity,
            offset=offset,
        )
    except Exception as e:
        return {"error": str(e)}
    return albums


@router.get("/artist/{artist_id}/top-tracks", tags=["Artists"])
def request_artist_top_tracks(artist_id: str):
    try:
        tracks = spotify_service.request_artist_top_tracks(artist_id=artist_id)
    except Exception as e:
        return {"error": str(e)}
    return tracks


# Playlist routes
@router.post("/playlists/{playlist_id}/artists", tags=["Playlists"])
def add_artist_tracks_to_playlist(
    playlist_id: str, req_body: AddArtistTracksToPlaylistBody
):
    try:
        response = spotify_service.add_artists_tracks_playlist(
            playlist_id=playlist_id, request_body=req_body
        )
    except Exception as e:
        return {"error": str(e)}

    return response
