import asyncio

import pytest

from app.orquestador.agentes.base import ArchivoGenerado
from app.orquestador.trabajos import EstadoTrabajo
from tests.factories import crear_configurador


async def _procesar(orquestador, config):
    trabajo = orquestador.trabajos.crear()
    await orquestador._procesar(trabajo, config)
    return trabajo


def _simular_pdf(monkeypatch, orquestador):
    monkeypatch.setattr(orquestador, "_generar_pdfs", lambda trabajo: (["curso.pdf"], []))


async def test_orquestador_fase_uno_inicia_programa_y_contenido_en_paralelo(
    orquestador_mock, config_referencia, monkeypatch
):
    # Arrange
    inicio_programa, inicio_contenido = asyncio.Event(), asyncio.Event()
    liberar = asyncio.Event()
    orquestador = orquestador_mock(
        barreras={
            "programa": (inicio_programa, liberar),
            "contenido": (inicio_contenido, liberar),
        }
    )
    _simular_pdf(monkeypatch, orquestador)
    trabajo = orquestador.trabajos.crear()
    tarea = asyncio.create_task(orquestador._procesar(trabajo, config_referencia))

    # Act
    await asyncio.gather(inicio_programa.wait(), inicio_contenido.wait())
    liberar.set()
    await tarea

    # Assert
    assert inicio_programa.is_set() and inicio_contenido.is_set()
    assert trabajo.estado is EstadoTrabajo.COMPLETADO


async def test_orquestador_fase_dos_espera_contenido_y_recibe_texto_real(
    orquestador_mock, config_referencia, monkeypatch
):
    # Arrange
    orquestador = orquestador_mock()
    _simular_pdf(monkeypatch, orquestador)

    # Act
    trabajo = await _procesar(orquestador, config_referencia)

    # Assert
    llamadas = orquestador._fabrica.llamadas
    prompt_eval = next(prompt for rol, prompt in llamadas if rol == "evaluacion")
    assert "ATENCIÓN: CONTENIDO REAL GENERADO" in prompt_eval
    assert "Texto del contenido." in prompt_eval
    assert [rol for rol, _ in llamadas].index("contenido") < [rol for rol, _ in llamadas].index("evaluacion")
    assert trabajo.estado is EstadoTrabajo.COMPLETADO


async def test_orquestador_sin_contenido_omite_fase_dos_y_degrada_estado(
    orquestador_mock, config_referencia, monkeypatch
):
    # Arrange
    orquestador = orquestador_mock({"contenido": [RuntimeError("error contenido")]})
    _simular_pdf(monkeypatch, orquestador)

    # Act
    trabajo = await _procesar(orquestador, config_referencia)

    # Assert
    assert trabajo.vias["evaluacion"] == "omitida"
    assert trabajo.vias["verificacion"] == "omitida"
    assert trabajo.estado is EstadoTrabajo.COMPLETADO_CON_ERRORES


async def test_orquestador_via_fallida_no_impide_resultados_de_otras(
    orquestador_mock, config_referencia, monkeypatch
):
    # Arrange
    orquestador = orquestador_mock({"evaluacion": [RuntimeError("fallo de evaluación")]})
    _simular_pdf(monkeypatch, orquestador)

    # Act
    trabajo = await _procesar(orquestador, config_referencia)

    # Assert
    assert trabajo.vias["evaluacion"] == "error: fallo de evaluación"
    assert "contenido_curso.md" in trabajo.archivos
    assert trabajo.estado is EstadoTrabajo.COMPLETADO_CON_ERRORES


async def test_orquestador_todas_las_vias_fallidas_termina_en_error(
    orquestador_mock, config_referencia
):
    # Arrange
    orquestador = orquestador_mock(
        {"programa": [RuntimeError("programa")], "contenido": [RuntimeError("contenido")]}
    )

    # Act
    trabajo = await _procesar(orquestador, config_referencia)

    # Assert
    assert trabajo.estado is EstadoTrabajo.ERROR
    assert trabajo.error == "Ninguna vía logró completarse."


