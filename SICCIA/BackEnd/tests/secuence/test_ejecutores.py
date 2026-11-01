import asyncio
import csv
from types import SimpleNamespace

import agno.agent
import pytest

from app.orquestador.config import ConfigModelo
from app.orquestador import ejecutores as modulo_ejecutores
from app.orquestador.ejecutores import (
    ConfiguracionProveedorError,
    EjecutorAgno,
    EjecutorMock,
    log_prueba,
)


def _modelo(proveedor="openai", respaldo=None, api_key="valor-de-prueba", base_url=None):
    return ConfigModelo(
        proveedor=proveedor,
        model_id="modelo-prueba",
        api_key=api_key,
        base_url=base_url,
        temperatura=0.1,
        max_tokens=20,
        timeout_segundos=5,
        respaldo=respaldo,
    )


def _agente_falso(monkeypatch, respuestas):
    class AgenteFalso:
        llamadas = 0

        def __init__(self, **kwargs):
            AgenteFalso.kwargs = kwargs

        async def arun(self, prompt):
            AgenteFalso.llamadas += 1
            respuesta = respuestas.pop(0)
            if isinstance(respuesta, Exception):
                raise respuesta
            return respuesta

    monkeypatch.setattr(agno.agent, "Agent", AgenteFalso)
    return AgenteFalso


async def test_ejecutor_mock_entrega_un_archivo_por_marcador(monkeypatch):
    # Arrange
    async def sin_espera(_):
        return None

    monkeypatch.setattr(asyncio, "sleep", sin_espera)
    ejecutor = EjecutorMock()
    prompt = "## Formato de entrega\n<!-- ARCHIVO: uno.md -->\n<!-- ARCHIVO: dos.md -->"

    # Act
    respuesta = await ejecutor.generar(rol="contenido", instrucciones="", prompt=prompt)

    # Assert
    assert respuesta.count("<!-- ARCHIVO:") == 2
    assert "[SIMULADO]" in respuesta


async def test_ejecutor_mock_sin_marcadores_devuelve_cuerpo(monkeypatch):
    # Arrange
    async def sin_espera(_):
        return None

    monkeypatch.setattr(asyncio, "sleep", sin_espera)
    ejecutor = EjecutorMock()

    # Act
    respuesta = await ejecutor.generar(rol="contenido", instrucciones="", prompt="# Sección")

    # Assert
    assert "[SIMULADO] Resultado" in respuesta
    assert "Prompt recibido" in respuesta


async def test_ejecutor_agno_respuesta_valida_registra_telemetria(monkeypatch, tmp_path):
    # Arrange
    from pathlib import Path

    monkeypatch.chdir(tmp_path)
    respuesta = SimpleNamespace(content="contenido válido", metrics={"prompt_tokens": 2, "completion_tokens": 3})
    _agente_falso(monkeypatch, [respuesta])
    ejecutor = EjecutorAgno(_modelo())
    monkeypatch.setattr(ejecutor, "_crear_modelo", lambda cfg=None: SimpleNamespace(id="modelo-prueba"))

    # Act
    resultado = await ejecutor.generar(rol="contenido", instrucciones="instrucciones", prompt="prompt")

    # Assert
    assert resultado == "contenido válido"
    assert Path("registro_pruebas_siccia.csv").is_file()


async def test_ejecutor_agno_modelo_planificador_solicita_esquema(monkeypatch):
    # Arrange
    agente = _agente_falso(monkeypatch, [SimpleNamespace(content="respuesta")])
    ejecutor = EjecutorAgno(_modelo())
    modelo = SimpleNamespace(id="modelo-prueba")
    monkeypatch.setattr(ejecutor, "_crear_modelo", lambda cfg=None: modelo)
    monkeypatch.setattr(modulo_ejecutores, "log_prueba", lambda **kwargs: None)

    # Act
    await ejecutor.generar(rol="planificador", instrucciones="", prompt="")

    # Assert
    assert agente.kwargs["use_json_mode"] is True
    assert agente.kwargs["output_schema"].__name__ == "CursoPlan"


