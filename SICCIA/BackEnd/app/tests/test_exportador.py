from app.orquestador.exportador_pdf import (
    filtrar_contenido_estudiante,
    procesar_imagenes_y_pdf,
    separar_listas_pegadas,
)


def test_separar_listas_pegadas_separa_pregunta_y_opciones():
    texto = "1. ¿Cuál es la respuesta? - A) Primera - B) Segunda"

    resultado = separar_listas_pegadas(texto)

    assert "1. ¿Cuál es la respuesta?\n\n" in resultado
    assert "- A) Primera" in resultado
    assert "- B) Segunda" in resultado


def test_filtro_estudiante_conserva_cierre_del_modulo():
    texto = (
        "# Módulo\n\n"
        "Explicación para el curso.\n\n"
        "Respuestas orientativas\n\n"
        "La respuesta esperada es fracción.\n\n"
        "Cierre del módulo: resume lo aprendido.\n"
    )

    resultado = filtrar_contenido_estudiante("contenido_curso.md", texto)

    assert "Respuestas orientativas" not in resultado
    assert "La respuesta esperada" not in resultado
    assert "Cierre del módulo" in resultado


def test_filtro_estudiante_elimina_solucionario_hasta_el_final():
    texto = (
        "# Evaluaciones\n\n"
        "Actividad 1.\n\n"
        "## Solucionario\n\n"
        "Respuesta correcta: A\n"
        "Justificación: porque es correcta.\n"
    )

    resultado = filtrar_contenido_estudiante("evaluaciones.md", texto)

    assert resultado.rstrip() == "# Evaluaciones\n\nActividad 1."


def test_estudiante_no_contiene_respuestas_y_docente_si():
    texto = (
        "Actividad.\n\n"
        "Respuesta correcta: B\n"
        "Justificación: se ajusta al tema.\n\n"
        "## Solucionario\n\n"
        "Respuestas orientativas: revisar el ejemplo.\n"
    )

    estudiante = filtrar_contenido_estudiante("evaluaciones.md", texto)
    docente = texto

    assert all(
        marca not in estudiante
        for marca in (
            "Respuesta correcta",
            "Justificación",
            "Solucionario",
            "Respuestas orientativas",
        )
    )
    assert all(marca in docente for marca in (
        "Respuesta correcta",
        "Justificación",
        "Solucionario",
        "Respuestas orientativas",
    ))


def test_archivo_no_especificado_no_se_filtra():
    texto = "Respuesta correcta: A\nSolucionario\n"

    assert filtrar_contenido_estudiante("verificacion.md", texto) == texto


def test_genera_dos_versiones_con_la_constante_activa(tmp_path, monkeypatch):
    import app.orquestador.exportador_pdf as exportador

    monkeypatch.setattr(exportador, "GENERAR_VERSION_ESTUDIANTE", True)
    monkeypatch.setattr(exportador, "WEASYPRINT_OK", True)

    class HtmlFalso:
        def __init__(self, string, base_url):
            self.string = string
            self.base_url = base_url

        def write_pdf(self, ruta):
            ruta.write_bytes(b"%PDF")

    monkeypatch.setattr(exportador, "HTML", HtmlFalso)
    archivo = type("Archivo", (), {"contenido": "# Curso"})()

    procesar_imagenes_y_pdf(tmp_path, {"contenido_curso.md": archivo})

    assert sorted(p.name for p in tmp_path.glob("*.pdf")) == [
        "contenido_curso_docente.pdf",
        "contenido_curso_estudiante.pdf",
    ]


def test_genera_un_pdf_original_con_la_constante_inactiva(tmp_path, monkeypatch):
    import app.orquestador.exportador_pdf as exportador

    monkeypatch.setattr(exportador, "GENERAR_VERSION_ESTUDIANTE", False)
    monkeypatch.setattr(exportador, "WEASYPRINT_OK", True)

    class HtmlFalso:
        def __init__(self, string, base_url):
            self.string = string
            self.base_url = base_url

        def write_pdf(self, ruta):
            ruta.write_bytes(b"%PDF")

    monkeypatch.setattr(exportador, "HTML", HtmlFalso)
    archivo = type("Archivo", (), {"contenido": "# Curso"})()

    procesar_imagenes_y_pdf(tmp_path, {"contenido_curso.md": archivo})

    assert [p.name for p in tmp_path.glob("*.pdf")] == ["contenido_curso.pdf"]


def test_filtro_estudiante_cubre_respuestas_de_contenido_y_evaluaciones():
    contenido = (
        "Explicación del tema.\n\n"
        "Respuestas orientativas\n\n"
        "Respuesta sugerida: 3/4.\n"
        "Continúa la explicación de la respuesta.\n\n"
        "## Siguiente sección\n\n"
        "Texto visible para estudiantes.\n\n"
        "Cierre del módulo: actividad de cierre.\n"
    )
    evaluaciones = (
        "## Actividad 1\n\n"
        "Respuesta correcta: B\n"
        "Justificación: se relaciona con el tema.\n\n"
        "Solucionario\n\n"
        "Respuesta correcta: A\n"
        "Justificación: explicación docente.\n"
    )

    contenido_estudiante = filtrar_contenido_estudiante("contenido_curso.md", contenido)
    evaluaciones_estudiante = filtrar_contenido_estudiante("evaluaciones.md", evaluaciones)

    assert "Respuesta sugerida" not in contenido_estudiante
    assert "Siguiente sección" in contenido_estudiante
    assert "Cierre del módulo" in contenido_estudiante
    assert "Respuesta correcta" not in evaluaciones_estudiante
    assert "Justificación" not in evaluaciones_estudiante
    assert "Solucionario" not in evaluaciones_estudiante
