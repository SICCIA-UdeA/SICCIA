import asyncio
import threading
import time
from urllib.error import HTTPError

import pytest

from app.orquestador.agentes import via_verificacion
from app.orquestador.agentes.base import ViaBase, normalizar_notacion_matematica
from app.orquestador.agentes.via_evaluacion import ViaEvaluacion
from app.orquestador.agentes.via_verificacion import ViaVerificacion
from tests.factories import FakeEjecutor


def test_via_separar_archivos_reconoce_marcadores_y_cercas():
    # Arrange
    via = ViaEvaluacion(FakeEjecutor())
    respuesta = "<!-- ARCHIVO: evaluaciones.md -->\n```markdown\n# Quiz\n```"

    # Act
    archivos = via._separar_archivos(respuesta)

    # Assert
    assert archivos["evaluaciones.md"] == "# Quiz\n"


def test_via_separar_archivos_sin_marcadores_usa_primer_archivo():
    # Arrange
    via = ViaEvaluacion(FakeEjecutor())

    # Act
    archivos = via._separar_archivos("# Respuesta sin marcador")

    # Assert
    assert archivos == {"evaluaciones.md": "# Respuesta sin marcador\n"}


def test_via_separar_archivos_ignora_nombre_no_esperado():
    # Arrange
    via = ViaEvaluacion(FakeEjecutor())

    # Act
    archivos = via._separar_archivos("<!-- ARCHIVO: desconocido.md -->\nignorado")

    # Assert
    assert "desconocido.md" not in archivos


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("```markdown\nhola\n```", "hola\n"),
        ("```md\n\n  hola\n```", "hola\n"),
        ("texto sin cerca", "texto sin cerca\n"),
        ("```python\ncodigo\n```", "```python\ncodigo\n```\n"),
    ],
)
def test_via_limpiar_reconoce_cercas_markdown_y_conserva_otras(texto, esperado):
    # Arrange
    via = ViaEvaluacion(FakeEjecutor())

    # Act
    resultado = via._limpiar(texto)

    # Assert
    assert resultado == esperado


def test_via_limpiar_entrada_adversa_responde_en_tiempo_lineal():
    # Arrange
    via = ViaEvaluacion(FakeEjecutor())
    texto = "```\n" + "\n" * 50_000 + "x"
    inicio = time.perf_counter()

    # Act
    resultado = via._limpiar(texto)

    # Assert
    assert resultado.endswith("\n")
    assert time.perf_counter() - inicio < 1


@pytest.mark.parametrize("texto", ["None", "null"])
def test_via_separar_archivos_respuesta_nula_lanza_error(texto):
    # Arrange
    via = ViaEvaluacion(FakeEjecutor())

    # Act
    with pytest.raises(ValueError, match="respuesta nula") as error:
        via._separar_archivos(texto)

    # Assert
    assert "respuesta nula" in str(error.value)


@pytest.mark.xfail(strict=True, reason="BUG: la vía acepta respuestas vacías y debería rechazarlas")
@pytest.mark.xfail_bug
def test_via_separar_archivos_respuesta_vacia_deberia_lanzar_error():
    # Arrange
    via = ViaEvaluacion(FakeEjecutor())

    # Act
    with pytest.raises(ValueError, match="respuesta nula"):
        via._separar_archivos("")

    # Assert
    assert via.archivos_esperados == ("evaluaciones.md",)


def test_normalizar_notacion_matematica_convierte_simbolos():
    # Arrange
    texto = r"$x$ + \frac{1}{2} + \sqrt{4} + \times"

    # Act
    resultado = normalizar_notacion_matematica(texto)

    # Assert
    assert resultado == "x + (1)/(2) + √(4) + ×"


def test_evaluacion_postprocesa_opciones_y_separacion_de_respuestas():
    # Arrange
    via = ViaEvaluacion(FakeEjecutor())
    texto = (
        "# Quiz\nPregunta a) uno b) dos\nRespuesta correcta: a)\n"
        "Justificación: comprobación\n## Solucionario\nRespuesta previa"
    )

    # Act
    resultado = via._postprocesar_archivo("evaluaciones.md", texto)

    # Assert
    assert "Respuesta correcta: a)" not in resultado.split("## Solucionario")[0]
    solucionario = resultado.split("## Solucionario", maxsplit=1)[1]
    assert "Justificación: comprobación" in solucionario
    assert "a) uno" in resultado and "b) dos" in resultado


def test_evaluacion_sin_solucionario_crea_seccion_de_respuestas():
    # Arrange
    via = ViaEvaluacion(FakeEjecutor())

    # Act
    resultado = via._postprocesar_archivo("evaluaciones.md", "# Quiz")

    # Assert
    assert "## Solucionario" in resultado
    assert "Completar el solucionario" in resultado


def test_verificacion_filtra_urls_no_confiables_y_anexa_estado(monkeypatch):
    # Arrange
    via = ViaVerificacion(FakeEjecutor())
    monkeypatch.setattr(via, "_url_verificable", lambda url: "universidad.edu" in url)
    texto = "Fuente https://universidad.edu/recurso\nOtra https://example.com/falso"

    # Act
    resultado = via._postprocesar_archivo("verificacion.md", texto)

    # Assert
    assert "universidad.edu/recurso" in resultado
    assert "example.com" not in resultado
    assert "## Estado de las URLs" in resultado


