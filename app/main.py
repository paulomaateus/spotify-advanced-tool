from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from app.services.spotify_worker import SpotifyWorker
from app.api.endpoints import albums, artists, tracks

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
spotifyWorker = SpotifyWorker()

app.include_router(albums.router, prefix="/album", tags=["albuns"])
app.include_router(artists.router, prefix="/artista", tags=["artistas"])
app.include_router(tracks.router, prefix="/faixa", tags=["faixas"])

@app.get("/login")
def login():
    return spotifyWorker._authorize_user()

@app.get("/callback")
async def callback(query_params: Request):
    
    code = query_params.query_params.get("code")
    error = query_params.query_params.get("error")
    if error:
        return error
    
    return await spotifyWorker._login(code)



@app.post("/playlists/album")
def adicionar_album_playlist(url_album: str, url_playlist: str, posicao: int = 0):
    lista_de_musicas = spotifyWorker._request_album_tracks_rank(url_album)
    try:
        response = spotifyWorker._playlist_add_list_of_tracks(
            playlist_id=url_playlist, position=posicao, tracks=lista_de_musicas
        )
    except Exception as e:
        return {"error": str(e)}
    return response.json()
