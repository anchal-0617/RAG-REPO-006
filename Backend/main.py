import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Backend.routes.document_routes import router as document_router
from Backend.routes.ask_routes import router as ask_router

Backend = FastAPI()

Backend.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows POST, GET, OPTIONS, etc.
    allow_headers=["*"],
)

Backend.include_router(document_router)
Backend.include_router(ask_router)