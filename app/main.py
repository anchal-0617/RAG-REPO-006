import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.document_routes import router as document_router
from app.routes.ask_routes import router as ask_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows POST, GET, OPTIONS, etc.
    allow_headers=["*"],
)

app.include_router(document_router)
app.include_router(ask_router)