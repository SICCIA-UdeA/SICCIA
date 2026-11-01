import io
import zipfile

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.orquestador.agentes.base import ArchivoGenerado
from app.orquestador.trabajos import EstadoTrabajo
from controller.orquestador_controller import OrquestadorController
from tests.factories import crear_configurador, fabrica_falsa


def _cliente_con_orquestador(orquestador):
    app = FastAPI()
    app.include_router(OrquestadorController(orquestador).router)
    return TestClient(app)


def _trabajo(orquestador, estado=EstadoTrabajo.COMPLETADO):
    trabajo = orquestador.trabajos.crear()
    trabajo.estado = estado
    return trabajo


def test_endpoint_crear_curso_devuelve_202(cliente_orquestador, config_referencia):
    # Arrange
    cuerpo = config_referencia.model_dump()

    # Act
    respuesta = cliente_orquestador.post("/orquestador/cursos", json=cuerpo)

    # Assert
    assert respuesta.status_code == 202
    assert respuesta.json()["id"]
    assert respuesta.json()["estado"] == "pendiente"


@pytest.mark.parametrize(
    "cuerpo",
    [
        {"datos": {"tema": "ab"}, "contenido": {"modulos_modo": "manual", "modulos": [{"titulo": "A"}]}},
        {"datos": {"tema": "Ciencias"}, "contenido": {"modulos_modo": "manual"}},
        {
            "datos": {"tema": "Ciencias"},
            "evaluacion": {"actividades": [{"tipo": "Quiz", "porcentaje": 60}, {"tipo": "Examen", "porcentaje": 30}]},
        },
    ],
)
def test_endpoint_crear_curso_configuracion_invalida_devuelve_422(cliente_orquestador, cuerpo):
    # Arrange
    datos_invalidos = cuerpo

    # Act
    respuesta = cliente_orquestador.post("/orquestador/cursos", json=datos_invalidos)

    # Assert
    assert respuesta.status_code == 422


def test_endpoint_estado_incluye_vias_archivos_y_advertencias(tmp_path):
    # Arrange
    from app.orquestador.orquestador import Orquestador

    orquestador = Orquestador(tmp_path, fabrica_falsa({}))
    trabajo = _trabajo(orquestador)
    trabajo.vias = {"contenido": "completada"}
    trabajo.advertencias = ["PDF parcial"]
    trabajo.archivos["curso.md"] = ArchivoGenerado("curso.md", "# Curso", "contenido")
    (trabajo.dir_resultados / "curso.md").write_text("# Curso", encoding="utf-8")
    cliente = _cliente_con_orquestador(orquestador)

    # Act
    respuesta = cliente.get(f"/orquestador/cursos/{trabajo.id}")

    # Assert
    assert respuesta.status_code == 200
    assert respuesta.json()["advertencias"] == ["PDF parcial"]
    assert respuesta.json()["archivos"][0]["tamano_bytes"] == 7


def test_endpoint_estado_trabajo_inexistente_devuelve_404(cliente_orquestador):
    # Arrange
    trabajo_id = "no-existe"

    # Act
    respuesta = cliente_orquestador.get(f"/orquestador/cursos/{trabajo_id}")

    # Assert
    assert respuesta.status_code == 404


def test_endpoint_descarga_zip_contiene_solo_pdfs_validos(tmp_path):
    # Arrange
    from app.orquestador.orquestador import Orquestador

    orquestador = Orquestador(tmp_path, fabrica_falsa({}))
    trabajo = _trabajo(orquestador)
    (trabajo.dir_resultados / "curso.pdf").write_bytes(b"PDF")
    (trabajo.dir_resultados / "curso.md").write_text("# Curso", encoding="utf-8")
    trabajo.archivos["curso.pdf"] = ArchivoGenerado("curso.pdf", "", "exportador")
    trabajo.archivos["curso.md"] = ArchivoGenerado("curso.md", "# Curso", "contenido")
    cliente = _cliente_con_orquestador(orquestador)

    # Act
    respuesta = cliente.get(f"/orquestador/cursos/{trabajo.id}/descarga")

    # Assert
    with zipfile.ZipFile(io.BytesIO(respuesta.content)) as archivo_zip:
        assert respuesta.status_code == 200
        assert archivo_zip.namelist() == ["curso.pdf"]
        assert archivo_zip.read("curso.pdf") == b"PDF"


