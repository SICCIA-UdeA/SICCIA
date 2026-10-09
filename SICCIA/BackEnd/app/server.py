"""Servidor ASGI que reúne los endpoints FastAPI y Flask del backend."""

from a2wsgi import WSGIMiddleware
from fastapi import FastAPI

from . import create_app as crear_app_flask
from .orquestador.app import crear_app as crear_app_orquestador


def crear_app() -> FastAPI:
    """Monta Flask dentro de FastAPI para servir ambas APIs en un puerto."""
    app = crear_app_orquestador()
    app.mount("/", WSGIMiddleware(crear_app_flask()), name="flask")
    return app