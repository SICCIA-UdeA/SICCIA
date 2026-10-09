"""Completa los datos que el usuario dejó en automático y produce el ``CursoPlan``."""
from __future__ import annotations

import json
import logging

from pydantic import ValidationError

from .ejecutores import EjecutorLLM
from .schemas import Configurador, CursoPlan, ModuloPlan

log = logging.getLogger(__name__)

_INSTRUCCIONES = (
    "Eres el diseñador curricular de un curso educativo. Respondes SIEMPRE y únicamente "
    "con un objeto JSON válido, sin texto adicional ni bloques de código."
)

_FORMATO = """{
  "tema": "...",
  "publico_objetivo": "...",
  "duracion_estimada": "...",
  "metodologia": "...",
  "modulos": [ {"titulo": "...", "temas": ["título del tema", "..."]} ]
}"""


class Planificador:
    rol = "planificador"

    def __init__(self, ejecutor: EjecutorLLM):
        self._ejecutor = ejecutor

    async def completar(self, config: Configurador) -> CursoPlan:
        faltantes = self._faltantes(config)
        if not faltantes:
            return self._plan_desde_config(config)

        if self._ejecutor.es_simulado:
            return self._fusionar(config, self._plan_simulado(config))

        prompt = self._prompt(config, faltantes)
        ultimo_error: Exception | None = None
        for intento in (1, 2):
            texto = await self._ejecutor.generar(rol=self.rol, instrucciones=_INSTRUCCIONES, prompt=prompt)
            try:
                return self._fusionar(config, self._parsear(texto))
            except (ValueError, ValidationError) as exc:
                ultimo_error = exc
                log.warning("Planificador: respuesta inválida (intento %s): %s", intento, exc)
                prompt += "\n\nTu respuesta anterior no fue un JSON válido con ese formato. Corrígela."
        raise RuntimeError(f"El planificador no devolvió un plan válido: {ultimo_error}")

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _faltantes(c: Configurador) -> list[str]:
        f = []
        if not c.datos.publico_objetivo:
            f.append("publico_objetivo")
        if not c.datos.duracion_estimada:
            f.append("duracion_estimada")
        if not c.datos.metodologia:
            f.append("metodologia")
        if c.contenido.modulos_modo == "automatico" or not c.contenido.modulos:
            f.append("modulos y temas")
        elif any(not m.temas for m in c.contenido.modulos):
            f.append("temas de los módulos que no los traen")
        return f

    @staticmethod
    def _plan_desde_config(c: Configurador) -> CursoPlan:
        return CursoPlan(
            tema=c.datos.tema,
            publico_objetivo=c.datos.publico_objetivo or "",
            duracion_estimada=c.datos.duracion_estimada or "",
            metodologia=c.datos.metodologia or "",
            modulos=[ModuloPlan(titulo=m.titulo, temas=m.temas) for m in c.contenido.modulos],
        )

    @staticmethod
    def _prompt(c: Configurador, faltantes: list[str]) -> str:
        dados = {
            "datos": c.datos.model_dump(exclude_none=True),
            "modulos_modo": c.contenido.modulos_modo,
            "num_modulos": c.contenido.num_modulos,
            "modulos_dados": [m.model_dump() for m in c.contenido.modulos],
        }
        return (
            "Diseña la base de un curso a partir de lo que dio el usuario.\n\n"
            f"Datos del usuario (JSON):\n{json.dumps(dados, ensure_ascii=False, indent=2)}\n\n"
            f"Debes diseñar lo que falta: {', '.join(faltantes)}.\n\n"
            "Reglas:\n"
            "- Conserva EXACTAMENTE los valores que el usuario sí dio (tema, módulos y temas dados).\n"
            "- De cada tema entrega solo el título, sin explicaciones ni contenido.\n"
            "- Si hay num_modulos, genera exactamente esa cantidad; si no, elige una cantidad razonable.\n"
            "- Cada módulo tiene entre 2 y 6 temas, ordenados de lo básico a lo avanzado.\n"
            "- Dimensiona módulos y temas según la duración estimada y el público objetivo.\n"
            "- Escribe en español.\n\n"
            f"Responde solo con un JSON con este formato:\n{_FORMATO}"
        )

    @staticmethod
    def _parsear(texto: str) -> CursoPlan:
        ini, fin = texto.find("{"), texto.rfind("}")
        if ini == -1 or fin <= ini:
            raise ValueError("no se encontró un objeto JSON en la respuesta")
        return CursoPlan.model_validate(json.loads(texto[ini : fin + 1]))

    @staticmethod
    def _fusionar(c: Configurador, plan: CursoPlan) -> CursoPlan:
        """Lo que el usuario dio manda siempre sobre lo que diseñó el modelo."""
        modulos = plan.modulos
        if c.contenido.modulos_modo == "manual" and c.contenido.modulos:
            disenados = {m.titulo.strip().lower(): m.temas for m in plan.modulos}
            modulos = []
            for i, dado in enumerate(c.contenido.modulos):
                if dado.temas:
                    temas = dado.temas
                else:
                    temas = disenados.get(dado.titulo.strip().lower()) or (
                        plan.modulos[i].temas if i < len(plan.modulos) else None
                    )
                if not temas:
                    raise ValueError(f"el plan no incluye temas para el módulo '{dado.titulo}'")
                modulos.append(ModuloPlan(titulo=dado.titulo, temas=temas))
        return CursoPlan(
            tema=c.datos.tema,
            publico_objetivo=c.datos.publico_objetivo or plan.publico_objetivo,
            duracion_estimada=c.datos.duracion_estimada or plan.duracion_estimada,
            metodologia=c.datos.metodologia or plan.metodologia,
            modulos=modulos,
        )

    @staticmethod
    def _plan_simulado(c: Configurador) -> CursoPlan:
        """Plan determinista para el modo mock (sin modelo conectado)."""
        if c.contenido.modulos_modo == "manual" and c.contenido.modulos:
            modulos = [
                ModuloPlan(titulo=m.titulo, temas=m.temas or [f"Tema {i}.{j}" for j in (1, 2, 3)])
                for i, m in enumerate(c.contenido.modulos, start=1)
            ]
        else:
            n = c.contenido.num_modulos or 3
            modulos = [
                ModuloPlan(titulo=f"Módulo {i} (simulado)", temas=[f"Tema {i}.{j} (simulado)" for j in (1, 2, 3)])
                for i in range(1, n + 1)
            ]
        return CursoPlan(
            tema=c.datos.tema,
            publico_objetivo="Público general (simulado)",
            duracion_estimada="20 horas (simulado)",
            metodologia="Aprendizaje basado en la práctica (simulado)",
            modulos=modulos,
        )
