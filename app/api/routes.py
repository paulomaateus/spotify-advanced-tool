from fastapi import APIRouter, Request, Response, HTTPException
from app.services.spotify_worker import SpotifyWorker
from app.models.track import TrackResponse
from app.models.playlist import AddArtistTracksToPlaylistBody, PlaylistAddTracksResponse
from app.models.album import AlbumResponse
from app.models.artist import ArtistAlbumsResponse, PopularTracksResponse
from app.errors.custom_exceptions import LoginErrorException, SpotifyErrorException

router = APIRouter()

spotify_service = SpotifyWorker()


# Authorization routes
@router.get("/login", tags=["Authorization"])
def login(client_id: str, client_secret: str):
    try:
        return spotify_service._authorize_user(
            client_id=client_id, client_secret=client_secret
        )
    except LoginErrorException as e:
        raise HTTPException(status_code=e.status, detail=e.message)


@router.get("/callback", tags=["Authorization"])
async def callback(request: Request):
    code = request.query_params.get("code")
    error = request.query_params.get("error")
    if error:
        return {"error": error}
    try:
        return await spotify_service._login(code)
    except LoginErrorException as e:
        raise HTTPException(status_code=e.status, detail=e.message)


# Track routes
@router.get("/track/{track_id}", tags=["Tracks"])
def track_info(track_id: str, response: Response) -> TrackResponse:
    try:
        result = spotify_service.request_track_info(track_id=track_id)
    except LoginErrorException as e:
        raise HTTPException(status_code=e.status, detail=e.message)
    except SpotifyErrorException as e:
        raise HTTPException(message=e.message, status_code=e.status)

    return result


# Album routes
@router.get("/album/{album_id}", tags=["Albums"])
def request_album_tracks(album_id: str, detail: bool = False) -> AlbumResponse:
    try:
        tracks = spotify_service.request_album_tracks(album_id=album_id, detail=detail)
    except LoginErrorException as e:
        raise HTTPException(status_code=e.status, detail=e.message)
    except SpotifyErrorException as e:
        raise HTTPException(message=e.message, status_code=e.status)
    return tracks


# Artist routes
@router.get("/artist/{artist_id}/albums", tags=["Artists"])
def request_artist_albums(
    artist_id: str,
    categories: str = "album",
    country: str = "BR",
    quantity: int = 50,
    offset: int = 0,
) -> ArtistAlbumsResponse:
    try:
        albums = spotify_service.request_artist_albums(
            artist_id=artist_id,
            categories=categories,
            country=country,
            quantity=quantity,
            offset=offset,
        )
    except LoginErrorException as e:
        raise HTTPException(status_code=e.status, detail=e.message)
    except SpotifyErrorException as e:
        raise HTTPException(message=e.message, status_code=e.status)
    return albums


@router.get("/artist/{artist_id}/top-tracks", tags=["Artists"])
def request_artist_top_tracks(artist_id: str) -> PopularTracksResponse:
    try:
        tracks = spotify_service.request_artist_top_tracks(artist_id=artist_id)
    except LoginErrorException as e:
        raise HTTPException(status_code=e.status, detail=e.message)
    except SpotifyErrorException as e:
        raise HTTPException(message=e.message, status_code=e.status)
    return tracks


# Playlist routes
@router.post("/playlists/{playlist_id}/artists", tags=["Playlists"])
def add_artist_tracks_to_playlist(
    playlist_id: str, req_body: AddArtistTracksToPlaylistBody
) -> PlaylistAddTracksResponse:
    try:
        response = spotify_service.add_artists_tracks_playlist(
            playlist_id=playlist_id, request_body=req_body
        )
    except LoginErrorException as e:
        raise HTTPException(status_code=e.status, detail=e.message)
    except SpotifyErrorException as e:
        raise HTTPException(message=e.message, status_code=e.status)

    return response
