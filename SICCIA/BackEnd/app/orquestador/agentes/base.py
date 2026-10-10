"""Clase base de las tres vías de trabajo.

Cada vía: (1) construye su subplantilla a partir del configurador y del plan,
(2) arma el prompt = plantilla madre + subplantilla + formato de entrega,
(3) llama al ejecutor (el agente/modelo que se elija después) y
(4) separa la respuesta en archivos Markdown.
"""
from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

from ..ejecutores import EjecutorLLM
from ..schemas import Configurador, CursoPlan

log = logging.getLogger(__name__)

_MARCADOR = re.compile(r"<!--\s*ARCHIVO:\s*([A-Za-z0-9_\-.]+)\s*-->")
_CERCA = re.compile(r"^\s*```(?:markdown|md)?\s*\n(.*)\n```\s*$", re.DOTALL)


@dataclass
class ArchivoGenerado:
    nombre: str
    contenido: str
    via: str


@dataclass
class ResultadoVia:
    via: str
    subplantilla: str
    archivos: list[ArchivoGenerado] = field(default_factory=list)


class ViaBase(ABC):
    rol: ClassVar[str]                          # nombre de la vía (también el rol del modelo)
    instrucciones: ClassVar[str]                # "system prompt" del agente de la vía
    archivos_esperados: ClassVar[tuple[str, ...]]  # archivos .md que debe entregar

    def __init__(self, ejecutor: EjecutorLLM):
        self._ejecutor = ejecutor

    @abstractmethod
    def construir_subplantilla(self, config: Configurador, plan: CursoPlan) -> str:
        """Subplantilla específica de la vía, en Markdown."""

    def construir_prompt(self, plantilla_madre: str, subplantilla: str) -> str:
        marcadores = "\n".join(f"<!-- ARCHIVO: {n} -->" for n in self.archivos_esperados)
        
        anti_latex = "REGLA ESTRICTA DE FORMATO: Usa ÚNICAMENTE Markdown estándar. ESTÁ TOTALMENTE PROHIBIDO usar LaTeX, MathJax, o símbolos de dólar ($ o $$). Escribe las fórmulas matemáticas como texto normal.\n\n"
        
        return (
            "Recibes dos documentos. La plantilla base fija el contexto común del curso y la "
            "plantilla específica indica exactamente qué debes producir. Cumple ambas.\n\n"
            f"{anti_latex}"
            f"---\n## DOCUMENTO 1: PLANTILLA BASE\n\n{plantilla_madre}\n\n"
            f"---\n## DOCUMENTO 2: PLANTILLA ESPECÍFICA\n\n{subplantilla}\n\n"
            "---\n## Formato de entrega\n"
            "Entrega todo en Markdown. Antes del contenido de cada archivo escribe, en su propia "
            "línea, su marcador exacto. Archivos a entregar, en este orden:\n\n"
            f"{marcadores}\n"
        )

    async def ejecutar(self, plantilla_madre: str, config: Configurador, plan: CursoPlan) -> ResultadoVia:
        subplantilla = self.construir_subplantilla(config, plan)
        prompt = self.construir_prompt(plantilla_madre, subplantilla)
        texto = await self._ejecutor.generar(rol=self.rol, instrucciones=self.instrucciones, prompt=prompt)
        archivos = [
            ArchivoGenerado(nombre=n, contenido=c, via=self.rol)
            for n, c in self._separar_archivos(texto).items()
        ]
        return ResultadoVia(via=self.rol, subplantilla=subplantilla, archivos=archivos)

    # ------------------------------------------------------------------ helpers
    def _separar_archivos(self, texto: str) -> dict[str, str]:
        texto = texto.strip()
        partes = _MARCADOR.split(texto)
        archivos: dict[str, str] = {}
        for i in range(1, len(partes), 2):
            nombre = Path(partes[i]).name
            if nombre in self.archivos_esperados:
                archivos[nombre] = self._limpiar(partes[i + 1])
            else:
                log.warning("Vía %s: archivo inesperado '%s' ignorado", self.rol, nombre)
        if not archivos:
            log.warning("Vía %s: la respuesta no traía marcadores; se guarda completa", self.rol)
            archivos[self.archivos_esperados[0]] = self._limpiar(partes[0])
        faltan = [n for n in self.archivos_esperados if n not in archivos]
        if faltan:
            log.warning("Vía %s: no entregó %s", self.rol, ", ".join(faltan))
        return archivos

    @staticmethod
    def _limpiar(texto: str) -> str:
        texto = texto.strip()
        m = _CERCA.match(texto)  # algunos modelos envuelven todo en ```markdown
        return (m.group(1) if m else texto).strip() + "\n"
