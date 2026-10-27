"""Convierte los .md del curso en PDF con una plantilla CSS fija.

El agente escribe solo el contenido en Markdown; el diseño vive en plantilla_pdf.css.
Antes de convertir:
- se separan las listas y las opciones A-D que llegaron pegadas o sin línea en blanco;
- se agrega una portada con los datos del configurador (interno/configurador.json);
- las fracciones a/b se muestran apiladas, fuera de los bloques de código.
"""
import html as htmllib
import json
import re
from pathlib import Path

import markdown

try:
    from weasyprint import HTML
    WEASYPRINT_OK = True
except ImportError:
    WEASYPRINT_OK = False

RUTA_CSS = Path(__file__).with_name("plantilla_pdf.css")
GENERAR_VERSION_ESTUDIANTE = False
_RE_IMG = re.compile(r"!\[(.*?)\]\(unsplash:(.*?)\)")
_RE_SEPARADOR = re.compile(r"\s+-\s+(?=\S)")
_RE_NUMERADO = re.compile(r"^(\s*\d+\.\s+)(.*)$")
_RE_OPCION = re.compile(r"^[A-Da-d][\)\.]\s")
_RE_CODIGO_HTML = re.compile(r"(<pre>.*?</pre>|<code>.*?</code>)", re.S)
_RE_FRACCION = re.compile(r"(?<![\w/.])(\d{1,4})/(\d{1,4})(?![\w/.])")

CSS_EXTRA = """
.portada { padding-top: 6.5cm; page-break-after: always; }
.portada .etiqueta { font-size: 9pt; letter-spacing: 2px; text-transform: uppercase; color: #0e7490; margin: 0 0 14px 0; }
.portada h1 { font-size: 30pt; line-height: 1.2; border-bottom: none; padding-bottom: 0; margin: 0; }
.portada .linea { width: 90px; height: 4px; background: #0e7490; margin: 22px 0; }
.portada .meta p { margin: 0 0 6px 0; font-size: 11pt; color: #374151; }
.portada .meta strong { color: #0f3d66; }
.frac { display: inline-block; vertical-align: middle; text-align: center; font-size: 0.9em; line-height: 1.1; margin: 0 2px; }
.frac .num { display: block; border-bottom: 1px solid currentColor; padding: 0 3px 1px 3px; }
.frac .den { display: block; padding: 1px 3px 0 3px; }
"""


def _escapar(valor) -> str:
    return htmllib.escape(str(valor))


def obtener_imagen_unsplash(palabras_clave: str) -> str:
    """URL para un marcador unsplash:. Source Unsplash está retirado: revisar antes de activar imágenes."""
    terminos = palabras_clave.strip().replace(" ", ",")
    return f"https://source.unsplash.com/800x400/?{terminos}"


def _partir(cuerpo: str):
    """Parte un texto por ' - '. Devuelve None si no parece una lista pegada."""
    partes = [p.strip() for p in _RE_SEPARADOR.split(cuerpo) if p.strip()]
    if len(partes) >= 2 and any(_RE_OPCION.match(p) for p in partes[1:]):
        return partes  # pregunta seguida de opciones A), B), C)...
    if len(partes) >= 3:
        return partes  # ítems de una lista pegados en una sola línea
    return None


def separar_listas_pegadas(texto: str) -> str:
    """Pone cada opción o ítem en su línea, con las líneas en blanco que Markdown necesita.

    No toca bloques de código, títulos, tablas ni citas.
    """
    salida = []
    en_codigo = False
    previa = ""      # tipo de la última línea emitida: "numerado", "item", "texto" o "" (vacía, título, código)
    anidada = False  # True cuando los ítems van bajo una pregunta numerada

    for linea in texto.split("\n"):
        if linea.lstrip().startswith("```"):
            en_codigo = not en_codigo
            salida.append(linea)
            previa = ""
            continue
        if en_codigo:
            salida.append(linea)
            continue
        if not linea.strip():
            salida.append(linea)
            previa = ""
            continue
        if linea.lstrip().startswith(("#", "|", ">", "*")):
            if previa:
                salida.append("")
            salida.append(linea)
            previa = ""
            anidada = False
            continue

        strip = linea.strip()
        if strip.startswith("- "):
            tipo, prefijo, cuerpo = "item", "", strip[2:]
        else:
            m = _RE_NUMERADO.match(linea)
            if m:
                tipo, prefijo, cuerpo = "numerado", m.group(1), m.group(2)
            else:
                tipo, prefijo, cuerpo = "texto", "", strip

        partes = _partir(cuerpo)

        if tipo == "item":
            items = partes or [cuerpo]
            if previa == "numerado":
                salida.append("")
                sangria = "    "
                anidada = True
            elif previa == "item":
                sangria = "    " if anidada else ""
            else:
                if previa:
                    salida.append("")
                sangria = ""
                anidada = False
            for it in items:
                salida.append(f"{sangria}- {it}")
            previa = "item"
            continue

        # Línea numerada o de texto: puede traer opciones pegadas detrás.
        if partes:
            cabecera = prefijo + partes[0]
            items = partes[1:]
        else:
            cabecera = prefijo + cuerpo if tipo == "numerado" else cuerpo
            items = []

        if previa and ((tipo == "numerado" and previa != "numerado") or (tipo == "texto" and previa == "item")):
            salida.append("")
        salida.append(cabecera)
        previa = tipo

        if items:
            salida.append("")
            sangria = "    " if tipo == "numerado" else ""
            for it in items:
                salida.append(f"{sangria}- {it}")
            previa = "item"
            anidada = tipo == "numerado"

    return "\n".join(salida)


