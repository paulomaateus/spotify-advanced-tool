from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from spotifyWorker import SpotifyWorker
from schemas import TrackListPayload
from fastapi.security import OAuth2AuthorizationCodeBearer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
spotifyWorker = SpotifyWorker()


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


@app.get("/artista/{url_artista}/melhores-musicas")
def melhores_musicas_artista(url_artista: str):
    try:
        musicas = spotifyWorker.request_artist_top_tracks(artist_id=url_artista)
    except Exception as e:
        return {"error": str(e)}
    return musicas


@app.get("/artista/{url_artista}/albuns")
def albuns_artista(
    url_artista: str,
    categorias: str = "album",
    pais: str = "BR",
    quantidade: int = 50,
    offset: int = 0,
):
    try:
        albuns = spotifyWorker.request_artist_albums(
            artist_id=url_artista,
            categorias=categorias,
            pais=pais,
            quantidade=quantidade,
            offset=offset,
        )
    except Exception as e:
        return {"error": str(e)}
    return albuns


@app.get("/album/{url_album}")
def musicas_album(
    url_album: str,
):
    try:
        musicas = spotifyWorker.request_album_tracks(album_id=url_album)
    except Exception as e:
        return {"error": str(e)}
    return musicas


@app.get("/musica/{musica_id}")
def musica_info(musica_id: str):
    try:
        musica = spotifyWorker.request_track_info(track_id=musica_id)
    except Exception as e:
        return {"error": str(e)}

    return musica


@app.get("/album/{url_album}/ordenado")
def musicas_album(
    url_album: str,
):
    try:
        musicas = spotifyWorker.request_album_tracks_rank(album_id=url_album)
    except Exception as e:
        return {"error": str(e)}
    return musicas


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
