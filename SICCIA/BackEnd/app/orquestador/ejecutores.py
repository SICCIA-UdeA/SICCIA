"""Capa que aísla al orquestador del proveedor de modelos.

``EjecutorLLM`` es lo único que las vías y el planificador conocen.
Se ha integrado el registro de telemetría (tokens y tiempos en CSV) y
políticas de reintentos (backoff) con respaldo (fallback) automático.
"""
from __future__ import annotations

import asyncio
import re
import time
import csv
import os
import json
import logging
from typing import Protocol

from .config import ConfigModelo, clave_google, config_modelo

_MARCADOR = re.compile(r"<!--\s*ARCHIVO:\s*([A-Za-z0-9_\-.]+)\s*-->")
log = logging.getLogger(__name__)


class ConfiguracionProveedorError(ValueError):
    """La configuración no permite construir el cliente del proveedor."""


class EjecutorLLM(Protocol):
    es_simulado: bool

    async def generar(self, *, rol: str, instrucciones: str, prompt: str) -> str: ...


# --- CAMBIO SICCIA: LOG DE TOKENS PARA EL PAPER ---
def log_prueba(proveedor: str, modelo: str, rol: str, respuesta_agno, segundos: float):
    """Guarda automáticamente los consumos en CSV para el artículo académico."""
    pt, ct = 0, 0
    
    # Intento 1: Formato estándar de métricas de Agno (Ahora lee Objetos correctamente)
    if hasattr(respuesta_agno, "metrics") and respuesta_agno.metrics:
        m = respuesta_agno.metrics
        if isinstance(m, dict):
            pt = m.get("prompt_tokens", m.get("input_tokens", 0))
            ct = m.get("completion_tokens", m.get("output_tokens", 0))
        else:
            pt = getattr(m, "prompt_tokens", getattr(m, "input_tokens", 0))
            ct = getattr(m, "completion_tokens", getattr(m, "output_tokens", 0))
    
    # Intento 2: Formato raw/usage (Común en OpenRouter/Groq directos)
    elif hasattr(respuesta_agno, "usage") and respuesta_agno.usage:
        uso = respuesta_agno.usage
        if isinstance(uso, dict):
            pt = uso.get("prompt_tokens", uso.get("input_tokens", 0))
            ct = uso.get("completion_tokens", uso.get("output_tokens", 0))
        else:
            pt = getattr(uso, "prompt_tokens", getattr(uso, "input_tokens", 0))
            ct = getattr(uso, "completion_tokens", getattr(uso, "output_tokens", 0))

    archivo = "registro_pruebas_siccia.csv"
    es_nuevo = not os.path.exists(archivo)
    
    with open(archivo, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        if es_nuevo:
            writer.writerow(["Fecha", "Proveedor", "Modelo", "Via_Rol", "Prompt_Tokens", "Completion_Tokens", "Tiempo_Segundos"])
        writer.writerow([time.strftime("%Y-%m-%d %H:%M"), proveedor, modelo, rol, pt, ct, round(segundos, 1)])
# ---------------------------------------------------

class EjecutorMock:
    """Devuelve Markdown de relleno e informa qué recibió, sin llamar a ningún modelo."""
    es_simulado = True

    async def generar(self, *, rol: str, instrucciones: str, prompt: str) -> str:
        await asyncio.sleep(0.05)
        secciones = [l for l in prompt.splitlines() if l.startswith("#")]
        cuerpo = (
            f"# [SIMULADO] Resultado del agente '{rol}'\n\n"
            f"Prompt recibido: {len(prompt)} caracteres.\n\n"
            "## Secciones que llegaron en el prompt\n"
            + "\n".join(f"- `{s}`" for s in secciones)
            + "\n"
        )
        pedidos = _MARCADOR.findall(prompt.split("## Formato de entrega")[-1])
        if not pedidos:
            return cuerpo
        return "\n".join(f"<!-- ARCHIVO: {n} -->\n{cuerpo}" for n in dict.fromkeys(pedidos))


class EjecutorAgno:
    es_simulado = False

    def __init__(self, cfg: ConfigModelo):
        self._cfg = cfg
        self.ultimo_proveedor = cfg.proveedor
        self.ultimo_modelo = cfg.model_id

    def _crear_modelo(self, cfg: ConfigModelo | None = None):
        cfg = cfg or self._cfg
        if cfg.proveedor == "gemini":
            from agno.models.google import Gemini
            kwargs = {"id": cfg.model_id, "temperature": cfg.temperatura}
            api_key = cfg.api_key or clave_google()
            if not api_key:
                raise ConfiguracionProveedorError(
                    "Gemini requiere GOOGLE_API_KEY o una clave API del rol."
                )
            kwargs["api_key"] = api_key
            return Gemini(**kwargs)
            
        if cfg.proveedor == "openai_like":
            from agno.models.openai.like import OpenAILike
            if not cfg.api_key or not cfg.base_url:
                raise ConfiguracionProveedorError(
                    "openai_like requiere ORQ_API_KEY y ORQ_BASE_URL."
                )
            return OpenAILike(
                id=cfg.model_id, api_key=cfg.api_key, base_url=cfg.base_url,
                temperature=cfg.temperatura, max_tokens=cfg.max_tokens,
            )
            
        if cfg.proveedor == "openai":
            from agno.models.openai import OpenAIChat
            if not cfg.api_key:
                raise ConfiguracionProveedorError("openai requiere ORQ_API_KEY.")
            return OpenAIChat(
                id=cfg.model_id,
                api_key=cfg.api_key,
                temperature=cfg.temperatura,
                max_tokens=cfg.max_tokens,
            )
            
        raise ValueError(f"Proveedor de modelo no soportado: {cfg.proveedor!r}")

    @staticmethod
    def _reintentable(exc: Exception) -> bool:
        if isinstance(exc, (asyncio.TimeoutError, TimeoutError, ConnectionError)):
            return True
        mensaje = str(exc).lower()
        return any(
            marcador in mensaje
            for marcador in ("429", "rate limit", "too many requests", "temporarily", "503", "502", "504",
                             "respuesta vacía", "respuesta nula", "timed out", "timeout")
        )

    async def generar(self, *, rol: str, instrucciones: str, prompt: str) -> str:
        from agno.agent import Agent

        intentos_maximos = 3
        espera_base = 2
        configuraciones = [self._cfg]
        if self._cfg.respaldo and self._cfg.respaldo.proveedor != self._cfg.proveedor:
            configuraciones.append(self._cfg.respaldo)
        ultimo_error: Exception | None = None

        for indice, cfg in enumerate(configuraciones):
            try:
                modelo = self._crear_modelo(cfg)
            except ConfiguracionProveedorError:
                if indice == 0:
                    raise
                log.warning("[%s] Respaldo %s no está configurado correctamente.", rol, cfg.proveedor)
                continue

            for intento in range(1, intentos_maximos + 1):
                try:
                    opciones_agente = {}
                    if rol == "planificador":
                        from .schemas import CursoPlan
                        opciones_agente = {"output_schema": CursoPlan, "use_json_mode": True}
                    agente = Agent(
                        name=rol, model=modelo, instructions=instrucciones, markdown=True,
                        **opciones_agente,
                    )
                    t0 = time.time()
                    respuesta = await asyncio.wait_for(
                        agente.arun(prompt), timeout=cfg.timeout_segundos
                    )
                    t1 = time.time()
                    contenido = respuesta.content if hasattr(respuesta, "content") else str(respuesta)
                    if hasattr(contenido, "model_dump_json"):
                        contenido = contenido.model_dump_json()
                    if not isinstance(contenido, str):
                        contenido = str(contenido)
                    contenido_limpio = contenido.strip()
                    valor_normalizado = contenido_limpio.strip("` \t\r\n").lower()
                    if not contenido_limpio or valor_normalizado in {"none", "null", "nan"}:
                        raise ValueError("El modelo devolvió una respuesta vacía o nula.")
                    if contenido_limpio.startswith("{") and "error" in contenido_limpio.lower():
                        try:
                            error_json = json.loads(contenido_limpio)
                            if "error" in error_json:
                                raise RuntimeError(
                                    f"La API devolvió un JSON de error: {error_json['error']}"
                                )
                        except json.JSONDecodeError:
                            pass
                    try:
                        log_prueba(
                            proveedor=cfg.proveedor,
                            modelo=getattr(modelo, "id", cfg.model_id),
                            rol=rol, respuesta_agno=respuesta, segundos=t1 - t0,
                        )
                    except Exception as exc:
                        log.warning("[%s] No se pudo registrar la telemetría: %s", rol, exc)
                    self.ultimo_proveedor = cfg.proveedor
                    self.ultimo_modelo = cfg.model_id
                    return contenido
                except Exception as exc:
                    ultimo_error = exc
                    if not self._reintentable(exc):
                        break
                    if intento < intentos_maximos:
                        espera = espera_base ** intento
                        log.warning(
                            "[%s] %s intento %d falló (%s). Reintentando en %ss.",
                            rol, cfg.proveedor, intento, exc, espera,
                        )
                        await asyncio.sleep(espera)
            if indice + 1 < len(configuraciones):
                log.warning(
                    "[%s] %s agotado; usando respaldo %s.",
                    rol, cfg.proveedor, configuraciones[indice + 1].proveedor,
                )
        if ultimo_error:
            raise RuntimeError(
                f"Fallaron los proveedores configurados para {rol}: {ultimo_error}"
            ) from ultimo_error
        raise RuntimeError(f"No hay un proveedor disponible para {rol}.")


def crear_ejecutor(rol: str) -> EjecutorLLM:
    cfg = config_modelo(rol)
    return EjecutorMock() if cfg.proveedor == "mock" else EjecutorAgno(cfg)