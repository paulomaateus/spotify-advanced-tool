from pydantic import BaseModel

class TrackListPayload(BaseModel):
    uris:list[str]
    position:int