async def test_orquestador_planificador_fallido_registra_error(orquestador_mock):
    # Arrange
    config = crear_configurador(datos={"metodologia": None})
    orquestador = orquestador_mock({"planificador": [RuntimeError("proveedor fuera") ]})

    # Act
    trabajo = await _procesar(orquestador, config)

    # Assert
    assert trabajo.estado is EstadoTrabajo.ERROR
    assert "no respondió: proveedor fuera" in trabajo.error


async def test_orquestador_iniciar_crea_trabajo_y_registra_tarea(
    orquestador_mock, config_referencia, monkeypatch
):
    # Arrange
    orquestador = orquestador_mock()
    _simular_pdf(monkeypatch, orquestador)

    # Act
    trabajo = orquestador.iniciar(config_referencia)
    tareas = tuple(orquestador._tareas)
    await asyncio.gather(*tareas)

    # Assert
    assert trabajo.id
    assert trabajo.estado is EstadoTrabajo.COMPLETADO


async def test_orquestador_guarda_archivos_internos_y_subplantillas(
    orquestador_mock, config_referencia, monkeypatch
):
    # Arrange
    orquestador = orquestador_mock()
    _simular_pdf(monkeypatch, orquestador)

    # Act
    trabajo = await _procesar(orquestador, config_referencia)

    # Assert
    assert (trabajo.dir_interno / "configurador.json").is_file()
    assert (trabajo.dir_interno / "plan_curso.json").is_file()
    assert (trabajo.dir_interno / "plantilla_madre.md").is_file()
    assert (trabajo.dir_interno / "subplantilla_programa.md").is_file()


def test_orquestador_generar_pdfs_registra_nombres_y_error(monkeypatch, tmp_path):
    # Arrange
    from app.orquestador import exportador_pdf
    from app.orquestador.orquestador import Orquestador
    from app.orquestador.trabajos import GestorTrabajos

    trabajo = GestorTrabajos(tmp_path).crear()
    (trabajo.dir_resultados / "curso.pdf").write_bytes(b"PDF")
    monkeypatch.setattr(
        exportador_pdf,
        "procesar_imagenes_y_pdf",
        lambda directorio, archivos: (["curso.pdf"], ["un markdown falló"]),
    )

    # Act
    generados, errores = Orquestador(tmp_path)._generar_pdfs(trabajo)

    # Assert
    assert generados == ["curso.pdf"]
    assert errores == ["un markdown falló"]
    assert trabajo.archivos["curso.pdf"].via == "exportador"


def test_orquestador_generar_pdfs_sin_pdf_agrega_error(monkeypatch, tmp_path):
    # Arrange
    from app.orquestador import exportador_pdf
    from app.orquestador.orquestador import Orquestador
    from app.orquestador.trabajos import GestorTrabajos

    trabajo = GestorTrabajos(tmp_path).crear()
    monkeypatch.setattr(exportador_pdf, "procesar_imagenes_y_pdf", lambda *args: ([], []))

    # Act
    generados, errores = Orquestador(tmp_path)._generar_pdfs(trabajo)

    # Assert
    assert generados == []
    assert errores == ["El exportador no generó ningún PDF."]


def test_orquestador_generar_pdfs_atrapa_error_del_exportador(monkeypatch, tmp_path):
    # Arrange
    from app.orquestador import exportador_pdf
    from app.orquestador.orquestador import Orquestador
    from app.orquestador.trabajos import GestorTrabajos

    trabajo = GestorTrabajos(tmp_path).crear()
    monkeypatch.setattr(exportador_pdf, "procesar_imagenes_y_pdf", lambda *args: 1 / 0)

    # Act
    generados, errores = Orquestador(tmp_path)._generar_pdfs(trabajo)

    # Assert
    assert generados == []
    assert "Falló la generación de PDF" in errores[0]


async def test_orquestador_correr_via_falla_registra_estado_error(
    orquestador_mock, config_referencia, plan_referencia
):
    # Arrange
    from app.orquestador.agentes.via_contenido import ViaContenido

    orquestador = orquestador_mock({"contenido": [ValueError("respuesta no válida")]})
    trabajo = orquestador.trabajos.crear()
    via = ViaContenido(orquestador._fabrica("contenido"))

    # Act
    resultado = await orquestador._correr_via(trabajo, via, "madre", config_referencia, plan_referencia)

    # Assert
    assert resultado is False
    assert trabajo.vias["contenido"] == "error: respuesta no válida"
