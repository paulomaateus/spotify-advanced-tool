from pydantic import BaseModel
from typing import List
class PopularTracksAlbumResponse(BaseModel):
    album_type: str 
    id: str
    name: str
    release_date: str
    
class PopularTracksArtistResponse(BaseModel):
    id: str
    name: str
    uri: str
    

class PopularTrackResponse(BaseModel):
    album: PopularTracksAlbumResponse
    artists: List["PopularTracksArtistResponse"]
    duration_ms: int
    id: str
    name: str
    popularity: int
    uri: str
    
class PopularTracksResponse(BaseModel):
    tracks: List["PopularTrackResponse"]
    

class AlbumItemsResponse(BaseModel):
    album_type:str
    total_tracks: int
    id: str
    name: str
    release_date: str
    album_group: str
    uri: str
    

class ArtistAlbumsResponse(BaseModel):
    total: int
    items: List["AlbumItemsResponse"]