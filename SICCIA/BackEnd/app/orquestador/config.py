"""Configuración del orquestador, leída de variables de entorno.

Cada vía se asocia a un proveedor con nombre (por ejemplo, ``nvidia`` o
``gemini``). Las credenciales y los modelos se declaran una sola vez por
proveedor; las variables antiguas por rol siguen siendo compatibles.

Variables:
    ORQ_VIA_<ROL>    nombre del proveedor asociado a una vía
    ORQ_RESPALDO_<ROL> nombre opcional del proveedor de respaldo
    ORQ_PROVEEDOR_<NOMBRE>_TIPO  mock | gemini | openai_like | openai
    ORQ_PROVEEDOR_<NOMBRE>_MODELO  id del modelo
    ORQ_PROVEEDOR_<NOMBRE>_API_KEY clave del proveedor
    ORQ_PROVEEDOR_<NOMBRE>_BASE_URL endpoint compatible con OpenAI
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

ROLES = ("planificador", "evaluacion", "contenido", "programa", "verificacion")
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
    respaldo: ConfigModelo | None = None


def _valor(*nombres: str) -> str | None:
    for nombre in nombres:
        valor = os.getenv(nombre) or _DOTENV.get(nombre)
        if valor:
            return valor
    return None


def _env(variable: str, rol: str, sufijo: str = "") -> str | None:
    nombres = (
        f"ORQ_{variable}{sufijo}_{rol.upper()}",
        f"ORQ_{variable}_{rol.upper()}{sufijo}",
        f"ORQ_{variable}{sufijo}",
    )
    for nombre in nombres:
        valor = _valor(nombre)
        if valor:
            return valor
    return None


def clave_google() -> str | None:
    return _valor("GOOGLE_API_KEY")


def _config_proveedor(nombre: str, rol: str) -> ConfigModelo:
    prefijo = f"ORQ_PROVEEDOR_{nombre.upper()}"
    max_tokens = int(
        _valor(f"{prefijo}_MAX_TOKENS")
        or (32768 if rol == "contenido" else 16384)
    )
    return ConfigModelo(
        proveedor=(_valor(f"{prefijo}_TIPO") or nombre).lower(),
        model_id=_valor(f"{prefijo}_MODELO", f"{prefijo}_MODEL_ID") or "gemini-3.8-flash",
        api_key=_valor(f"{prefijo}_API_KEY"),
        base_url=_valor(f"{prefijo}_BASE_URL"),
        temperatura=float(_valor(f"{prefijo}_TEMPERATURA") or 0.4),
        max_tokens=max_tokens,
        timeout_segundos=float(_valor(f"{prefijo}_TIMEOUT_SEGUNDOS") or 900),
    )


def config_modelo(rol: str) -> ConfigModelo:
    nombre = _valor(f"ORQ_VIA_{rol.upper()}")
    nombre_respaldo = _valor(f"ORQ_RESPALDO_{rol.upper()}")
    if nombre:
        primaria = _config_proveedor(nombre, rol)
        if nombre_respaldo and nombre_respaldo.lower() != nombre.lower():
            primaria = ConfigModelo(
                **{
                    **primaria.__dict__,
                    "respaldo": _config_proveedor(nombre_respaldo, rol),
                }
            )
        return primaria

    primaria = ConfigModelo(
        proveedor=(_env("PROVEEDOR", rol) or "mock").lower(),
        model_id=_env("MODEL_ID", rol) or "gemini-3.8-flash",
        api_key=_env("API_KEY", rol),
        base_url=_env("BASE_URL", rol),
        temperatura=float(_env("TEMPERATURA", rol) or 0.4),
        max_tokens=int(_env("MAX_TOKENS", rol) or (32768 if rol == "contenido" else 16384)),
        timeout_segundos=float(_env("TIMEOUT_SEGUNDOS", rol) or 900),
    )
    proveedor_respaldo = (_env("PROVEEDOR", rol, "_RESPALDO") or "").lower()
    if not proveedor_respaldo:
        return primaria
    respaldo = ConfigModelo(
        proveedor=proveedor_respaldo,
        model_id=_env("MODEL_ID", rol, "_RESPALDO") or "gemini-3.8-flash",
        api_key=_env("API_KEY", rol, "_RESPALDO"),
        base_url=_env("BASE_URL", rol, "_RESPALDO"),
        temperatura=float(_env("TEMPERATURA", rol, "_RESPALDO") or primaria.temperatura),
        max_tokens=int(_env("MAX_TOKENS", rol, "_RESPALDO") or primaria.max_tokens),
        timeout_segundos=float(
            _env("TIMEOUT_SEGUNDOS", rol, "_RESPALDO") or primaria.timeout_segundos
        ),
    )
    return ConfigModelo(**{**primaria.__dict__, "respaldo": respaldo})


def directorio_salida() -> Path:
    return Path(os.getenv("ORQ_DIR_SALIDA", "orquestador_salida"))
