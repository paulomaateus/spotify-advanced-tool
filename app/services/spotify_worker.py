import requests
import base64
import threading
import httpx
from app.core.consts import CLIENT_ID, CLIENT_SECRET
from app.models.album import AlbumResponse
from app.models.track import TrackResponse
from app.models.artist import PopularTracksResponse, ArtistAlbumsResponse
from app.models.schemas import Error
from app.models.playlist import AddArtistTracksToPlaylistBody
from fastapi.responses import RedirectResponse


class SpotifyWorker:
    def __init__(self):
        self._token = None
        self._tokenType = None
        self._headers = None
        self._spotify_url = "https://api.spotify.com/v1"
        self.logged = False

    def _authorize_user(self):
        response_type = "code"
        redirect_uri = "http://localhost:8000/callback"
        scope = "playlist-modify-private playlist-modify-public playlist-read-private playlist-read-collaborative"
        url = f"https://accounts.spotify.com/authorize?response_type={response_type}&client_id={CLIENT_ID}&scope={scope}&redirect_uri={redirect_uri}"
        return RedirectResponse(url)

    async def _login(self, code: str):
        body = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "http://localhost:8000/callback",
        }
        bytes_credentials = f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8")
        base64_credentials = base64.b64encode(bytes_credentials).decode("utf-8")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {base64_credentials}",
        }
        url = "https://accounts.spotify.com/api/token"

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=body)
        if response.status_code == 200:
            data = response.json()
            self._token = data["access_token"]
            self._tokenType = data["token_type"]
            self._start_token_renewal_timer(data["expires_in"])
            self._headers = {"Authorization": f"{self._tokenType} {self._token}"}
            self.logged = True

            return RedirectResponse("http://localhost:8000/docs")
        else:
            raise Exception(f"Erro no login: {response.json()}")

    def _start_token_renewal_timer(self, expires_in):
        renewal_time = expires_in - 60
        timer = threading.Timer(renewal_time, self._login)
        timer.daemon = True
        timer.start()

    def _get_id_from_url(self, url: str) -> str:
        for i in range(len(url) - 1, -1, -1):
            if url[i] == "/":
                for j in range(i + 1, len(url) - 1):
                    if not url[j].isalnum():
                        return url[i + 1 : j]
                return url[i + 1 :]
        return url

    def request_artist_top_tracks(
        self, artist_id: str
    ) -> PopularTracksResponse | Error:

        formated_id = self._get_id_from_url(artist_id)
        url = f"{self._spotify_url}/artists/{formated_id}/top-tracks?market=BR"
        try:
            response = requests.get(url=url, headers=self._headers)
        except Exception as e:
            raise e
        if response.status_code != 200:
            return Error(**response.json())

        return PopularTracksResponse(**response.json())

    def request_artist_albums(
        self, artist_id: str, categories: str, country: str, quantity: int, offset: int
    ) -> ArtistAlbumsResponse | Error:
        formated_id = self._get_id_from_url(artist_id)
        url = f"{self._spotify_url}/artists/{formated_id}/albums?include_groups={categories}&market={country}&limit={quantity}&offset={offset}"
        try:
            response = requests.get(url=url, headers=self._headers)
        except Exception as e:
            raise e
        if response.status_code != 200:
            return Error(**response.json())

        return ArtistAlbumsResponse(**response.json())

    def request_album_tracks(
        self, album_id: str, detail: bool = False
    ) -> AlbumResponse | Error:
        formated_id = self._get_id_from_url(album_id)
        url = f"{self._spotify_url}/albums/{formated_id}"

        try:
            response = requests.get(url=url, headers=self._headers)
        except Exception as e:
            raise e
        if response.status_code != 200:
            return Error(**response.json())

        data = response.json()
        if detail:
            album_tracks = data["tracks"]["items"]
            album_tracks_infos = []

            for album_track in album_tracks:
                track_info = self.request_track_info(album_track["id"])
                if type(track_info) == Error:
                    return track_info
                album_tracks_infos.append(track_info)

            # if order_by:
            #     album_tracks_infos = sorted(
            #         album_tracks_infos, key=lambda track: track[order_by], reverse=True
            #     ) código para ordenar tracks com popularity
            data["tracks"]["items"] = album_tracks_infos
            response = AlbumResponse(**data)

            return response
        return AlbumResponse(**data)

    def request_track_info(self, track_id: str) -> TrackResponse | Error:
        formated_id = self._get_id_from_url(track_id)
        url = f"{self._spotify_url}/tracks/{formated_id}"
        try:
            response = requests.get(url=url, headers=self._headers)
        except Exception as e:
            raise e
        if response.status_code != 200:
            return Error(**response.json())
        return TrackResponse(**response.json())

    def add_artists_tracks_playlist(
        self, playlist_id, request_body: AddArtistTracksToPlaylistBody
    ):
        playlist_id = self._get_id_from_url(playlist_id)
        errors = []
        if request_body.all_tracks:
            # for each artist, retrieve their albums
            for artist_id in request_body.artists_ids:
                try:
                    albums = self.request_artist_albums(
                        artist_id, "album,single", "BR", 50, 0
                    )
                except Exception as e:
                    errors.append({"artist_id": artist_id, "error": str(e)})
                # for each album retrieved, request their tracks
                for album in albums.items:
                    try:
                        album_tracks = self.request_album_tracks(album_id=album.id)
                    except Exception as e:
                        errors.append({"album_id": album.id, "error": str(e)})
                    track_uris = [
                        {"name": track.name, "uri": track.uri}
                        for track in album_tracks.tracks.items
                    ]
                    # remove duplicates
                    seen_names = set()
                    track_uris = [
                        item
                        for item in track_uris
                        if item["name"] not in seen_names
                        and not seen_names.add(item["name"])
                    ]

                    # with the tracks, add the album's tracks in playlist
                    # the spotify only allowed add 100 songs per request, so this method add album by album in the provided playlist
                    try:
                        self._playlist_add_list_of_tracks(playlist_id=playlist_id, tracks=track_uris)
                    except Exception as e:
                        print("na verdade o erro foi aqui")
                        errors.append({"album_id": album.id, "error": str(e)})
            
            return {"errors": errors}
        else:   
            # TODO configure the input albums 
            return

    def _playlist_add_list_of_tracks(
        self, playlist_id: str, tracks: list[str], position: int = 0
    ):
        formated_id = self._get_id_from_url(playlist_id)
        track_uris = [track["uri"] for track in tracks]
        body = {"uris": track_uris, "position": position}
        url = f"{self._spotify_url}/playlists/{formated_id}/tracks"
        try:
            response = requests.post(url=url, headers=self._headers, json=body)
        except Exception as e:

            raise e
        return response
