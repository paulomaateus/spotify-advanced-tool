import requests
import base64
import threading
import httpx
import os
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from app.errors.custom_exceptions import LoginErrorException, SpotifyErrorException
from app.core.consts import (
    AUTHORIZATION_URL,
    DEFAULT_SCOPE,
    SPOTIFY_API_URL,
    TOKEN_URL,
)
from app.models.album import AlbumResponse
from app.models.track import TrackResponse
from app.models.artist import PopularTracksResponse, ArtistAlbumsResponse
from app.models.playlist import AddArtistTracksToPlaylistBody, PlaylistAddTracksResponse


class SpotifyWorker:
    def __init__(self):
        load_dotenv()
        self._token = None
        self._tokenType = None
        self._headers = None
        self._spotify_url = SPOTIFY_API_URL
        self.logged = False
        self.server_url = f"{os.getenv('SERVER_IP')}:{os.getenv('SERVER_PORT')}"

    def _authorize_user(self, client_id: str, client_secret: str) -> RedirectResponse:
        response_type = "code"
        self.client_id = client_id
        self.client_secret = client_secret
        scope = DEFAULT_SCOPE
        url = f"{AUTHORIZATION_URL}?response_type={response_type}&client_id={client_id}&scope={scope}&redirect_uri=http://{self.server_url}/callback"
        try:
            return RedirectResponse(url)
        except Exception as e:
            raise LoginErrorException(f"Login Error: Cannot redirect. {str(e)}", 502)

    async def _login(self, code: str) -> RedirectResponse:
        body = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": f"http://{self.server_url}/callback",
        }
        bytes_credentials = f"{self.client_id}:{self.client_secret}".encode("utf-8")
        base64_credentials = base64.b64encode(bytes_credentials).decode("utf-8")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {base64_credentials}",
        }
        url = TOKEN_URL

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=body)
        if response.status_code == 200:
            data = response.json()
            self._token = data["access_token"]
            self._tokenType = data["token_type"]
            self._start_token_renewal_timer(data["expires_in"])
            self._headers = {"Authorization": f"{self._tokenType} {self._token}"}
            self.logged = True
            try:
                return RedirectResponse(f"http://{self.server_url}/docs")
            except Exception as e:
                raise LoginErrorException(
                    f"Login Error: Cannot redirect. {str(e)}", 502
                )
        else:
            raise LoginErrorException(f"Login Error: {response.json()}", 401)

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

    def request_artist_top_tracks(self, artist_id: str) -> PopularTracksResponse:

        if not self.logged:
            raise LoginErrorException(f"Login Error: The user is not logged in", 402)

        formated_id = self._get_id_from_url(artist_id)
        url = f"{self._spotify_url}/artists/{formated_id}/top-tracks?market=BR"
        try:
            response = requests.get(url=url, headers=self._headers)
        except Exception as e:
            raise e
        if response.status_code != 200:
            raise SpotifyErrorException(
                f"Spotify API Error: {response.json()['message']}", response.status_code
            )

        return PopularTracksResponse(**response.json())

    def request_artist_albums(
        self, artist_id: str, categories: str, country: str, quantity: int, offset: int
    ) -> ArtistAlbumsResponse:
        if not self.logged:
            raise LoginErrorException(f"Login Error: The user is not logged in", 402)

        formated_id = self._get_id_from_url(artist_id)
        url = f"{self._spotify_url}/artists/{formated_id}/albums?include_groups={categories}&market={country}&limit={quantity}&offset={offset}"
        try:
            response = requests.get(url=url, headers=self._headers)
        except Exception as e:
            raise e
        if response.status_code != 200:
            raise SpotifyErrorException(
                f"Spotify API Error: {response.json()['message']}", response.status_code
            )

        return ArtistAlbumsResponse(**response.json())

    def request_album_tracks(
        self, album_id: str, detail: bool = False
    ) -> AlbumResponse:
        if not self.logged:
            raise LoginErrorException(f"Login Error: The user is not logged in", 402)

        formated_id = self._get_id_from_url(album_id)
        url = f"{self._spotify_url}/albums/{formated_id}"

        try:
            response = requests.get(url=url, headers=self._headers)
        except Exception as e:
            raise e

        if response.status_code != 200:
            raise SpotifyErrorException(
                f"Spotify API Error: {response.json()['message']}", response.status_code
            )

        data = response.json()
        if detail:
            album_tracks = data["tracks"]["items"]
            album_tracks_infos = []

            for album_track in album_tracks:
                track_info = self.request_track_info(album_track["id"])
                album_tracks_infos.append(track_info)

            # if order_by:
            #     album_tracks_infos = sorted(
            #         album_tracks_infos, key=lambda track: track[order_by], reverse=True
            #     ) código para ordenar tracks com popularity
            data["tracks"]["items"] = album_tracks_infos
            response = AlbumResponse(**data)

            return response
        return AlbumResponse(**data)

    def request_track_info(self, track_id: str) -> TrackResponse:
        if not self.logged:
            raise LoginErrorException(f"Login Error: The user is not logged in", 402)

        formated_id = self._get_id_from_url(track_id)
        url = f"{self._spotify_url}/tracks/{formated_id}"
        try:
            response = requests.get(url=url, headers=self._headers)
        except Exception as e:
            raise e
        if response.status_code != 200:
            raise SpotifyErrorException(
                f"Spotify API Error: {response.json()['message']}", response.status_code
            )

        return TrackResponse(**response.json())

    def add_artists_tracks_playlist(
        self, playlist_id, request_body: AddArtistTracksToPlaylistBody
    ):
        if not self.logged:
            raise LoginErrorException(f"Login Error: The user is not logged in", 402)

        playlist_id = self._get_id_from_url(playlist_id)
        errors = []
        success = []
        seen_names = set()
        if request_body.all_tracks:
            # for each artist, retrieve their albums
            for artist_id in request_body.artists_ids:
                try:
                    albums = self.request_artist_albums(
                        artist_id, "album,single,appears_on,compilation", "BR", 50, 0
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
                    track_uris = [
                        item
                        for item in track_uris
                        if item["name"] not in seen_names
                        and not seen_names.add(item["name"])
                    ]

                    # with the tracks, add the album's tracks in playlist
                    # the spotify only allowed add 100 songs per request, so this method add album by album in the provided playlist
                    try:
                        self._playlist_add_list_of_tracks(
                            playlist_id=playlist_id, tracks=track_uris
                        )
                        success += track_uris
                    except Exception as e:
                        errors.append({"album_id": album.id, "error": str(e)})

            response = {"errors": errors, "success": success}

            return PlaylistAddTracksResponse(**response)
        else:
            # for each artist, retrieve their albums according the configuration provided
            for artist_id in request_body.artists_ids:
                try:
                    albums = self.request_artist_albums(
                        artist_id,
                        ",".join(request_body.configuration.include_groups),
                        "BR",
                        50,
                        0,
                    )
                except Exception as e:
                    errors.append({"artist_id": artist_id, "error": str(e)})
                # for each album retrieved, get their popularity number and sort by this if necessary
                all_albums = []

                for album in albums.items:
                    try:
                        album_tracks = self.request_album_tracks(
                            album_id=album.id,
                        )
                        all_albums.append(album_tracks)
                    except Exception as e:
                        errors.append({"album_id": album.id, "error": str(e)})
                # sorting albums by popularity
                if request_body.configuration.order_albums_by_popularity:
                    all_albums = sorted(
                        all_albums,
                        key=lambda album: album.popularity,
                        reverse=True,
                    )

                # limit the amount of albums
                albuns_count = -1
                tracks_count = 0
                for i in range(len(all_albums)):
                    if (
                        all_albums[i].tracks.total
                        < request_body.configuration.limit_tracks_per_album
                    ):
                        tracks_count += all_albums[i].tracks.total
                    else:
                        tracks_count += (
                            request_body.configuration.limit_tracks_per_album
                        )
                    if (
                        tracks_count
                        >= request_body.configuration.limit_tracks_per_artist
                    ):
                        albuns_count = i + 1
                        break
                if albuns_count != -1:
                    all_albums = all_albums[:albuns_count]

                # if I have to sorting tracks by popularity, request track details and sort
                if request_body.configuration.order_tracks_by_popularity:
                    albums_with_track_details = []
                    for album in all_albums:
                        try:
                            album_tracks = self.request_album_tracks(
                                album_id=album.id, detail=True
                            )
                            album_tracks.tracks.items = sorted(
                                album_tracks.tracks.items,
                                key=lambda track: track.popularity,
                                reverse=True,
                            )
                            albums_with_track_details.append(album_tracks)
                        except Exception as e:
                            errors.append({"album_id": album.id, "error": str(e)})

                    all_albums = albums_with_track_details

                # limit the quantity of tracks per album
                all_albums_tracks = [
                    album.tracks.items[
                        : request_body.configuration.limit_tracks_per_album
                    ]
                    for album in all_albums
                ]

                # collecting only the names and the uris of tracks
                albums_tracks_uris = [
                    [{"name": track.name, "uri": track.uri} for track in album]
                    for album in all_albums_tracks
                ]

                # remove duplicates
                albums_tracks_uris = [
                    [
                        item
                        for item in album_tracks_uris
                        if item["name"] not in seen_names
                        and not seen_names.add(item["name"])
                    ]
                    for album_tracks_uris in albums_tracks_uris
                ]
                # with the tracks, add the album's tracks in playlist
                # the spotify only allowed add 100 songs per request, so this method add album by album in the provided playlist
                tracks_count = 0
                for album_tracks_uris in albums_tracks_uris:
                    tracks_count += len(album_tracks_uris)
                    if (
                        tracks_count
                        <= request_body.configuration.limit_tracks_per_artist
                    ):
                        try:
                            self._playlist_add_list_of_tracks(
                                playlist_id=playlist_id, tracks=album_tracks_uris
                            )
                            success += album_tracks_uris
                        except Exception as e:
                            errors.append({"album_id": album.id, "error": str(e)})
                    else:
                        overflow = (
                            tracks_count
                            - request_body.configuration.limit_tracks_per_artist
                        )
                        try:
                            self._playlist_add_list_of_tracks(
                                playlist_id=playlist_id,
                                tracks=album_tracks_uris[:-overflow],
                            )
                            success += album_tracks_uris
                        except Exception as e:
                            errors.append({"album_id": album.id, "error": str(e)})

            response = {"errors": errors, "success": success}

            return PlaylistAddTracksResponse(**response)

    # TODO Adicionar o retorno desse metodo auxiliar para melhorar a lógica do metodo acima
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
