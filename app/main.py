from fastapi import FastAPI, Depends
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from app.services.spotify_worker import SpotifyWorker
from app.api import routes

app = FastAPI()

app.include_router(routes.router )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
