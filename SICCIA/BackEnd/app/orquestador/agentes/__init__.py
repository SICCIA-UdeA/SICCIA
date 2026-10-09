"""Vías de trabajo del orquestador: cada clase es un agente (o grupo de agentes) en paralelo."""
from .base import ArchivoGenerado, ResultadoVia, ViaBase
from .via_contenido import ViaContenido
from .via_evaluacion import ViaEvaluacion
from .via_programa import ViaPrograma

__all__ = [
    "ArchivoGenerado", "ResultadoVia", "ViaBase",
    "ViaEvaluacion", "ViaContenido", "ViaPrograma",
]