@pytest.mark.parametrize(
    ("estado", "advertencia", "codigo"),
    [
        (EstadoTrabajo.EJECUTANDO, None, 409),
        (EstadoTrabajo.ERROR, "error general", 409),
        (EstadoTrabajo.COMPLETADO, "PDF no disponible", 500),
    ],
)
def test_endpoint_descarga_zip_estados_no_descargables_devuelve_error(tmp_path, estado, advertencia, codigo):
    # Arrange
    from app.orquestador.orquestador import Orquestador

    orquestador = Orquestador(tmp_path, fabrica_falsa({}))
    trabajo = _trabajo(orquestador, estado)
    trabajo.error = "error general" if estado is EstadoTrabajo.ERROR else None
    trabajo.advertencias = [advertencia] if advertencia else []
    cliente = _cliente_con_orquestador(orquestador)

    # Act
    respuesta = cliente.get(f"/orquestador/cursos/{trabajo.id}/descarga")

    # Assert
    assert respuesta.status_code == codigo


@pytest.mark.parametrize("contenido", [None, b""])
def test_endpoint_descarga_zip_pdf_ausente_o_vacio_devuelve_410(tmp_path, contenido):
    # Arrange
    from app.orquestador.orquestador import Orquestador

    orquestador = Orquestador(tmp_path, fabrica_falsa({}))
    trabajo = _trabajo(orquestador)
    trabajo.archivos["curso.pdf"] = ArchivoGenerado("curso.pdf", "", "exportador")
    if contenido is not None:
        (trabajo.dir_resultados / "curso.pdf").write_bytes(contenido)
    cliente = _cliente_con_orquestador(orquestador)

    # Act
    respuesta = cliente.get(f"/orquestador/cursos/{trabajo.id}/descarga")

    # Assert
    assert respuesta.status_code == 410


@pytest.mark.parametrize(
    ("nombre", "media_type"),
    [("curso.pdf", "application/pdf"), ("curso.md", "text/markdown")],
)
def test_endpoint_archivo_entrega_tipo_mime_correcto(tmp_path, nombre, media_type):
    # Arrange
    from app.orquestador.orquestador import Orquestador

    orquestador = Orquestador(tmp_path, fabrica_falsa({}))
    trabajo = _trabajo(orquestador)
    (trabajo.dir_resultados / nombre).write_bytes(b"contenido")
    trabajo.archivos[nombre] = ArchivoGenerado(nombre, "contenido", "contenido")
    cliente = _cliente_con_orquestador(orquestador)

    # Act
    respuesta = cliente.get(f"/orquestador/cursos/{trabajo.id}/archivos/{nombre}")

    # Assert
    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"].startswith(media_type)


def test_endpoint_archivo_no_registrado_devuelve_404(tmp_path):
    # Arrange
    from app.orquestador.orquestador import Orquestador

    orquestador = Orquestador(tmp_path, fabrica_falsa({}))
    trabajo = _trabajo(orquestador)
    cliente = _cliente_con_orquestador(orquestador)

    # Act
    respuesta = cliente.get(f"/orquestador/cursos/{trabajo.id}/archivos/falta.md")

    # Assert
    assert respuesta.status_code == 404


def test_endpoint_archivo_rechaza_ruta_fuera_de_resultados(tmp_path):
    # Arrange
    from app.orquestador.orquestador import Orquestador

    orquestador = Orquestador(tmp_path, fabrica_falsa({}))
    trabajo = _trabajo(orquestador)
    nombre = "..\\fuera.md"
    trabajo.archivos[nombre] = ArchivoGenerado(nombre, "fuera", "prueba")
    cliente = _cliente_con_orquestador(orquestador)

    # Act
    respuesta = cliente.get(f"/orquestador/cursos/{trabajo.id}/archivos/..%5Cfuera.md")

    # Assert
    assert respuesta.status_code == 400


def test_endpoint_descarga_zip_trabajo_inexistente_devuelve_404(cliente_orquestador):
    # Arrange
    trabajo_id = "ausente"

    # Act
    respuesta = cliente_orquestador.get(f"/orquestador/cursos/{trabajo_id}/descarga")

    # Assert
    assert respuesta.status_code == 404