def test_verificacion_dominio_confiable_valida_host_y_esquema():
    # Arrange
    urls = ("https://campus.edu.co/recurso", "https://example.com/recurso", "ftp://docs.python.org")

    # Act
    resultados = [ViaVerificacion._dominio_confiable(url) for url in urls]

    # Assert
    assert resultados == [True, False, False]


def test_verificacion_dominio_malformado_no_es_confiable():
    # Arrange
    url = "https://["

    # Act
    resultado = ViaVerificacion._dominio_confiable(url)

    # Assert
    assert resultado is False


def test_verificacion_url_no_confiable_no_consulta_red(monkeypatch):
    # Arrange
    monkeypatch.setattr(
        ViaVerificacion,
        "_url_disponible",
        staticmethod(lambda url: (_ for _ in ()).throw(AssertionError(url))),
    )

    # Act
    resultado = ViaVerificacion._url_verificable("https://example.com/fuente")

    # Assert
    assert resultado is False


def test_verificacion_url_disponible_usa_head_y_acepta_200(monkeypatch):
    # Arrange
    metodos = []

    class Respuesta:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

    class Opener:
        def open(self, solicitud, timeout):
            metodos.append(solicitud.get_method())
            return Respuesta()

    monkeypatch.setattr(via_verificacion, "build_opener", lambda *args: Opener())

    # Act
    resultado = ViaVerificacion._url_disponible("https://universidad.edu/fuente")

    # Assert
    assert resultado is True
    assert metodos == ["HEAD"]


def test_verificacion_url_disponible_reintenta_get_despues_de_head(monkeypatch):
    # Arrange
    metodos = []

    class Respuesta:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

    class Opener:
        def open(self, solicitud, timeout):
            metodos.append(solicitud.get_method())
            if solicitud.get_method() == "HEAD":
                raise HTTPError(solicitud.full_url, 405, "método no permitido", None, None)
            return Respuesta()

    monkeypatch.setattr(via_verificacion, "build_opener", lambda *args: Opener())

    # Act
    resultado = ViaVerificacion._url_disponible("https://universidad.edu/fuente")

    # Assert
    assert resultado is True
    assert metodos == ["HEAD", "GET"]


def test_verificacion_url_disponible_respuesta_error_devuelve_false(monkeypatch):
    # Arrange
    class Respuesta:
        status = 404

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

    class Opener:
        def open(self, solicitud, timeout):
            return Respuesta()

    monkeypatch.setattr(via_verificacion, "build_opener", lambda *args: Opener())

    # Act
    resultado = ViaVerificacion._url_disponible("https://universidad.edu/fuente")

    # Assert
    assert resultado is False


def test_verificacion_rechaza_redireccion_a_dominio_no_confiable(monkeypatch):
    # Arrange
    handlers = []

    class Opener:
        def open(self, solicitud, timeout):
            class Respuesta:
                status = 200

                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    return None

            return Respuesta()

    monkeypatch.setattr(
        via_verificacion,
        "build_opener",
        lambda handler: handlers.append(handler) or Opener(),
    )

    # Act
    ViaVerificacion._url_disponible("https://universidad.edu/fuente")
    with pytest.raises(HTTPError, match="dominio no permitido"):
        handlers[0].redirect_request(None, None, 302, "redirect", None, "https://example.com/fuente")

    # Assert
    assert len(handlers) == 1


def test_verificacion_omite_urls_mas_alla_del_limite(monkeypatch):
    # Arrange
    via = ViaVerificacion(FakeEjecutor())
    llamadas = []
    monkeypatch.setattr(via, "_url_verificable", lambda url: llamadas.append(url) or True)
    texto = "\n".join(f"Fuente https://ciencia.edu/{indice}" for indice in range(11))

    # Act
    resultado = via._postprocesar_archivo("verificacion.md", texto)

    # Assert
    assert len(llamadas) == 10
    assert "https://ciencia.edu/10" not in resultado


def test_verificacion_otro_archivo_no_modifica_contenido():
    # Arrange
    via = ViaVerificacion(FakeEjecutor())
    contenido = "Documento sin validar"

    # Act
    resultado = via._postprocesar_archivo("otro.md", contenido)

    # Assert
    assert resultado == contenido


async def test_verificacion_postproceso_no_bloquea_event_loop(monkeypatch):
    # Arrange
    barrera = threading.Barrier(2)

    def esperar_red(_url):
        barrera.wait()
        return True

    via = ViaVerificacion(FakeEjecutor())
    monkeypatch.setattr(via, "_url_verificable", esperar_red)

    # Act
    resultado, latido = await asyncio.gather(
        asyncio.to_thread(
            via._postprocesar_archivo, "verificacion.md", "Fuente https://ciencia.edu/fuente"
        ),
        asyncio.to_thread(barrera.wait),
    )

    # Assert
    assert latido in (0, 1)
    assert "Estado de las URLs" in resultado


def test_via_base_es_abstracta():
    # Arrange
    clase = ViaBase

    # Act
    with pytest.raises(TypeError):
        clase(FakeEjecutor())

    # Assert
    assert clase.__abstractmethods__
