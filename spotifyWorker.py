import requests
import base64
import threading
import json
from fastapi.responses import RedirectResponse
from fastapi.requests import Request
import time
import httpx
from consts import CLIENT_ID, CLIENT_SECRET


class SpotifyWorker:
    def __init__(self):
        self._token = None
        self._tokenType = None
        self._spotify_url = "https://api.spotify.com/v1"


    def _authorize_user(self):
        response_type = "code"
        redirect_uri = "http://localhost:8000/callback"
        scope = "playlist-modify-private playlist-modify-public playlist-read-private playlist-read-collaborative"
        url = (
            f"https://accounts.spotify.com/authorize?response_type={response_type}&client_id={CLIENT_ID}&scope={scope}&redirect_uri={redirect_uri}"
        )
        return RedirectResponse(url)

    async def _login(self, code: str):
        body = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "http://localhost:8000/callback"
        }
        bytes_credentials = f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8")
        base64_credentials = base64.b64encode(bytes_credentials).decode("utf-8")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {base64_credentials}"
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

    def request_artist_top_tracks(self, artist_id: str):

        formated_id = self._get_id_from_url(artist_id)
        url = f"{self._spotify_url}/artists/{formated_id}/top-tracks?market=BR"
        try:
            response = requests.get(url=url, headers=self._headers)
        except Exception as e:
            raise e
        return response.json()

    def request_artist_albums(
        self, artist_id: str, categorias: str, pais: str, quantidade: int, offset: int
    ):
        formated_id = self._get_id_from_url(artist_id)
        url = f"{self._spotify_url}/artists/{formated_id}/albums?include_groups={categorias}&market={pais}&limit={quantidade}&offset={offset}"

        try:
            response = requests.get(url=url, headers=self._headers)
        except Exception as e:
            raise e
        return response.json()

    def request_album_tracks(self, album_id: str):
        formated_id = self._get_id_from_url(album_id)
        url = f"{self._spotify_url}/albums/{formated_id}"

        try:
            response = requests.get(url=url, headers=self._headers)
        except Exception as e:
            raise e
        return response.json()

    def request_track_info(self, track_id: str):
        formated_id = self._get_id_from_url(track_id)
        url = f"{self._spotify_url}/tracks/{formated_id}"
        try:
            response = requests.get(url=url, headers=self._headers)
        except Exception as e:
            raise e
        return response.json()

    def _request_album_tracks_rank(self, album_id: str):
        formated_id = self._get_id_from_url(album_id)
        url = f"{self._spotify_url}/albums/{formated_id}"
        try:
            response = requests.get(url=url, headers=self._headers)
        except Exception as e:
            raise e
        album_tracks = response.json()["tracks"]["items"]
        album_tracks_infos = []

        for album_track in album_tracks:
            album_tracks_infos.append(self.request_track_info(album_track["id"]))

        sorted_tracks = sorted(
            album_tracks_infos, key=lambda track: track["popularity"], reverse=True
        )

        return sorted_tracks

    def _playlist_add_list_of_tracks(
        self, playlist_id: str, tracks: list[str], position: int
    ):
        print(self._headers)
        formated_id = self._get_id_from_url(playlist_id)
        track_uris = [track["uri"] for track in tracks]
        body = {"uris": track_uris, "position": position}
        url = f"{self._spotify_url}/playlists/{formated_id}/tracks"
        try:
            response = requests.post(url=url, headers=self._headers, json=body)
        except Exception as e:

            raise e
        return response
