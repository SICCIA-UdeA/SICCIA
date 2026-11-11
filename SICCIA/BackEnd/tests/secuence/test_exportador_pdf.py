import builtins
import importlib
import json
import time
from types import SimpleNamespace

import pytest

from app.orquestador import exportador_pdf as pdf
from app.orquestador.agentes.base import ArchivoGenerado


def test_exportador_separar_listas_pegadas_divide_opciones():
    # Arrange
    texto = "Pregunta - a) Uno - b) Dos - c) Tres"

    # Act
    resultado = pdf.separar_listas_pegadas(texto)

    # Assert
    assert "Pregunta\n\n- a) Uno\n- b) Dos\n- c) Tres" == resultado


def test_exportador_separar_listas_no_modifica_bloque_de_codigo():
    # Arrange
    texto = "```text\n- uno - dos - tres\n```"

    # Act
    resultado = pdf.separar_listas_pegadas(texto)

    # Assert
    assert resultado == texto


@pytest.mark.parametrize(
    ("cuerpo", "cantidad"),
    [("Pregunta - a) Uno - b) Dos", 3), ("Uno - Dos - Tres", 3), ("Uno - Dos", None)],
)
def test_exportador_partir_detecta_opciones_y_listas(cuerpo, cantidad):
    # Arrange
    texto = cuerpo

    # Act
    resultado = pdf._partir(texto)

    # Assert
    assert len(resultado) == cantidad if resultado is not None else cantidad is None


@pytest.mark.parametrize(
    ("linea", "esperado"),
    [
        ("1. Texto", ("1. ", "Texto")),
        ("  12.   x", ("  12.   ", "x")),
        ("1. ", ("1. ", "")),
        ("1.", None),
        ("a. x", None),
        ("1.x", None),
    ],
)
def test_exportador_parsear_numerado_reconoce_formato(linea, esperado):
    # Arrange

    # Act
    resultado = pdf._parsear_numerado(linea)

    # Assert
    assert resultado == esperado


def test_exportador_separador_divide_tres_partes_y_rechaza_una():
    # Arrange

    # Act
    tres_partes = pdf._partir("Pregunta - A) uno - B) dos")
    una_parte = pdf._partir("Pregunta - A")

    # Assert
    assert tres_partes == ["Pregunta", "A) uno", "B) dos"]
    assert una_parte is None


def test_exportador_parsear_numerado_entrada_adversa_responde_en_tiempo_lineal():
    # Arrange
    linea = "1." + " " * 50_000 + "x" * 50_000

    # Act
    inicio = time.perf_counter()
    resultado = pdf._parsear_numerado(linea)

    # Assert
    assert resultado == ("1." + " " * 50_000, "x" * 50_000)
    assert time.perf_counter() - inicio < 1


def test_exportador_separador_entrada_adversa_responde_en_tiempo_lineal():
    # Arrange
    texto = "a" + " " * 50_000 + "b"

    # Act
    inicio = time.perf_counter()
    resultado = pdf._RE_SEPARADOR.split(texto)

    # Assert
    assert resultado == [texto]
    assert time.perf_counter() - inicio < 1


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("- Uno - Dos - Tres", "- Uno\n- Dos\n- Tres"),
        ("1. Pregunta\n- Uno\n- Dos", "1. Pregunta\n\n    - Uno\n    - Dos"),
        ("Texto\n## Título\n| tabla |", "Texto\n\n## Título\n| tabla |"),
        ("Texto\n\nContinuación", "Texto\n\nContinuación"),
    ],
)
def test_exportador_separar_listas_maneja_niveles_y_limites(texto, esperado):
    # Arrange
    entrada = texto

    # Act
    resultado = pdf.separar_listas_pegadas(entrada)

    # Assert
    assert resultado == esperado


def test_exportador_fracciones_no_modifica_codigo():
    # Arrange
    html = "<p>1/2</p><code>3/4</code>"

    # Act
    resultado = pdf._estilizar_fracciones(html)

    # Assert
    assert "class='frac'" in resultado
    assert "<code>3/4</code>" in resultado


def test_exportador_portada_escapa_datos_del_configurador(tmp_path):
    # Arrange
    interno = tmp_path / "interno"
    interno.mkdir()
    (interno / "configurador.json").write_text(
        json.dumps({"datos": {"tema": "<Curso>", "publico_objetivo": "Primaria"}}),
        encoding="utf-8",
    )

    # Act
    portada = pdf._portada(tmp_path / "resultados")

    # Assert
    assert "&lt;Curso&gt;" in portada
    assert "Primaria" in portada


def test_exportador_portada_sin_configuracion_devuelve_vacio(tmp_path):
    # Arrange
    directorio = tmp_path / "resultados"

    # Act
    portada = pdf._portada(directorio)

    # Assert
    assert portada == ""


@pytest.mark.parametrize(
    ("nombre", "texto", "esperado"),
    [
        ("evaluaciones.md", "Pregunta\nRespuesta correcta: A\n## Solucionario\nA", "Pregunta"),
        ("contenido_curso.md", "Tema\nRespuestas orientativas\nA\n# Cierre", "# Cierre"),
        ("programa_curso.md", "Respuesta correcta: A", "Respuesta correcta: A"),
    ],
)
def test_exportador_filtra_documentos_estudiante(nombre, texto, esperado):
    # Arrange
    documento = texto

    # Act
    resultado = pdf.filtrar_contenido_estudiante(nombre, documento)

    # Assert
    assert esperado in resultado


