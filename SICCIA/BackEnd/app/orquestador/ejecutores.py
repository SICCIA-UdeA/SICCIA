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

    def _crear_modelo(self):
        cfg = self._cfg
        if cfg.proveedor == "gemini":
            from agno.models.google import Gemini
            kwargs = {"id": cfg.model_id, "temperature": cfg.temperatura}
            api_key = clave_google() or cfg.api_key
            if api_key:
                kwargs["api_key"] = api_key
            return Gemini(**kwargs)
            
        if cfg.proveedor == "openai_like":
            from agno.models.openai.like import OpenAILike
            return OpenAILike(
                id=cfg.model_id, api_key=cfg.api_key, base_url=cfg.base_url,
                temperature=cfg.temperatura, max_tokens=cfg.max_tokens,
            )
            
        if cfg.proveedor == "openai":
            from agno.models.openai import OpenAIChat
            return OpenAIChat(
                id=cfg.model_id,
                api_key=cfg.api_key,
                temperature=cfg.temperatura,
                max_tokens=cfg.max_tokens,
            )
            
        raise ValueError(f"Proveedor de modelo no soportado: {cfg.proveedor!r}")

    async def generar(self, *, rol: str, instrucciones: str, prompt: str) -> str:
        from agno.agent import Agent

        intentos_maximos = 3
        espera_base = 2
        modelo_actual = self._crear_modelo()
        
        for intento in range(1, intentos_maximos + 1):
            try:
                opciones_agente = {}
                if rol == "planificador":
                    from .schemas import CursoPlan

                    opciones_agente = {
                        "output_schema": CursoPlan,
                        "use_json_mode": True,
                    }
                agente = Agent(
                    name=rol, 
                    model=modelo_actual, 
                    instructions=instrucciones, 
                    markdown=True,
                    **opciones_agente,
                )
                
                t0 = time.time()
                respuesta = await asyncio.wait_for(
                    agente.arun(prompt),
                    timeout=self._cfg.timeout_segundos,
                )
                t1 = time.time()
                
                contenido = respuesta.content if hasattr(respuesta, "content") else str(respuesta)
                if hasattr(contenido, "model_dump_json"):
                    contenido = contenido.model_dump_json()
                if not isinstance(contenido, str):
                    contenido = str(contenido)
                    
                contenido_limpio = contenido.strip()
                
                # 1. BLOQUEO CONTRA RESPUESTAS VACÍAS
                if not contenido_limpio:
                    raise ValueError("El modelo devolvió una respuesta vacía o None.")
                
                # 2. BLOQUEO CONTRA ERRORES DISFRAZADOS DE TEXTO EXITOSO
                if contenido_limpio.startswith("{") and "error" in contenido_limpio.lower():
                    try:
                        error_json = json.loads(contenido_limpio)
                        if "error" in error_json:
                            raise RuntimeError(f"La API devolvió un JSON de error: {error_json['error']}")
                    except json.JSONDecodeError:
                        pass # Falsa alarma, es texto Markdown que curiosamente empezaba con llave
                
                # Telemetría: Pasamos la respuesta completa para cazar los tokens
                try:
                    log_prueba(
                        proveedor=self._cfg.proveedor, 
                        modelo=getattr(modelo_actual, "id", self._cfg.model_id), 
                        rol=rol, 
                        respuesta_agno=respuesta,
                        segundos=t1 - t0
                    )
                except Exception as exc:  # un fallo de telemetría no debe repetir la llamada al modelo
                    log.warning(f"[{rol}] No se pudo registrar la telemetría: {exc}")
                
                return contenido

            except Exception as exc:
                if intento < intentos_maximos:
                    tiempo_espera = espera_base ** intento # 2s, 4s...
                    log.warning(f"[{rol}] Intento {intento} falló ({exc}). Reintentando en {tiempo_espera}s...")
                    await asyncio.sleep(tiempo_espera)
                    
                    # El fallback solo aplica a Gemini; no debe cambiar
                    # silenciosamente un proveedor openai_like u openai.
                    if intento == intentos_maximos - 1 and self._cfg.proveedor == "gemini":
                        log.warning(f"[{rol}] Agotando recursos. Cambiando a modelo de respaldo: gemini-3.8-flash")
                        from agno.models.google import Gemini
                        fallback_key = clave_google()
                        modelo_actual = Gemini(id="gemini-3.8-flash", api_key=fallback_key)
                else:
                    log.error(f"[{rol}] Fallo definitivo tras {intentos_maximos} intentos.")
                    raise exc # Lanza el error para que orquestador.py atrape el fallo de esta vía


def crear_ejecutor(rol: str) -> EjecutorLLM:
    cfg = config_modelo(rol)
    return EjecutorMock() if cfg.proveedor == "mock" else EjecutorAgno(cfg)