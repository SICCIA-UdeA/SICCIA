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
from app.orquestador import Configurador, Orquestador
from app.orquestador.ejecutores import EjecutorMock
from app.orquestador.plantillas import construir_plantilla_madre, distribucion_horaria
from app.orquestador.planificador import Planificador

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

        for _ in range(1200):
            estado = cliente.get(f"/orquestador/cursos/{trabajo_id}").json()
            if estado["estado"] not in ("pendiente", "planificando", "ejecutando"):
                break
            time.sleep(0.05)

        assert estado["estado"] == "completado", estado
        nombres = {a["nombre"] for a in estado["archivos"] if a["nombre"].endswith(".md")}
        assert nombres == {"evaluaciones.md", "contenido_curso.md", "programa_curso.md", "presentaciones.md", "verificacion.md"}
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
    for rol in ("PLANIFICADOR", "EVALUACION", "CONTENIDO", "PROGRAMA", "VERIFICACION"):
        monkeypatch.setenv(f"ORQ_PROVEEDOR_{rol}", "mock")
    monkeypatch.setenv("ORQ_DIR_SALIDA", str(tmp_path))

    with TestClient(crear_backend_app()) as cliente:
        auth = cliente.get("/auth/me")
        assert auth.status_code == 401
        assert auth.json() == {"authenticated": False}

        inicio = cliente.post("/orquestador/cursos", json=EJEMPLO)
        assert inicio.status_code == 202
        trabajo_id = inicio.json()["id"]

        for _ in range(1200):
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


@pytest.mark.asyncio
async def test_distribucion_horaria_reparte_y_conserva_totales():
    config = Configurador.model_validate(EJEMPLO)
    plan = await Planificador(EjecutorMock()).completar(config)

    tabla = distribucion_horaria(plan)

    assert "| **TOTAL** | | **30** | **30** |" in tabla
    assert tabla.count("| Módulo") == sum(len(m.temas) for m in plan.modulos) + 1
    assert "## Distribución horaria común y obligatoria" in construir_plantilla_madre(plan)


def test_distribucion_horaria_acepta_rango_y_no_repite_duracion_por_tema():
    config = Configurador.model_validate(EJEMPLO)
    config.datos.duracion_estimada = "12-16 horas"
    plan = Planificador._plan_simulado(config).model_copy(
        update={"duracion_estimada": config.datos.duracion_estimada}
    )

    tabla = distribucion_horaria(plan)

    assert "| **TOTAL** | | **12** | **16** |" in tabla
    assert tabla.count("| **TOTAL**") == 1


def test_planificador_parsea_json_entre_texto():
    plan = Planificador._parsear(
        'Aquí está el plan:\n```json\n{"tema":"Python","publico_objetivo":"Docentes",'
        '"duracion_estimada":"10 horas","metodologia":"Práctica",'
        '"modulos":[{"titulo":"Bases","temas":["Variables"]}]}\n```\n'
    )
    assert plan.modulos[0].temas == ["Variables"]


def test_planificador_detecta_error_del_proveedor_en_el_contenido():
    assert Planificador._es_error_proveedor(
        "Error code: 429 - Rate limit exceeded: free-models-per-day"
    )


@pytest.mark.asyncio
async def test_planificador_no_disfraza_error_del_proveedor():
    class EjecutorFallido:
        es_simulado = False

        async def generar(self, *, rol, instrucciones, prompt):
            raise ValueError("429: rate limit")

    config = Configurador.model_validate(EJEMPLO)
    with pytest.raises(RuntimeError, match="proveedor.*429: rate limit"):
        await Planificador(EjecutorFallido()).completar(config)


def test_pdf_se_descarga_como_pdf_y_entra_al_zip(tmp_path):
    import io
    import zipfile

    with _cliente(tmp_path) as cliente:
        trabajo_id = cliente.post("/orquestador/cursos", json=EJEMPLO).json()["id"]
        for _ in range(1200):
            estado = cliente.get(f"/orquestador/cursos/{trabajo_id}").json()
            if estado["estado"] not in ("pendiente", "planificando", "ejecutando"):
                break
            time.sleep(0.05)

        pdfs = [a["nombre"] for a in estado["archivos"] if a["nombre"].endswith(".pdf")]
        assert pdfs, "no se registró ningún PDF (revisa que WeasyPrint esté instalado)"

        r = cliente.get(f"/orquestador/cursos/{trabajo_id}/archivos/{pdfs[0]}")
        assert r.status_code == 200
        assert r.headers["content-type"] == "application/pdf"
        assert r.content[:4] == b"%PDF"

        z = cliente.get(f"/orquestador/cursos/{trabajo_id}/descarga")
        assert z.status_code == 200
        with zipfile.ZipFile(io.BytesIO(z.content)) as zf:
            assert all(nombre.endswith(".pdf") for nombre in zf.namelist())
            assert zf.read(pdfs[0])[:4] == b"%PDF"