async def test_ejecutor_agno_acepta_contenido_modelo(monkeypatch):
    # Arrange
    class ContenidoModelo:
        def model_dump_json(self):
            return '{"resultado":"válido"}'

    _agente_falso(monkeypatch, [SimpleNamespace(content=ContenidoModelo())])
    ejecutor = EjecutorAgno(_modelo())
    monkeypatch.setattr(ejecutor, "_crear_modelo", lambda cfg=None: SimpleNamespace(id="modelo"))
    monkeypatch.setattr(modulo_ejecutores, "log_prueba", lambda **kwargs: None)

    # Act
    resultado = await ejecutor.generar(rol="contenido", instrucciones="", prompt="")

    # Assert
    assert resultado == '{"resultado":"válido"}'


async def test_ejecutor_agno_sin_content_convierte_respuesta_a_texto(monkeypatch):
    # Arrange
    respuesta = SimpleNamespace()
    _agente_falso(monkeypatch, [respuesta])
    ejecutor = EjecutorAgno(_modelo())
    monkeypatch.setattr(ejecutor, "_crear_modelo", lambda cfg=None: SimpleNamespace(id="modelo"))
    monkeypatch.setattr(modulo_ejecutores, "log_prueba", lambda **kwargs: None)

    # Act
    resultado = await ejecutor.generar(rol="contenido", instrucciones="", prompt="")

    # Assert
    assert resultado == str(respuesta)


@pytest.mark.parametrize(
    ("proveedor", "clave", "base_url", "atributo", "argumentos"),
    [
        ("gemini", "valor-de-prueba", None, "Gemini", {"api_key": "valor-de-prueba"}),
        ("openai_like", "valor-de-prueba", "https://api.localhost/v1", "OpenAILike", {"base_url": "https://api.localhost/v1"}),
        ("openai", "valor-de-prueba", None, "OpenAIChat", {"api_key": "valor-de-prueba"}),
    ],
)
def test_ejecutor_agno_crea_modelo_con_configuracion(monkeypatch, proveedor, clave, base_url, atributo, argumentos):
    # Arrange
    import agno.models.google
    import agno.models.openai
    import agno.models.openai.like

    llamadas = []

    class ModeloFalso:
        def __init__(self, **kwargs):
            llamadas.append(kwargs)

    modulo = {
        "Gemini": agno.models.google,
        "OpenAILike": agno.models.openai.like,
        "OpenAIChat": agno.models.openai,
    }[atributo]
    monkeypatch.setattr(modulo, atributo, ModeloFalso)
    ejecutor = EjecutorAgno(_modelo(proveedor=proveedor, api_key=clave, base_url=base_url))

    # Act
    modelo = ejecutor._crear_modelo()

    # Assert
    assert isinstance(modelo, ModeloFalso)
    assert all(llamadas[0][clave] == valor for clave, valor in argumentos.items())


def test_ejecutor_agno_proveedor_desconocido_falla():
    # Arrange
    ejecutor = EjecutorAgno(_modelo(proveedor="desconocido"))

    # Act
    with pytest.raises(ValueError, match="no soportado"):
        ejecutor._crear_modelo()

    # Assert
    assert ejecutor._cfg.proveedor == "desconocido"


async def test_ejecutor_agno_respaldo_mal_configurado_agota_proveedores(monkeypatch):
    # Arrange
    principal = _modelo()
    respaldo = _modelo(proveedor="gemini", api_key=None)
    ejecutor = EjecutorAgno(ConfigModelo(**{**principal.__dict__, "respaldo": respaldo}))
    _agente_falso(monkeypatch, [RuntimeError("error permanente")])

    def crear_modelo(cfg=None):
        if cfg.proveedor == "gemini":
            raise ConfiguracionProveedorError("respaldo incompleto")
        return SimpleNamespace(id="modelo")

    monkeypatch.setattr(ejecutor, "_crear_modelo", crear_modelo)

    # Act
    with pytest.raises(RuntimeError, match="Fallaron los proveedores"):
        await ejecutor.generar(rol="contenido", instrucciones="", prompt="")

    # Assert
    assert ejecutor._cfg.respaldo.proveedor == "gemini"


