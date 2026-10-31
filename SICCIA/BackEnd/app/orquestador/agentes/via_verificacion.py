from __future__ import annotations

import re
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from ..schemas import Configurador, CursoPlan
from .base import ViaBase


_URL = re.compile(r"https?://[^\s<>\])]+")
_DOMINIOS_CONFIABLES = (
    ".edu",
    ".edu.co",
    ".edu.mx",
    ".edu.ar",
    ".ac.uk",
    ".gov",
    ".gov.co",
    ".gov.uk",
    "ocw.mit.edu",
    "docs.python.org",
    "nasa.gov",
    "who.int",
    "unesco.org",
)


class ViaVerificacion(ViaBase):
    rol = "verificacion"
    archivos_esperados = ("verificacion.md",)
    
    # CAMBIO CLAVE 1: Restricciones negativas fuertes en el system prompt
    instrucciones = (
        "Eres un verificador académico estricto (Fact-Checker) y epistemólogo. "
        "Tu ÚNICO trabajo es validar la VERACIDAD de las afirmaciones históricas, científicas o teóricas. "
        "ESTÁ ESTRICTAMENTE PROHIBIDO hacer revisiones de código, evaluar sintaxis de programación, "
        "ortografía, gramática, estilo pedagógico o formato Markdown. Solo te importan los hechos. "
        "Incluye únicamente fuentes reales y enlaces oficiales que conozcas con certeza."
    )

    def construir_subplantilla(self, config: Configurador, plan: CursoPlan) -> str:
        # CAMBIO CLAVE 2: Enfoque de la tabla hacia "Afirmaciones Factuales"
        return """# Plantilla específica: Verificación de Veracidad

## Tu tarea
Acabas de recibir en la plantilla base el **contenido real** que generó el agente de contenido.
Debes leerlo críticamente enfocándote EXCLUSIVAMENTE en buscar alucinaciones, errores de hechos, anacronismos, datos inventados o imprecisiones científicas.
Ignora por completo el estilo de redacción o el código fuente.
Si el curso incluye matemáticas, comprueba además la exactitud aritmética de cada ejemplo resuelto y
de cada respuesta del taller de práctica del contenido. Registra cada error aritmético en la tabla
de afirmaciones, indicando la operación, el resultado correcto y dónde aparece. No revises estilo ni código.

## Estructura ESTRICTA del documento `verificacion.md`
1. `# Reporte de Verificación Académica`
2. `## Resumen de Fiabilidad`: Un párrafo indicando si los hechos presentados son rigurosos y exactos, o si hay riesgo de desinformación (alucinación).
3. `## Afirmaciones Revisadas`: 
   (Crea una tabla con 3 columnas: "Afirmación Factual o cálculo" / "Estado (Correcto, Impreciso, Falso)" / "Evidencia Científica, operación correcta o corrección").
   *Nota: No evalúes bloques de código ni opiniones, solo hechos concretos.*
4. `## Fuentes verificables`:
   Propón hasta 3 libros, papers, artículos académicos o documentación oficial REALES (incluye autor
   o institución y año comprobable) para respaldar el tema. Cada fuente debe incluir una URL oficial
   completa que empiece por `https://`. NO inventes títulos ni URLs. Si no tienes certeza de que una
   fuente o su URL existe, omítela. El sistema comprobará que la URL responda antes de incluirla.
   Como máximo se comprobarán 10 URLs, con un timeout máximo de 3 segundos por consulta y hasta
   cinco verificaciones simultáneas. Solo se permiten los dominios oficiales indicados por el sistema.
"""

    def _postprocesar_archivo(self, nombre: str, contenido: str) -> str:
        if nombre != "verificacion.md":
            return contenido

        urls = list(dict.fromkeys(_URL.findall(contenido)))
        urls_verificables = urls[:10]
        with ThreadPoolExecutor(max_workers=5) as executor:
            estados = dict(zip(urls_verificables, executor.map(self._url_verificable, urls_verificables)))
        estados.update({url: False for url in urls[10:]})
        lineas = contenido.splitlines()
        resultado: list[str] = []
        for linea in lineas:
            urls_linea = _URL.findall(linea)
            if urls_linea and any(not estados[url] for url in urls_linea):
                continue
            else:
                resultado.append(linea)
        verificados = [url for url in urls if estados[url]]
        resultado.append("")
        resultado.append("## Estado de las URLs")
        if verificados:
            resultado.append("Las siguientes URLs respondieron correctamente durante la generación:")
            resultado.extend(f"- {url}" for url in verificados)
        else:
            resultado.append(
                "No se pudo verificar ninguna URL durante la generación. "
                "No se presentan enlaces como fuentes verificadas."
            )
        return "\n".join(resultado).rstrip() + "\n"

    @staticmethod
    def _dominio_confiable(url: str) -> bool:
        try:
            parsed = urlparse(url)
            if parsed.scheme not in {"http", "https"}:
                return False
            host = (parsed.hostname or "").lower().rstrip(".")
        except ValueError:
            return False
        return any(
            host == dominio.lstrip(".")
            or host.endswith(f".{dominio.lstrip('.')}")
            for dominio in _DOMINIOS_CONFIABLES
        )

    @classmethod
    def _url_verificable(cls, url: str) -> bool:
        return cls._dominio_confiable(url) and cls._url_disponible(url)

    @staticmethod
    def _url_disponible(url: str) -> bool:
        class RedireccionPermitida(HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                if not ViaVerificacion._dominio_confiable(newurl):
                    raise HTTPError(newurl, 403, "Redirección a un dominio no permitido", headers, fp)
                return super().redirect_request(req, fp, code, msg, headers, newurl)

        opener = build_opener(RedireccionPermitida())
        limite = time.monotonic() + 3
        for metodo in ("HEAD", "GET"):
            restante = limite - time.monotonic()
            if restante <= 0:
                return False
            try:
                solicitud = Request(url, method=metodo, headers={"User-Agent": "SICCIA-Verificador/1.0"})
                with opener.open(solicitud, timeout=restante) as respuesta:
                    return 200 <= respuesta.status < 400
            except (OSError, URLError, ValueError):
                if metodo == "GET":
                    return False
        return False