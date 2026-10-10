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

from .config import ConfigModelo, config_modelo

_MARCADOR = re.compile(r"<!--\s*ARCHIVO:\s*([A-Za-z0-9_\-.]+)\s*-->")
log = logging.getLogger(__name__)


class EjecutorLLM(Protocol):
    es_simulado: bool

    async def generar(self, *, rol: str, instrucciones: str, prompt: str) -> str: ...


# --- LOG DE TOKENS PARA EL PAPER ---
def log_prueba(proveedor: str, modelo: str, rol: str, usage, segundos: float):
    pt = getattr(usage, "prompt_tokens", 0) if usage else 0
    ct = getattr(usage, "completion_tokens", 0) if usage else 0
    
    if pt == 0 and ct == 0 and isinstance(usage, dict):
        pt = usage.get("prompt_tokens", 0)
        ct = usage.get("completion_tokens", 0)

    archivo = "registro_pruebas_siccia.csv"
    es_nuevo = not os.path.exists(archivo)
    
    with open(archivo, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        if es_nuevo:
            writer.writerow(["Fecha", "Proveedor", "Modelo", "Via_Rol", "Prompt_Tokens", "Completion_Tokens", "Tiempo_Segundos"])
        writer.writerow([time.strftime("%Y-%m-%d %H:%M"), proveedor, modelo, rol, pt, ct, round(segundos, 1)])
# -----------------------------------


class EjecutorMock:
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
            if cfg.api_key:
                kwargs["api_key"] = cfg.api_key
            return Gemini(**kwargs)
            
        if cfg.proveedor == "openai_like":
            from agno.models.openai.like import OpenAILike
            return OpenAILike(
                id=cfg.model_id, api_key=cfg.api_key, base_url=cfg.base_url,
                temperature=cfg.temperatura,
            )
            
        if cfg.proveedor == "openai":
            from agno.models.openai import OpenAIChat
            return OpenAIChat(id=cfg.model_id, api_key=cfg.api_key, temperature=cfg.temperatura)
            
        raise ValueError(f"Proveedor de modelo no soportado: {cfg.proveedor!r}")

    async def generar(self, *, rol: str, instrucciones: str, prompt: str) -> str:
        from agno.agent import Agent

        intentos_maximos = 3
        espera_base = 2
        modelo_actual = self._crear_modelo()
        
        for intento in range(1, intentos_maximos + 1):
            try:
                agente = Agent(
                    name=rol, 
                    model=modelo_actual, 
                    instructions=instrucciones, 
                    markdown=True
                )
                
                t0 = time.time()
                respuesta = await agente.arun(prompt)
                t1 = time.time()
                
                contenido = respuesta.content if hasattr(respuesta, "content") else str(respuesta)
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
                
                # Si pasa los filtros, registramos telemetría y retornamos
                uso = getattr(respuesta, "usage", None)
                log_prueba(
                    proveedor=self._cfg.proveedor, 
                    modelo=getattr(modelo_actual, "id", self._cfg.model_id), 
                    rol=rol, 
                    usage=uso, 
                    segundos=t1 - t0
                )
                
                return contenido

            except Exception as exc:
                if intento < intentos_maximos:
                    tiempo_espera = espera_base ** intento # 2s, 4s...
                    log.warning(f"[{rol}] Intento {intento} falló ({exc}). Reintentando en {tiempo_espera}s...")
                    await asyncio.sleep(tiempo_espera)
                    
                    # 3. FALLBACK: Si es el último reintento, saltar al salvavidas (Gemini)
                    if intento == intentos_maximos - 1:
                        log.warning(f"[{rol}] Agotando recursos. Cambiando a modelo de respaldo: gemini-2.5-flash")
                        from agno.models.google import Gemini
                        fallback_key = os.getenv("GOOGLE_API_KEY") or os.getenv("ORQ_API_KEY_CONTENIDO")
                        modelo_actual = Gemini(id="gemini-2.5-flash", api_key=fallback_key)
                else:
                    log.error(f"[{rol}] Fallo definitivo tras {intentos_maximos} intentos.")
                    raise exc # Lanza el error para que orquestador.py atrape el fallo de esta vía


def crear_ejecutor(rol: str) -> EjecutorLLM:
    cfg = config_modelo(rol)
    return EjecutorMock() if cfg.proveedor == "mock" else EjecutorAgno(cfg)