from pydantic import BaseModel
from typing import List
from app.models.track import TrackAlbumResponse

class AlbumResponse(BaseModel):
    album_type: str
    total_tracks: int
    id: str
    name: str
    release_date: str
    uri: str
    artists: List["AlbumArtistsResponse"]
    tracks: "AlbumTracksResponse"


class AlbumArtistsResponse(BaseModel):
    id: str
    name: str
    uri: str


class AlbumTracksResponse(BaseModel):
    total: int
    items: List["AlbumSimplifiedTrackResponse"] | List["TrackAlbumResponse"]


class AlbumSimplifiedTrackResponse(BaseModel):
    artists: List["AlbumArtistsResponse"]
    duration_ms: int
    id: str
    is_playable: bool
    name: str
    uri: str
    
