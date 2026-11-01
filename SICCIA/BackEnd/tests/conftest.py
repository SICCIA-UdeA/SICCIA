"""Aislamiento global para pruebas unitarias del backend."""
from __future__ import annotations

import os
import socket
import ipaddress

import dotenv
import pytest

BASE_URL = "http://localhost"

dotenv.load_dotenv = lambda *args, **kwargs: False
dotenv.dotenv_values = lambda *args, **kwargs: {}

from app.config import Config
from app.orquestador import config as config_orquestador
from app.orquestador.schemas import Configurador
from tests.factories import (
    FakeEjecutor,
    crear_configurador,
    crear_plan,
    fabrica_falsa,
)

config_orquestador._DOTENV = {}


@pytest.fixture(autouse=True)
def aislar_entorno(monkeypatch, tmp_path):
    for nombre in tuple(os.environ):
        if nombre.startswith("ORQ_") or nombre == "GOOGLE_API_KEY" or nombre.endswith("_API_KEY"):
            monkeypatch.delenv(nombre, raising=False)
    monkeypatch.setenv("ORQ_PROVEEDOR", "mock")
    monkeypatch.setattr(Config, "SECRET_KEY", "valor-de-prueba")
    monkeypatch.setattr(Config, "GOOGLE_CLIENT_ID", "valor-de-prueba")
    monkeypatch.setattr(Config, "GOOGLE_CLIENT_SECRET", "valor-de-prueba")
    monkeypatch.setattr(Config, "GOOGLE_REDIRECT_URI", f"{BASE_URL}/auth/google/callback")
    monkeypatch.setattr(config_orquestador, "_DOTENV", {})
    monkeypatch.chdir(tmp_path)


@pytest.fixture(autouse=True)
def bloquear_red(monkeypatch):
    conectar_original = socket.socket.connect

    def connect_bloqueado(sock, direccion):
        host = direccion[0] if isinstance(direccion, tuple) else direccion
        try:
            es_loopback = ipaddress.ip_address(host.split("%")[0]).is_loopback
        except ValueError:
            es_loopback = False
        if es_loopback:
            return conectar_original(sock, direccion)
        raise RuntimeError("red bloqueada en pruebas unitarias")

    monkeypatch.setattr(socket.socket, "connect", connect_bloqueado)


@pytest.fixture
def config_referencia() -> Configurador:
    return crear_configurador()


@pytest.fixture
def plan_referencia():
    return crear_plan()


@pytest.fixture
def fake_ejecutor_factory():
    return fabrica_falsa


@pytest.fixture
def orquestador_mock(tmp_path):
    def crear(respuestas=None, barreras=None):
        from app.orquestador.orquestador import Orquestador

        return Orquestador(
            directorio=tmp_path / "trabajos",
            fabrica_ejecutor=fabrica_falsa(respuestas or {}, barreras=barreras),
        )

    return crear


@pytest.fixture
def cliente_orquestador(tmp_path):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from app.orquestador.orquestador import Orquestador
    from controller.orquestador_controller import OrquestadorController

    app = FastAPI()
    app.include_router(
        OrquestadorController(
            Orquestador(directorio=tmp_path / "trabajos", fabrica_ejecutor=fabrica_falsa({}))
        ).router
    )
    return TestClient(app)


@pytest.fixture
def cliente_flask():
    from app import create_app

    return create_app().test_client()


__all__ = ["FakeEjecutor"]
