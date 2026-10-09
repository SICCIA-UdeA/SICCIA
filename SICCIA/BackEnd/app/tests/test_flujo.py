"""Pruebas con el ejecutor simulado (no requieren modelos ni agno). Ejecutar: pytest"""
import json
import time
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import Config
from app.server import crear_app as crear_backend_app
from controller.orquestador_controller import OrquestadorController
from orquestador import Configurador, Orquestador
from orquestador.ejecutores import EjecutorMock
from orquestador.plantillas import construir_plantilla_madre
from orquestador.planificador import Planificador

EJEMPLO = json.loads((Path(__file__).parent.parent / "ejemplo_configurador.json").read_text(encoding="utf-8"))


def _cliente(tmp_path):
    orq = Orquestador(directorio=tmp_path, fabrica_ejecutor=lambda rol: EjecutorMock())
    app = FastAPI()
    app.include_router(OrquestadorController(orq).router)
    return TestClient(app)


def test_flujo_completo_con_mock(tmp_path):
    with _cliente(tmp_path) as cliente:
        r = cliente.post("/orquestador/cursos", json=EJEMPLO)
        assert r.status_code == 202
        trabajo_id = r.json()["id"]

        for _ in range(100):
            estado = cliente.get(f"/orquestador/cursos/{trabajo_id}").json()
            if estado["estado"] not in ("pendiente", "planificando", "ejecutando"):
                break
            time.sleep(0.05)

        assert estado["estado"] == "completado", estado
        nombres = {a["nombre"] for a in estado["archivos"]}
        assert nombres == {"evaluaciones.md", "contenido_curso.md", "programa_curso.md", "presentaciones.md"}
        assert cliente.get(f"/orquestador/cursos/{trabajo_id}/descarga").status_code == 200
        assert (tmp_path / trabajo_id / "interno" / "plantilla_madre.md").exists()


def test_porcentajes_invalidos_dan_422(tmp_path):
    malo = json.loads(json.dumps(EJEMPLO))
    malo["evaluacion"]["actividades"][0]["porcentaje"] = 10
    with _cliente(tmp_path) as cliente:
        assert cliente.post("/orquestador/cursos", json=malo).status_code == 422


def test_auth_y_orquestador_comparten_servidor(monkeypatch, tmp_path):
    monkeypatch.setattr(Config, "SECRET_KEY", "test-secret-key")
    monkeypatch.setattr(Config, "GOOGLE_CLIENT_ID", "test-client")
    monkeypatch.setattr(Config, "GOOGLE_CLIENT_SECRET", "test-secret")
    monkeypatch.setenv("ORQ_PROVEEDOR", "mock")
    monkeypatch.setenv("ORQ_DIR_SALIDA", str(tmp_path))

    with TestClient(crear_backend_app()) as cliente:
        auth = cliente.get("/auth/me")
        assert auth.status_code == 401
        assert auth.json() == {"authenticated": False}

        inicio = cliente.post("/orquestador/cursos", json=EJEMPLO)
        assert inicio.status_code == 202
        trabajo_id = inicio.json()["id"]

        for _ in range(100):
            estado = cliente.get(f"/orquestador/cursos/{trabajo_id}").json()
            if estado["estado"] not in ("pendiente", "planificando", "ejecutando"):
                break
            time.sleep(0.05)

        assert estado["estado"] == "completado", estado


@pytest.mark.asyncio
async def test_plantilla_madre_contiene_estructura():
    config = Configurador.model_validate(EJEMPLO)
    plan = await Planificador(EjecutorMock()).completar(config)
    madre = construir_plantilla_madre(plan)
    assert "### Módulo 4" in madre and "4.3." in madre
    assert config.datos.publico_objetivo in madre  # lo dado por el usuario se conserva
