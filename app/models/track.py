from pydantic import BaseModel
from typing import List


class TrackResponse(BaseModel):
    album: "TrackAlbumResponse"
    artists: List["TrackArtistResponse"]
    duration_ms: int
    id: str
    is_playable: bool
    name:str
    popularity: int
    uri: str

class TrackAlbumResponse(BaseModel):
    id: str
    name: str
    uri: str


class TrackArtistResponse(BaseModel):
    name: str
    id: str
    uri: str