async def test_ejecutor_agno_error_de_telemetria_no_pierde_respuesta(monkeypatch):
    # Arrange
    _agente_falso(monkeypatch, [SimpleNamespace(content="contenido útil")])
    ejecutor = EjecutorAgno(_modelo())
    monkeypatch.setattr(ejecutor, "_crear_modelo", lambda cfg=None: SimpleNamespace(id="modelo"))
    monkeypatch.setattr(
        modulo_ejecutores,
        "log_prueba",
        lambda **kwargs: (_ for _ in ()).throw(OSError("CSV no disponible")),
    )

    # Act
    resultado = await ejecutor.generar(rol="contenido", instrucciones="", prompt="")

    # Assert
    assert resultado == "contenido útil"


async def test_ejecutor_agno_error_transitorio_reintenta(monkeypatch):
    # Arrange
    _agente_falso(monkeypatch, [RuntimeError("503 temporal"), SimpleNamespace(content="recuperado")])
    ejecutor = EjecutorAgno(_modelo())
    monkeypatch.setattr(ejecutor, "_crear_modelo", lambda cfg=None: SimpleNamespace(id="modelo-prueba"))

    async def sin_espera(_):
        return None

    monkeypatch.setattr(asyncio, "sleep", sin_espera)

    # Act
    resultado = await ejecutor.generar(rol="contenido", instrucciones="", prompt="")

    # Assert
    assert resultado == "recuperado"


async def test_ejecutor_agno_error_no_reintentable_se_propaga(monkeypatch):
    # Arrange
    agente = _agente_falso(monkeypatch, [RuntimeError("error permanente")])
    ejecutor = EjecutorAgno(_modelo())
    monkeypatch.setattr(ejecutor, "_crear_modelo", lambda cfg=None: SimpleNamespace(id="modelo-prueba"))

    # Act
    with pytest.raises(RuntimeError, match="Fallaron los proveedores"):
        await ejecutor.generar(rol="contenido", instrucciones="", prompt="")

    # Assert
    assert agente.llamadas == 1


async def test_ejecutor_agno_agota_primario_y_usa_respaldo(monkeypatch):
    # Arrange
    principal = _modelo()
    respaldo = _modelo(proveedor="gemini")
    ejecutor = EjecutorAgno(
        ConfigModelo(**{**principal.__dict__, "respaldo": respaldo})
    )
    proveedores = []

    def crear_modelo(cfg=None):
        proveedores.append(cfg.proveedor)
        return SimpleNamespace(id=cfg.proveedor)

    _agente_falso(
        monkeypatch,
        [RuntimeError("503")] * 3 + [SimpleNamespace(content="respuesta de respaldo")],
    )
    monkeypatch.setattr(ejecutor, "_crear_modelo", crear_modelo)

    async def sin_espera(_):
        return None

    monkeypatch.setattr(asyncio, "sleep", sin_espera)

    # Act
    resultado = await ejecutor.generar(rol="contenido", instrucciones="", prompt="")

    # Assert
    assert resultado == "respuesta de respaldo"
    assert proveedores == ["openai", "gemini"]


