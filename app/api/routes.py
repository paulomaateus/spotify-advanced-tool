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
async def callback(query_params: Request):

    code = query_params.query_params.get("code")
    error = query_params.query_params.get("error")
    if error:
        return error

    return await spotify_service._login(code)


# Tracks routes
@router.get("/faixa/{musica_id}", tags=["Faixas"])
def track_info(track_id: str, res: Response) -> TrackResponse | Error:
    try:
        response = spotify_service.request_track_info(track_id=track_id)
    except Exception as e:
        res.status_code = 500
        return Error(message=str(e), status=500)
    if type(response) == Error:
        res.status_code = response.status
    
    return response
    

# Album routes
@router.get("/album/{url_album}", tags=["Albuns"])
def request_album_tracks(
    url_album: str, order_by: str = None,
):
    try:
        musicas = spotify_service.request_album_tracks(
            album_id=url_album, order_by=order_by
        )
    except Exception as e:
        return {"error": str(e)}
    return musicas


# Artists routes
@router.get("/artista/{url_artista}/albuns", tags=["Artistas"])
def request_artist_albums(
    artist_id: str,
    categories: str = "album",
    country: str = "BR",
    quantity: int = 50,
    offset: int = 0,
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


@router.get("/artista/{url_artista}/melhores-musicas", tags=["Artistas"])
def request_artist_popular_tracks(artist_id: str):
    try:
        musicas = spotify_service.request_artist_top_tracks(artist_id=artist_id)
    except Exception as e:
        return {"error": str(e)}
    return musicas


#playlists 
@router.post("/playlists/{id_playlist}/album", tags=["Playlists"])
def adicionar_album_playlist(id_playlist: str, url_album: str, posicao: int = 0):
    lista_de_musicas = spotify_service._request_album_tracks_rank(url_album)
    try:
        response = spotify_service._playlist_add_list_of_tracks(
            playlist_id=id_playlist, position=posicao, tracks=lista_de_musicas
        )
    except Exception as e:
        return {"error": str(e)}
    return response.json()

@router.post("/playlists/{id_playlist}/artists", tags=["Playlists"])
def adicionar_faixas_artista_playlist(id_playlist: str, req_body: AddArtistTracksToPlaylistBody ):
    try: 
        response = spotify_service.add_artists_tracks_playlist(playlist_id=id_playlist, request_body=req_body)
    except Exception as e: 
        return {"error" : str(e)}
    
    return response