"""Contratos de datos: el JSON "configurador" que llega del frontend y el plan del curso.

Todo es opcional salvo ``datos.tema``: lo que el usuario deje en automático lo
diseña el orquestador. Los campos desconocidos se ignoran (no rompen la solicitud),
así las opciones fuera del MVP pueden seguir llegando sin problema.
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ----------------------------------------------------------------- configurador
class ModuloConfig(BaseModel):
    titulo: str = Field(min_length=1)
    temas: list[str] = Field(default_factory=list, description="Solo títulos. Vacío = automático.")


class DatosCurso(BaseModel):
    tema: str = Field(min_length=3)
    publico_objetivo: str | None = None
    duracion_estimada: str | None = None
    metodologia: str | None = None


class ContenidoConfig(BaseModel):
    modulos_modo: Literal["automatico", "manual"] = "automatico"
    num_modulos: int | None = Field(default=None, ge=1, le=20)
    modulos: list[ModuloConfig] = Field(default_factory=list)
    incluir_ejemplos_practicos: bool = True
    incluir_talleres_practica: bool = True   # talleres NO calificados, uno por módulo
    incluir_cierre_por_modulo: bool = True   # bloque de conclusión al final de cada módulo
    incluir_enlaces: bool = False            # fuera del MVP (alucinación de URLs)
    formato_referencias: str | None = None   # fuera del MVP (APA, IEEE...)

    @model_validator(mode="after")
    def _modo_manual_requiere_modulos(self) -> "ContenidoConfig":
        if self.modulos_modo == "manual" and not self.modulos:
            raise ValueError("modulos_modo='manual' requiere al menos un módulo en 'modulos'")
        return self


class ActividadEvaluativa(BaseModel):
    tipo: str = Field(min_length=2, description="examen, laboratorio, investigación, taller...")
    cantidad: int = Field(default=1, ge=1)
    porcentaje: float | None = Field(
        default=None, ge=0, le=100,
        description="Porcentaje de la nota final que aporta TODO este grupo de actividades.",
    )


class EvaluacionConfig(BaseModel):
    tipos_pregunta: list[str] = Field(default_factory=list)  # selección múltiple, V/F, matching...
    actividades: list[ActividadEvaluativa] = Field(default_factory=list)
    total_actividades: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def _porcentajes_coherentes(self) -> "EvaluacionConfig":
        dados = [a.porcentaje for a in self.actividades if a.porcentaje is not None]
        suma = sum(dados)
        if suma > 100.01:
            raise ValueError(f"Los porcentajes de evaluación suman {suma:g}%, máximo 100%")
        if self.actividades and len(dados) == len(self.actividades) and abs(suma - 100) > 0.01:
            raise ValueError(f"Los porcentajes de evaluación suman {suma:g}%, deben sumar 100%")
        return self


class EstiloConfig(BaseModel):
    formato_salida: str = "pdf"
    incluir_imagenes: bool = False


class Configurador(BaseModel):
    model_config = ConfigDict(extra="ignore")

    datos: DatosCurso
    contenido: ContenidoConfig = Field(default_factory=ContenidoConfig)
    evaluacion: EvaluacionConfig = Field(default_factory=EvaluacionConfig)
    estilo: EstiloConfig = Field(default_factory=EstiloConfig)


# ------------------------------------------------------------------ plan del curso
class ModuloPlan(BaseModel):
    titulo: str = Field(min_length=1)
    temas: list[str] = Field(min_length=1)  # solo títulos


class CursoPlan(BaseModel):
    """Datos básicos del curso ya completos (lo que va en la plantilla madre)."""
    tema: str
    publico_objetivo: str
    duracion_estimada: str
    metodologia: str
    modulos: list[ModuloPlan] = Field(min_length=1)


# ---------------------------------------------------------------- respuestas API
class ArchivoInfo(BaseModel):
    nombre: str
    via: str
    tamano_bytes: int


class TrabajoCreado(BaseModel):
    id: str
    estado: str


class TrabajoRespuesta(BaseModel):
    id: str
    estado: str
    creado_en: datetime
    vias: dict[str, str]
    archivos: list[ArchivoInfo]
    error: str | None = None
