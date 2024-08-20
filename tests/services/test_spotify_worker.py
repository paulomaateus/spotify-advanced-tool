import pytest
import os
from unittest.mock import patch, Mock, MagicMock
from fastapi.responses import RedirectResponse
from app.services.spotify_worker import SpotifyWorker
from app.models.artist import PopularTracksResponse, ArtistAlbumsResponse, AlbumItemsResponse
from app.models.album import AlbumResponse, AlbumTracksResponse, AlbumSimplifiedTrackResponse
from app.models.track import TrackResponse
from app.models.playlist import (
    AddArtistTracksToPlaylistBody,
    PlaylistAddTracksResponse,
    AddArtistTracksToPlaylistConfig,
)
from app.errors.custom_exceptions import LoginErrorException, SpotifyErrorException


@pytest.fixture
def spotify_worker():
    worker = SpotifyWorker()
    worker.logged = True
    return worker


@patch("app.services.spotify_worker.RedirectResponse")
def test_authorize_user_sucess(mock_redirect, spotify_worker):
    mock_redirect.return_value = Mock(spec=RedirectResponse)
    response = spotify_worker._authorize_user("test_client_id", "test_client_secret")
    assert isinstance(response, RedirectResponse)


@patch("app.services.spotify_worker.RedirectResponse")
def test_authorize_user_failure(mock_redirect, spotify_worker):
    mock_redirect.side_effect = Exception("Redirect error")
    with pytest.raises(LoginErrorException):
        spotify_worker._authorize_user("test_client_id", "test_client_secret")


def test_request_artist_top_tracks_success(spotify_worker):
    with patch("app.services.spotify_worker.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tracks": [
                {
                    "album": "album_id_1",
                    "id": "track_id_1",
                    "name": "Track 1",
                    "duration_ms": 1000,
                    "popularity": 100,
                    "uri": "dqwd10281r12jsd",
                    "album": {
                        "album_type": "album",
                        "id": "id120du10jsc",
                        "name": "FBC",
                        "release_date": "sadfsdlfsdfj",
                    },
                    "artists": [
                        {
                            "id": "123encdewc",
                            "name": "Pablo Escobar",
                            "uri": "sdajkajsdas",
                        }
                    ],
                },
                {
                    "album": "album_id_2",
                    "id": "track_id_2",
                    "name": "Track 2",
                    "duration_ms": 1000,
                    "popularity": 100,
                    "uri": "dqwd10281r12jsd",
                    "album": {
                        "album_type": "album",
                        "id": "id120du10jsc",
                        "name": "FBC",
                        "release_date": "sadfsdlfsdfj",
                    },
                    "artists": [
                        {
                            "id": "123encdewc",
                            "name": "Pablo Escobar",
                            "uri": "sdajkajsdas",
                        }
                    ],
                },
            ]
        }
        mock_get.return_value = mock_response

        response = spotify_worker.request_artist_top_tracks("artist_id")
        assert isinstance(response, PopularTracksResponse)
        assert len(response.tracks) == 2


def test_request_artist_albums_success(spotify_worker):
    with patch("app.services.spotify_worker.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total": "2",
            "items": [
                {
                    "id": "1",
                    "album_type": "algo 1",
                    "total_tracks": 2,
                    "name": "album teste1",
                    "release_date": "10/02/2020",
                    "album_group": "album",
                    "uri": "ljealsdnqwdqwdj",
                },
                {
                    "id": "12",
                    "album_type": "algo 2",
                    "total_tracks": 2,
                    "name": "album teste2",
                    "release_date": "10/02/2020",
                    "album_group": "album",
                    "uri": "ljealsdnqwdqwdj",
                },
            ],
        }
        mock_get.return_value = mock_response

        response = spotify_worker.request_artist_albums(
            "artist_id", "album,single", "BR", 10, 0
        )
        assert isinstance(response, ArtistAlbumsResponse)
        assert len(response.items) == 2


