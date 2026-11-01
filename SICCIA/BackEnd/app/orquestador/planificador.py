"""Completa los datos que el usuario dejó en automático y produce el ``CursoPlan``."""
from __future__ import annotations

import json
import logging
import unicodedata

from pydantic import ValidationError

from .ejecutores import EjecutorLLM
from .plantillas import perfil_metodologia, perfil_publico
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
            try:
                texto = await self._ejecutor.generar(
                    rol=self.rol, instrucciones=_INSTRUCCIONES, prompt=prompt
                )
            except Exception as exc:
                raise RuntimeError(f"El proveedor del planificador no respondió: {exc}") from exc
            if self._es_error_proveedor(texto):
                raise RuntimeError(f"El proveedor del planificador devolvió un error: {texto.strip()}")
            try:
                return self._fusionar(config, self._parsear(texto))
            except (ValueError, ValidationError) as exc:
                ultimo_error = exc
                log.warning("Planificador: respuesta inválida (intento %s): %s", intento, exc)
                prompt += "\n\nTu respuesta anterior no fue un JSON válido con ese formato. Corrígela."
        raise RuntimeError(f"El planificador no devolvió un plan válido: {ultimo_error}")

    @staticmethod
    def _es_error_proveedor(texto: str) -> bool:
        texto_normalizado = texto.lower()
        return any(
            indicador in texto_normalizado
            for indicador in (
                "rate limit",
                "free-models-per-day",
                "429",
                "404 page not found",
                "provider returned error",
            )
        )

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
        publico = perfil_publico(c.datos.publico_objetivo or "")
        cantidad_temas = "2 a 4" if publico.nivel in {"primaria", "inicial/preescolar"} else "3 a 6"
        dados = {
            "datos": c.datos.model_dump(exclude_none=True),
            "modulos_modo": c.contenido.modulos_modo,
            "num_modulos": c.contenido.num_modulos,
            "modulos_dados": [m.model_dump() for m in c.contenido.modulos],
        }
        grados = (
            f"{publico.grados[0]} a {publico.grados[1]}"
            if publico.grados else "no especificados"
        )
        return (
            "Diseña la base de un curso a partir de lo que dio el usuario.\n\n"
            f"Datos del usuario (JSON):\n{json.dumps(dados, ensure_ascii=False, indent=2)}\n\n"
            f"Debes diseñar lo que falta: {', '.join(faltantes)}.\n\n"
            f"Perfil del público: nivel {publico.nivel}, grados {grados}, "
            f"edad aproximada {publico.edad_aproximada}.\n{publico.reglas}\n"
            f"Perfil de metodología:\n{perfil_metodologia(c.datos.metodologia or '')}\n\n"
            "Reglas:\n"
            "- Conserva EXACTAMENTE los valores que el usuario sí dio (tema, módulos y temas dados).\n"
            "- En modo manual, conserva exactamente títulos, cantidad y orden de los módulos del usuario; "
            "completa solamente los temas vacíos.\n"
            "- De cada tema entrega solo el título, sin explicaciones ni contenido.\n"
            "- Si hay num_modulos, genera exactamente esa cantidad; si no, elige una cantidad razonable.\n"
            f"- Cada módulo tiene {cantidad_temas} temas, ordenados de lo simple a lo complejo, "
            "con títulos adecuados a la edad.\n"
            "- Dimensiona módulos y temas según la duración estimada y el público objetivo.\n"
            "- Escribe en español.\n\n"
            f"Responde solo con un JSON con este formato:\n{_FORMATO}"
        )

    @staticmethod
    def _parsear(texto: str) -> CursoPlan:
        decoder = json.JSONDecoder()
        for posicion, caracter in enumerate(texto):
            if caracter != "{":
                continue
            try:
                objeto, _ = decoder.raw_decode(texto[posicion:])
            except json.JSONDecodeError:
                continue
            if isinstance(objeto, dict):
                return CursoPlan.model_validate(objeto)
        raise ValueError("no se encontró un objeto JSON válido en la respuesta")

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
                    temas = disenados.get(dado.titulo.strip().lower())
                    if not temas and i < len(plan.modulos):
                        temas = plan.modulos[i].temas
                if not temas:
                    raise ValueError(
                        f"el planificador no devolvió temas para el módulo manual "
                        f"'{dado.titulo}' (posición {i + 1}); no se pueden inventar."
                    )
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
            temas_por_modulo = {
                "sumas": ["Sumas sin llevar", "Sumas llevando", "Problemas de suma"],
                "restas": ["Restas sin prestar", "Restas prestando", "Problemas de resta"],
                "multiplicacion": [
                    "Multiplicación como grupos iguales",
                    "Tablas de multiplicar",
                    "Problemas de multiplicación",
                ],
                "division": [
                    "Repartos en partes iguales",
                    "Divisiones exactas",
                    "Problemas de división",
                ],
            }

            def temas_simulados(titulo: str) -> list[str]:
                clave = "".join(
                    caracter
                    for caracter in unicodedata.normalize("NFD", titulo.lower())
                    if unicodedata.category(caracter) != "Mn"
                )
                return temas_por_modulo.get(
                    clave,
                    [
                        f"Conceptos básicos de {titulo}",
                        f"Procedimientos de {titulo}",
                        f"Problemas contextualizados de {titulo}",
                    ],
                )

            modulos = [
                ModuloPlan(
                    titulo=m.titulo,
                    temas=m.temas or temas_simulados(m.titulo),
                )
                for m in c.contenido.modulos
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
