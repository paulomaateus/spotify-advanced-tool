from pydantic import BaseModel

class TrackListPayload(BaseModel):
    uris:list[str]
    position:int

class Error(BaseModel):
    status: int
    message: str