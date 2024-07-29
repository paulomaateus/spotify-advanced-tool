from pydantic import BaseModel
from typing import List

class AddArtistTracksToPlaylistConfig(BaseModel):
    limit: int
    include_groups: List['str']

class AddArtistTracksToPlaylistBody(BaseModel):
    artists_ids: List["str"]
    all_tracks: bool
    configuration: AddArtistTracksToPlaylistConfig