"""Punto de entrada de Render para servir la API y la web en el mismo dominio."""

from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from main import app


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://benjapato.github.io"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

carpeta_web = Path(__file__).resolve().parent.parent / "web"
app.mount("/web", StaticFiles(directory=carpeta_web, html=True), name="web")