def test_request_album_tracks_success(spotify_worker):
    with patch("app.services.spotify_worker.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "album_type": "album",
            "total_tracks": "2",
            "id": "e129djasdcw",
            "name": "Album do FBC",
            "release_date": "20/02/2010",
            "uri": "asdasdsasdasda",
            "popularity": 100,
            "artists": [
                {"id": "sadaskjdaskld", "name": "fbc", "uri": "asdlajsasdasdk"}
            ],
            "tracks": {
                "total": 2,
                "items": [
                    {
                        "duration_ms": 1000,
                        "name": "se eu te contar",
                        "id": "saddqasdasdass",
                        "uri": "sajdlakdas",
                        "artists": [
                            {
                                "id": "skdjaldasdas",
                                "name": "FBC",
                                "uri": "asdasq2wwdqwj",
                            }
                        ],
                    },
                    {
                        "duration_ms": 1000,
                        "name": "se ta solteira",
                        "id": "saddqasdasdass",
                        "uri": "sajdlakdas",
                        "artists": [
                            {
                                "id": "skdjaldasdas",
                                "name": "FBC",
                                "uri": "asdasq2wwdqwj",
                            }
                        ],
                    },
                ],
            },
        }

        mock_get.return_value = mock_response

        response = spotify_worker.request_album_tracks("album_id", detail=False)
        assert isinstance(response, AlbumResponse)
        assert len(response.tracks.items) == 2


def test_request_track_info_success(spotify_worker):
    with patch("app.services.spotify_worker.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "duration_ms": 1000,
            "name": "se eu te contar",
            "id": "track_id_1",
            "uri": "sajdlakdas",
            "popularity": 100,
            "artists": [
                {
                    "id": "skdjaldasdas",
                    "name": "FBC",
                    "uri": "asdasq2wwdqwj",
                }
            ],
            "album": {"id": "album-id", "name": "fbc album", "uri": "essa uri"},
        }
        mock_get.return_value = mock_response

        response = spotify_worker.request_track_info("track_id")
        assert isinstance(response, TrackResponse)
        assert response.id == "track_id_1"


def test_add_artists_tracks_playlist(spotify_worker):
    # Mock the request_artist_albums and request_album_tracks methods
    with patch.object(
        spotify_worker, "request_artist_albums"
    ) as mock_artist_albums, patch.object(
        spotify_worker, "request_album_tracks"
    ) as mock_album_tracks, patch.object(
        spotify_worker, "_playlist_add_list_of_tracks"
    ) as mock_add_tracks:

        # Set up mock return values for the artist albums and album tracks
        mock_artist_albums.return_value = ArtistAlbumsResponse(
            total=1,
            items=[
                AlbumItemsResponse(
                    album_type="album",
                    total_tracks=10,
                    id="album_1",
                    name="Album 1",
                    release_date="2024-01-01",
                    album_group="album",
                    uri="spotify:album:1",
                )
            ],
        )

        mock_album_tracks.return_value = AlbumResponse(
            album_type="album",
            total_tracks=10,
            id="album_1",
            name="Album 1",
            release_date="2024-01-01",
            uri="spotify:album:1",
            artists=[],
            tracks=AlbumTracksResponse(
                total=10,
                items=[
                    AlbumSimplifiedTrackResponse(
                        artists=[],
                        duration_ms=180000,
                        id="track_1",
                        name="Track 1",
                        uri="spotify:track:1",
                    )
                ],
            ),
            popularity=50,
        )

        # Mock playlist add tracks success
        mock_add_tracks.return_value = MagicMock()

        # Create the request body
        config = AddArtistTracksToPlaylistConfig(
            limit_tracks_per_album=50,
            limit_tracks_per_artist=50,
            include_groups=["album", "single"],
            order_tracks_by_popularity=False,
            order_albums_by_popularity=False,
        )

        request_body = AddArtistTracksToPlaylistBody(
            artists_ids=["artist_1"], all_tracks=True, configuration=config
        )

        # Call the method to test
        result = spotify_worker.add_artists_tracks_playlist("playlist_1", request_body)

        # Assert that the mocks were called with the correct arguments
        mock_artist_albums.assert_called_once_with(
            "artist_1", "album,single,appears_on,compilation", "BR", 50, 0
        )
        mock_album_tracks.assert_called_once_with(album_id="album_1")
        mock_add_tracks.assert_called_once_with(
            playlist_id="playlist_1",
            tracks=[{"name": "Track 1", "uri": "spotify:track:1"}],
        )

        # Assert that the result is a PlaylistAddTracksResponse and check its contents
        assert isinstance(result, PlaylistAddTracksResponse)
        assert len(result.success) == 1
        assert len(result.errors) == 0
