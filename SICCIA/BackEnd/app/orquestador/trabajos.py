"""Registro de trabajos (en memoria) y su carpeta en disco.

Nota: el estado vive en memoria; si el servidor se reinicia se pierde el seguimiento,
aunque los archivos ya generados siguen en disco. Más adelante puede pasar a BD.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from .agentes.base import ArchivoGenerado


class EstadoTrabajo(str, Enum):
    PENDIENTE = "pendiente"
    PLANIFICANDO = "planificando"
    EJECUTANDO = "ejecutando"
    COMPLETADO = "completado"
    COMPLETADO_CON_ERRORES = "completado_con_errores"
    ERROR = "error"


@dataclass
class Trabajo:
    id: str
    directorio: Path
    estado: EstadoTrabajo = EstadoTrabajo.PENDIENTE
    vias: dict[str, str] = field(default_factory=dict)
    archivos: dict[str, ArchivoGenerado] = field(default_factory=dict)  # nombre -> archivo
    error: str | None = None
    creado_en: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def dir_resultados(self) -> Path:
        return self.directorio / "resultados"   # lo que se descarga

    @property
    def dir_interno(self) -> Path:
        return self.directorio / "interno"      # plantillas y plan, para depuración

    @property
    def terminado(self) -> bool:
        return self.estado in (
            EstadoTrabajo.COMPLETADO, EstadoTrabajo.COMPLETADO_CON_ERRORES, EstadoTrabajo.ERROR
        )


class GestorTrabajos:
    def __init__(self, base: Path):
        self._base = base
        self._trabajos: dict[str, Trabajo] = {}

    def crear(self) -> Trabajo:
        trabajo_id = uuid.uuid4().hex
        trabajo = Trabajo(id=trabajo_id, directorio=self._base / trabajo_id)
        trabajo.dir_resultados.mkdir(parents=True, exist_ok=True)
        trabajo.dir_interno.mkdir(parents=True, exist_ok=True)
        self._trabajos[trabajo.id] = trabajo
        return trabajo

    def obtener(self, trabajo_id: str) -> Trabajo | None:
        return self._trabajos.get(trabajo_id)
