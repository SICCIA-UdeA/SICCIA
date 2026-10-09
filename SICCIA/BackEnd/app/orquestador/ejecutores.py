"""Capa que aísla al orquestador del proveedor de modelos.

``EjecutorLLM`` es lo único que las vías y el planificador conocen. Hoy hay dos
implementaciones:

* ``EjecutorMock``: sin modelo; permite probar todo el flujo sin conexión.
* ``EjecutorAgno``: crea un ``agno.agent.Agent`` con Gemini, o con cualquier
  endpoint compatible con el SDK de OpenAI (``openai_like`` / ``openai``).

Agno solo se importa cuando se usa, así el paquete funciona en modo mock sin él.
"""
from __future__ import annotations

import asyncio
import re
from typing import Protocol

from .config import ConfigModelo, config_modelo

_MARCADOR = re.compile(r"<!--\s*ARCHIVO:\s*([A-Za-z0-9_\-.]+)\s*-->")


class EjecutorLLM(Protocol):
    es_simulado: bool

    async def generar(self, *, rol: str, instrucciones: str, prompt: str) -> str: ...


class EjecutorMock:
    """Devuelve Markdown de relleno e informa qué recibió, sin llamar a ningún modelo."""

    es_simulado = True

    async def generar(self, *, rol: str, instrucciones: str, prompt: str) -> str:
        await asyncio.sleep(0.05)  # simula latencia para que el paralelismo sea observable
        secciones = [l for l in prompt.splitlines() if l.startswith("#")]
        cuerpo = (
            f"# [SIMULADO] Resultado del agente '{rol}'\n\n"
            f"Prompt recibido: {len(prompt)} caracteres.\n\n"
            "## Secciones que llegaron en el prompt\n"
            + "\n".join(f"- `{s}`" for s in secciones)
            + "\n"
        )
        # Una sección por cada archivo que el prompt pide entregar.
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

        agente = Agent(name=rol, model=self._crear_modelo(), instructions=instrucciones, markdown=True)
        respuesta = await agente.arun(prompt)
        contenido = respuesta.content
        return contenido if isinstance(contenido, str) else str(contenido)


def crear_ejecutor(rol: str) -> EjecutorLLM:
    cfg = config_modelo(rol)
    return EjecutorMock() if cfg.proveedor == "mock" else EjecutorAgno(cfg)
