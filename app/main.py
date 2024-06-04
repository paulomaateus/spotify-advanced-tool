from fastapi import FastAPI, Depends
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from app.services.spotify_worker import SpotifyWorker
from app.api.endpoints import albums, artists, tracks, authorization

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
spotify_service = SpotifyWorker()

def get_spotify_service() -> SpotifyWorker: #TODO corrigir problemas de instancia compartilhada
    return spotify_service


app.include_router(albums.router, prefix="/album", tags=["albuns"], dependencies=[Depends(get_spotify_service)])
app.include_router(artists.router, prefix="/artista", tags=["artistas"], dependencies=[Depends(get_spotify_service)])
app.include_router(tracks.router, prefix="/faixa", tags=["faixas"], dependencies=[Depends(get_spotify_service)])
app.include_router(authorization.router, tags=["authorization"], dependencies=[Depends(get_spotify_service)])


@app.post("/playlists/album")
def adicionar_album_playlist(url_album: str, url_playlist: str, posicao: int = 0):
    lista_de_musicas = spotify_service._request_album_tracks_rank(url_album)
    try:
        response = spotify_service._playlist_add_list_of_tracks(
            playlist_id=url_playlist, position=posicao, tracks=lista_de_musicas
        )
    except Exception as e:
        return {"error": str(e)}
    return response.json()
