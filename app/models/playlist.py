from pydantic import BaseModel
from typing import List

class AddArtistTracksToPlaylistConfig(BaseModel):
    limit_tracks_per_album: int = 50
    limit_albums: int = 50
    include_groups: List['str'] = ["album", "single", "compilation", "appears_on"]
    order_tracks_by_popularity: bool = False
    order_albums_by_popularity: bool = False

class AddArtistTracksToPlaylistBody(BaseModel):
    artists_ids: List["str"]
    all_tracks: bool
    configuration: AddArtistTracksToPlaylistConfig