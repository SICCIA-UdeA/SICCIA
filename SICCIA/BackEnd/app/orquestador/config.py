"""Configuración del orquestador, leída de variables de entorno.

Cada rol (planificador, evaluacion, contenido, programa) puede usar un modelo
distinto. Para un rol se busca primero ``ORQ_<VAR>_<ROL>`` y luego ``ORQ_<VAR>``.

Variables:
    ORQ_PROVEEDOR    mock | gemini | openai_like | openai     (defecto: mock)
    ORQ_MODEL_ID     id del modelo                            (defecto: gemini-2.5-flash)
    ORQ_API_KEY      clave del proveedor (para gemini, Agno también lee GOOGLE_API_KEY)
    ORQ_BASE_URL     solo openai_like (p. ej. endpoint compatible con OpenAI)
    ORQ_TEMPERATURA  defecto 0.4
    ORQ_DIR_SALIDA   carpeta donde se guardan los trabajos   (defecto: orquestador_salida)

Ejemplo: ORQ_PROVEEDOR=gemini y ORQ_MODEL_ID_EVALUACION=gemini-2.5-pro
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROLES = ("planificador", "evaluacion", "contenido", "programa")


@dataclass(frozen=True)
class ConfigModelo:
    proveedor: str
    model_id: str
    api_key: str | None
    base_url: str | None
    temperatura: float


def _env(variable: str, rol: str) -> str | None:
    return os.getenv(f"ORQ_{variable}_{rol.upper()}") or os.getenv(f"ORQ_{variable}")


def config_modelo(rol: str) -> ConfigModelo:
    return ConfigModelo(
        proveedor=(_env("PROVEEDOR", rol) or "mock").lower(),
        model_id=_env("MODEL_ID", rol) or "gemini-2.5-flash",
        api_key=_env("API_KEY", rol),
        base_url=_env("BASE_URL", rol),
        temperatura=float(_env("TEMPERATURA", rol) or 0.4),
    )


def directorio_salida() -> Path:
    return Path(os.getenv("ORQ_DIR_SALIDA", "orquestador_salida"))
