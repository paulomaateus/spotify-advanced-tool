from pydantic import BaseModel
from typing import List

class AddArtistTracksToPlaylistConfig(BaseModel):
    limit_tracks_per_album: int = 50
    limit_tracks_per_artist: int = 50
    include_groups: List['str'] = ["album", "single", "compilation", "appears_on"]
    order_tracks_by_popularity: bool = False
    order_albums_by_popularity: bool = False

class AddArtistTracksToPlaylistBody(BaseModel):
    artists_ids: List["str"]
    all_tracks: bool
    configuration: AddArtistTracksToPlaylistConfig
    
class PlaylistAddTracksError(BaseModel):
    album_id: str = ""
    artist_id: str= ""
    track_id: str= ""
    error: str
    
class PlaylistAddTracksSucess(BaseModel):
    name: str = ""
    uri: str= ""
class PlaylistAddTracksResponse(BaseModel):
    errors: List["PlaylistAddTracksError"]
    success: List["PlaylistAddTracksSucess"]