def _estilizar_fracciones(html: str) -> str:
    """Muestra a/b como fracción apilada, sin tocar código ni el contenido de las etiquetas code."""
    partes = _RE_CODIGO_HTML.split(html)
    for i in range(0, len(partes), 2):  # los índices pares son texto fuera de código
        partes[i] = _RE_FRACCION.sub(
            lambda m: (
                f"<span class='frac'><span class='num'>{m.group(1)}</span>"
                f"<span class='den'>{m.group(2)}</span></span>"
            ),
            partes[i],
        )
    return "".join(partes)


def _portada(directorio_trabajo: Path) -> str:
    """HTML de la portada con los datos del configurador. Vacío si no hay configurador guardado."""
    ruta = directorio_trabajo.parent / "interno" / "configurador.json"
    if not ruta.exists():
        return ""
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8")).get("datos", {})
    except (OSError, ValueError):
        return ""
    tema = datos.get("tema") or "Curso"
    campos = [
        ("Público", datos.get("publico_objetivo")),
        ("Duración", datos.get("duracion_estimada")),
        ("Metodología", datos.get("metodologia")),
    ]
    meta = "".join(f"<p><strong>{etiqueta}:</strong> {_escapar(valor)}</p>" for etiqueta, valor in campos if valor)
    return (
        "<section class='portada'>"
        "<div class='etiqueta'>Curso</div>"
        f"<h1>{_escapar(tema)}</h1>"
        "<div class='linea'></div>"
        f"<div class='meta'>{meta}</div>"
        "</section>"
    )


def filtrar_contenido_estudiante(nombre: str, texto: str) -> str:
    """Retira las respuestas y solucionarios de la versión para estudiantes."""
    if nombre == "evaluaciones.md":
        lineas = []
        for linea in texto.splitlines():
            if "Solucionario" in linea:
                break
            if linea.lstrip().startswith(("Respuesta correcta", "Justificación")):
                continue
            lineas.append(linea)
        return "\n".join(lineas)

    if nombre != "contenido_curso.md":
        return texto

    lineas = texto.splitlines()
    salida = []
    omitiendo_respuestas = False
    for linea in lineas:
        inicio = linea.strip()
        if not omitiendo_respuestas and inicio.startswith("Respuestas orientativas"):
            omitiendo_respuestas = True
            continue
        if omitiendo_respuestas:
            if inicio.startswith("#") or inicio.startswith("Cierre del módulo"):
                omitiendo_respuestas = False
            else:
                continue
        salida.append(linea)
    return "\n".join(salida)


def procesar_imagenes_y_pdf(directorio_trabajo: Path, archivos_generados: dict) -> None:
    """Genera versiones para estudiantes y docentes de cada Markdown."""
    if not WEASYPRINT_OK:
        print("WeasyPrint no está instalado: no se generan PDF.")
        return
    css = RUTA_CSS.read_text(encoding="utf-8") + CSS_EXTRA
    portada = _portada(directorio_trabajo)
    for nombre, archivo in archivos_generados.items():
        if not nombre.endswith(".md"):
            continue
        versiones = (
            (
                ("estudiante", filtrar_contenido_estudiante(nombre, archivo.contenido)),
                ("docente", archivo.contenido),
            )
            if GENERAR_VERSION_ESTUDIANTE
            else (("completo", archivo.contenido),)
        )
        for audiencia, contenido in versiones:
            texto = _RE_IMG.sub(
                lambda m: f"![{m.group(1)}]({obtener_imagen_unsplash(m.group(2))})",
                contenido,
            )
            texto = separar_listas_pegadas(texto)
            cuerpo = markdown.markdown(texto, extensions=["tables", "fenced_code", "sane_lists"])
            cuerpo = _estilizar_fracciones(cuerpo)
            documento = (
                "<!DOCTYPE html><html lang='es'><head><meta charset='utf-8'>"
                f"<style>{css}</style></head><body>{portada}{cuerpo}</body></html>"
            )
            sufijo = f"_{audiencia}" if GENERAR_VERSION_ESTUDIANTE else ""
            ruta_pdf = directorio_trabajo / nombre.replace(".md", f"{sufijo}.pdf")
            HTML(string=documento, base_url=str(directorio_trabajo)).write_pdf(ruta_pdf)
            print(f"PDF generado: {ruta_pdf.name}")