def test_exportador_pdf_falso_genera_documentos_por_markdown(tmp_path, monkeypatch):
    # Arrange
    class HtmlFalso:
        def __init__(self, string, base_url):
            self.string = string

        def write_pdf(self, destino):
            destino.write_bytes(b"PDF de prueba")

    monkeypatch.setattr(pdf, "HTML", HtmlFalso)
    monkeypatch.setattr(pdf, "WEASYPRINT_OK", True)
    monkeypatch.setattr(
        pdf,
        "markdown",
        SimpleNamespace(markdown=lambda texto, extensions: f"<p>{texto}</p>"),
    )
    archivo = ArchivoGenerado("curso.md", "# Curso\n", "contenido")
    (tmp_path / "curso.md").write_text(archivo.contenido, encoding="utf-8")

    # Act
    generados, errores = pdf.procesar_imagenes_y_pdf(tmp_path, {"curso.md": archivo})

    # Assert
    assert generados == ["curso.pdf"]
    assert not errores
    assert (tmp_path / "curso.pdf").read_bytes() == b"PDF de prueba"


def test_exportador_pdf_registra_error_sin_detener_otros_archivos(tmp_path, monkeypatch):
    # Arrange
    class HtmlSelectivo:
        def __init__(self, string, base_url):
            self.string = string

        def write_pdf(self, destino):
            if destino.name == "malo.pdf":
                raise OSError("conversión fallida")
            destino.write_bytes(b"PDF")

    monkeypatch.setattr(pdf, "HTML", HtmlSelectivo)
    monkeypatch.setattr(pdf, "WEASYPRINT_OK", True)
    monkeypatch.setattr(
        pdf,
        "markdown",
        SimpleNamespace(markdown=lambda texto, extensions: f"<p>{texto}</p>"),
    )
    archivos = {
        "malo.md": ArchivoGenerado("malo.md", "# Malo", "contenido"),
        "bueno.md": ArchivoGenerado("bueno.md", "# Bueno", "contenido"),
    }

    # Act
    generados, errores = pdf.procesar_imagenes_y_pdf(tmp_path, archivos)

    # Assert
    assert generados == ["bueno.pdf"]
    assert "malo.md: conversión fallida" in errores


def test_exportador_pdf_sin_markdown_devuelve_error_claro(tmp_path, monkeypatch):
    # Arrange
    monkeypatch.setattr(pdf, "WEASYPRINT_OK", True)
    monkeypatch.setattr(pdf, "markdown", None)

    # Act
    generados, errores = pdf.procesar_imagenes_y_pdf(
        tmp_path, {"curso.md": ArchivoGenerado("curso.md", "# Curso", "contenido")}
    )

    # Assert
    assert generados == []
    assert "biblioteca markdown" in errores[0]


def test_exportador_pdf_sin_archivos_markdown_informa_error(tmp_path, monkeypatch):
    # Arrange
    monkeypatch.setattr(pdf, "WEASYPRINT_OK", True)
    monkeypatch.setattr(
        pdf, "markdown", SimpleNamespace(markdown=lambda texto, extensions: f"<p>{texto}</p>")
    )

    # Act
    generados, errores = pdf.procesar_imagenes_y_pdf(tmp_path, {})

    # Assert
    assert generados == []
    assert errores == ["No hay archivos Markdown para convertir en PDF."]


def test_exportador_pdf_version_estudiante_filtra_solucionario(tmp_path, monkeypatch):
    # Arrange
    documentos = []

    class HtmlCapturador:
        def __init__(self, string, base_url):
            documentos.append(string)

        def write_pdf(self, destino):
            destino.write_bytes(b"PDF")

    monkeypatch.setattr(pdf, "HTML", HtmlCapturador)
    monkeypatch.setattr(pdf, "WEASYPRINT_OK", True)
    monkeypatch.setattr(
        pdf, "markdown", SimpleNamespace(markdown=lambda texto, extensions: f"<p>{texto}</p>")
    )
    monkeypatch.setattr(pdf, "GENERAR_VERSION_ESTUDIANTE", True)
    contenido = "# Quiz\nPregunta\n## Solucionario\nRespuesta"
    archivo = ArchivoGenerado("evaluaciones.md", contenido, "evaluacion")

    # Act
    generados, errores = pdf.procesar_imagenes_y_pdf(tmp_path, {"evaluaciones.md": archivo})

    # Assert
    assert generados == ["evaluaciones_estudiante.pdf", "evaluaciones_docente.pdf"]
    assert not errores
    assert "Respuesta" not in documentos[0]
    assert "Respuesta" in documentos[1]


def test_exportador_pdf_bloquea_si_falta_weasyprint(tmp_path, monkeypatch):
    # Arrange
    monkeypatch.setattr(pdf, "WEASYPRINT_OK", False)
    monkeypatch.setattr(pdf, "WEASYPRINT_ERROR", "dependencia nativa")

    # Act
    generados, errores = pdf.procesar_imagenes_y_pdf(
        tmp_path, {"curso.md": ArchivoGenerado("curso.md", "# Curso", "contenido")}
    )

    # Assert
    assert not generados
    assert "dependencia nativa" in errores[0]


def test_exportador_pdf_importacion_oseerror_no_rompe_modulo(monkeypatch):
    # Arrange
    importar_original = builtins.__import__

    def importar_con_error(nombre, *args, **kwargs):
        if nombre == "weasyprint":
            raise OSError("Pango no disponible")
        return importar_original(nombre, *args, **kwargs)

    # Act
    with monkeypatch.context() as parche:
        parche.setattr(builtins, "__import__", importar_con_error)
        modulo = importlib.reload(pdf)
        disponibilidad = modulo.WEASYPRINT_OK
        detalle = modulo.WEASYPRINT_ERROR
    importlib.reload(pdf)

    # Assert
    assert disponibilidad is False
    assert "Pango no disponible" in detalle
