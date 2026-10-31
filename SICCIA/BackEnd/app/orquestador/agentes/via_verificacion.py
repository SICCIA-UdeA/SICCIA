from __future__ import annotations

import re
from urllib.error import URLError
from urllib.request import Request, urlopen
from urllib.parse import urlparse

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

## Estructura ESTRICTA del documento `verificacion.md`
1. `# Reporte de Verificación Académica`
2. `## Resumen de Fiabilidad`: Un párrafo indicando si los hechos presentados son rigurosos y exactos, o si hay riesgo de desinformación (alucinación).
3. `## Afirmaciones Revisadas`: 
   (Crea una tabla con 3 columnas: "Afirmación Factual" / "Estado (Correcto, Impreciso, Falso)" / "Evidencia Científica o Corrección").
   *Nota: No evalúes bloques de código ni opiniones, solo hechos concretos.*
4. `## Fuentes verificables`:
   Propón hasta 3 libros, papers, artículos académicos o documentación oficial REALES (incluye autor
   o institución y año comprobable) para respaldar el tema. Cada fuente debe incluir una URL oficial
   completa que empiece por `https://`. NO inventes títulos ni URLs. Si no tienes certeza de que una
   fuente o su URL existe, omítela. El sistema comprobará que la URL responda antes de incluirla.
"""

    def _postprocesar_archivo(self, nombre: str, contenido: str) -> str:
        if nombre != "verificacion.md":
            return contenido

        urls = list(dict.fromkeys(_URL.findall(contenido)))
        estados = {url: self._url_verificable(url) for url in urls}
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
            host = (urlparse(url).hostname or "").lower().rstrip(".")
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
        try:
            solicitud = Request(url, method="HEAD", headers={"User-Agent": "SICCIA-Verificador/1.0"})
            with urlopen(solicitud, timeout=5) as respuesta:
                return 200 <= respuesta.status < 400
        except (OSError, URLError, ValueError):
            try:
                solicitud = Request(url, method="GET", headers={"User-Agent": "SICCIA-Verificador/1.0"})
                with urlopen(solicitud, timeout=5) as respuesta:
                    return 200 <= respuesta.status < 400
            except (OSError, URLError, ValueError):
                return False