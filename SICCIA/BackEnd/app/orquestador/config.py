"""Configuración del orquestador, leída de variables de entorno.

Cada rol (planificador, evaluacion, contenido, programa) puede usar un modelo
distinto. Para un rol se busca primero ``ORQ_<VAR>_<ROL>`` y luego ``ORQ_<VAR>``.

Variables:
    ORQ_PROVEEDOR    mock | gemini | openai_like | openai     (defecto: mock)
    ORQ_MODEL_ID     id del modelo                            (defecto: gemini-3.8-flash)
    ORQ_API_KEY      clave del proveedor (para gemini, Agno también lee GOOGLE_API_KEY)
    ORQ_BASE_URL     solo openai_like (p. ej. endpoint compatible con OpenAI)
    ORQ_TEMPERATURA  defecto 0.4
    ORQ_MAX_TOKENS   máximo de tokens generados por llamada (defecto: 16384)
    ORQ_TIMEOUT_SEGUNDOS tiempo máximo por llamada al modelo (defecto: 900)
    ORQ_DIR_SALIDA   carpeta donde se guardan los trabajos   (defecto: orquestador_salida)

Ejemplo: ORQ_PROVEEDOR=gemini y ORQ_MODEL_ID_EVALUACION=gemini-2.5-pro
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values

ROLES = ("planificador", "evaluacion", "contenido", "programa")
_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
_DOTENV = dotenv_values(_ENV_FILE)


@dataclass(frozen=True)
class ConfigModelo:
    proveedor: str
    model_id: str
    api_key: str | None
    base_url: str | None
    temperatura: float
    max_tokens: int
    timeout_segundos: float


def _env(variable: str, rol: str) -> str | None:
    nombres = (f"ORQ_{variable}_{rol.upper()}", f"ORQ_{variable}")
    for nombre in nombres:
        valor = os.getenv(nombre) or _DOTENV.get(nombre)
        if valor:
            return valor
    return None


def clave_google() -> str | None:
    return os.getenv("GOOGLE_API_KEY") or _DOTENV.get("GOOGLE_API_KEY")


def config_modelo(rol: str) -> ConfigModelo:
    return ConfigModelo(
        proveedor=(_env("PROVEEDOR", rol) or "mock").lower(),
        model_id=_env("MODEL_ID", rol) or "gemini-3.8-flash",
        api_key=_env("API_KEY", rol),
        base_url=_env("BASE_URL", rol),
        temperatura=float(_env("TEMPERATURA", rol) or 0.4),
        max_tokens=int(_env("MAX_TOKENS", rol) or 16384),
        timeout_segundos=float(_env("TIMEOUT_SEGUNDOS", rol) or 900),
    )


def directorio_salida() -> Path:
    return Path(os.getenv("ORQ_DIR_SALIDA", "orquestador_salida"))
