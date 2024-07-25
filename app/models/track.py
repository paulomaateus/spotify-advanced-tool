from pydantic import BaseModel, ConfigDict
from typing import List


class TrackResponse(BaseModel):
    album: "TrackAlbumResponse"
    artists: List["TrackArtistResponse"]
    model_config = ConfigDict(extra="ignore")
    duration_ms: int | None
    id: str | None
    name:str | None
    popularity: int | None
    uri: str | None

class TrackAlbumResponse(BaseModel):
    id: str
    name: str
    uri: str


class TrackArtistResponse(BaseModel):
    name: str
    id: str
    uri: str