@pytest.mark.parametrize("contenido", ["", "None", "null", "nan"])
async def test_ejecutor_agno_respuesta_vacia_o_nula_falla(monkeypatch, contenido):
    # Arrange
    _agente_falso(monkeypatch, [SimpleNamespace(content=contenido)])
    ejecutor = EjecutorAgno(_modelo())
    monkeypatch.setattr(ejecutor, "_crear_modelo", lambda cfg=None: SimpleNamespace(id="modelo-prueba"))

    # Act
    with pytest.raises(RuntimeError, match="Fallaron los proveedores"):
        await ejecutor.generar(rol="contenido", instrucciones="", prompt="")

    # Assert
    assert contenido.strip("` \t\r\n").lower() in {"", "none", "null", "nan"}


async def test_ejecutor_agno_json_de_error_no_se_acepta(monkeypatch):
    # Arrange
    _agente_falso(monkeypatch, [SimpleNamespace(content='{"error":"respuesta rechazada"}')])
    ejecutor = EjecutorAgno(_modelo())
    monkeypatch.setattr(ejecutor, "_crear_modelo", lambda cfg=None: SimpleNamespace(id="modelo-prueba"))

    # Act
    with pytest.raises(RuntimeError, match="Fallaron los proveedores"):
        await ejecutor.generar(rol="contenido", instrucciones="", prompt="")

    # Assert
    assert not ejecutor._reintentable(ValueError("respuesta rechazada"))


@pytest.mark.parametrize(
    ("error", "reintentable"),
    [
        (TimeoutError("timeout"), True),
        (RuntimeError("429"), True),
        (RuntimeError("503"), True),
        (RuntimeError("mensaje irrelevante"), False),
    ],
)
def test_ejecutor_agno_clasifica_reintentos(error, reintentable):
    # Arrange
    excepcion = error

    # Act
    resultado = EjecutorAgno._reintentable(excepcion)

    # Assert
    assert resultado is reintentable


def test_ejecutor_agno_gemini_sin_clave_informa_configuracion():
    # Arrange
    ejecutor = EjecutorAgno(_modelo(proveedor="gemini", api_key=None))

    # Act
    with pytest.raises(ConfiguracionProveedorError, match="requiere GOOGLE_API_KEY"):
        ejecutor._crear_modelo()

    # Assert
    assert ejecutor._cfg.proveedor == "gemini"


def test_ejecutor_agno_openai_like_sin_url_o_clave_informa_configuracion():
    # Arrange
    ejecutor = EjecutorAgno(_modelo(proveedor="openai_like", api_key=None))

    # Act
    with pytest.raises(ConfiguracionProveedorError, match="requiere ORQ_API_KEY"):
        ejecutor._crear_modelo()

    # Assert
    assert ejecutor._cfg.proveedor == "openai_like"


def test_log_prueba_escribe_encabezado_y_metricas(tmp_path, monkeypatch):
    # Arrange
    monkeypatch.chdir(tmp_path)
    respuesta = SimpleNamespace(metrics={"prompt_tokens": 7, "completion_tokens": 9})

    # Act
    log_prueba("mock", "modelo", "contenido", respuesta, 1.24)

    # Assert
    with open(tmp_path / "registro_pruebas_siccia.csv", encoding="utf-8") as archivo:
        filas = list(csv.reader(archivo, delimiter=";"))
    assert filas[0][0] == "Fecha"
    assert filas[1][4:6] == ["7", "9"]


def test_log_prueba_lee_usage_y_agrega_fila_sin_encabezado(tmp_path, monkeypatch):
    # Arrange
    monkeypatch.chdir(tmp_path)
    (tmp_path / "registro_pruebas_siccia.csv").write_text("encabezado existente\n", encoding="utf-8")
    respuesta = SimpleNamespace(usage=SimpleNamespace(input_tokens=4, output_tokens=6))

    # Act
    log_prueba("mock", "modelo", "programa", respuesta, 0.5)

    # Assert
    with open(tmp_path / "registro_pruebas_siccia.csv", encoding="utf-8") as archivo:
        filas = list(csv.reader(archivo, delimiter=";"))
    assert filas[0] == ["encabezado existente"]
    assert filas[1][4:6] == ["4", "6"]
