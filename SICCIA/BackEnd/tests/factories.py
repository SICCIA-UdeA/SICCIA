"""Fábricas pequeñas y deterministas para datos y dobles de proveedores."""
from __future__ import annotations

import asyncio
import copy
import json
from collections import defaultdict
from typing import Callable

from app.orquestador.schemas import Configurador, CursoPlan


CONFIG_REFERENCIA = {
    "datos": {
        "tema": "Matematicas",
        "publico_objetivo": "Básica primaria · Grados 3.º a 5.º",
        "duracion_estimada": "12-16 horas",
        "metodologia": "Resolución de problemas",
    },
    "contenido": {
        "modulos_modo": "manual",
        "num_modulos": 4,
        "modulos": [
            {"titulo": "Sumas", "temas": []},
            {"titulo": "Restas", "temas": []},
            {"titulo": "Multiplicacion", "temas": []},
            {"titulo": "Division", "temas": []},
        ],
        "incluir_ejemplos_practicos": True,
        "incluir_talleres_practica": True,
        "incluir_cierre_por_modulo": True,
    },
    "evaluacion": {
        "tipos_pregunta": ["Selección múltiple"],
        "actividades": [
            {"tipo": "Laboratorio", "cantidad": 1, "porcentaje": 10},
            {"tipo": "Investigación", "cantidad": 1, "porcentaje": 20},
            {"tipo": "Quiz", "cantidad": 1, "porcentaje": 30},
            {"tipo": "Examen", "cantidad": 1, "porcentaje": 40},
        ],
        "total_actividades": 4,
    },
}

RESPUESTAS_CORRECTAS = {
    "contenido": "<!-- ARCHIVO: contenido_curso.md -->\n# Contenido real\nTexto del contenido.",
    "programa": (
        "<!-- ARCHIVO: programa_curso.md -->\n# Programa\n"
        "<!-- ARCHIVO: presentaciones.md -->\n# Presentaciones"
    ),
    "evaluacion": "<!-- ARCHIVO: evaluaciones.md -->\n# Evaluaciones",
    "verificacion": "<!-- ARCHIVO: verificacion.md -->\n# Verificación",
}


def crear_configurador(**cambios) -> Configurador:
    valores = copy.deepcopy(CONFIG_REFERENCIA)
    for seccion, campos in cambios.items():
        valores.setdefault(seccion, {}).update(campos)
    return Configurador.model_validate(valores)


def crear_plan(**cambios) -> CursoPlan:
    valores = {
        "tema": "Matematicas",
        "publico_objetivo": "Básica primaria · Grados 3.º a 5.º",
        "duracion_estimada": "12-16 horas",
        "metodologia": "Resolución de problemas",
        "modulos": [
            {"titulo": "Sumas", "temas": ["Sumas sin llevar", "Sumas llevando"]},
            {"titulo": "Restas", "temas": ["Restas sin prestar", "Restas prestando"]},
        ],
    }
    valores.update(cambios)
    return CursoPlan.model_validate(valores)


class FakeEjecutor:
    """Ejecutor determinista con respuestas ordenadas y barreras opcionales."""

    es_simulado = False

    def __init__(self, respuestas=None, llamadas=None, barreras=None):
        self.respuestas = defaultdict(list, respuestas or {})
        self.llamadas = llamadas if llamadas is not None else []
        self.barreras = barreras or {}
        self.ultimo_proveedor = "falso"

    async def generar(self, *, rol: str, instrucciones: str, prompt: str) -> str:
        self.llamadas.append((rol, prompt))
        if rol in self.barreras:
            iniciado, liberar = self.barreras[rol]
            iniciado.set()
            await liberar.wait()
        cola = self.respuestas[rol]
        if not cola:
            if rol == "planificador":
                plan = {
                    "tema": "Matematicas",
                    "publico_objetivo": "Básica primaria · Grados 3.º a 5.º",
                    "duracion_estimada": "12-16 horas",
                    "metodologia": "Resolución de problemas",
                    "modulos": [
                        {"titulo": "Sumas", "temas": ["Sumas sin llevar"]},
                        {"titulo": "Restas", "temas": ["Restas sin prestar"]},
                        {"titulo": "Multiplicacion", "temas": ["Multiplicación básica"]},
                        {"titulo": "Division", "temas": ["Divisiones exactas"]},
                    ],
                }
                return json.dumps(plan, ensure_ascii=False)
            return RESPUESTAS_CORRECTAS.get(rol, "")
        respuesta = cola.pop(0)
        if isinstance(respuesta, Exception):
            raise respuesta
        return respuesta


def fabrica_falsa(respuestas=None, barreras=None) -> Callable[[str], FakeEjecutor]:
    llamadas = []
    ejecutores = {}

    def crear(rol: str) -> FakeEjecutor:
        if rol not in ejecutores:
            ejecutores[rol] = FakeEjecutor(respuestas, llamadas, barreras)
        return ejecutores[rol]

    crear.llamadas = llamadas
    crear.ejecutores = ejecutores
    return crear


def plan_json():
    return {
        "tema": "Ciencias",
        "publico_objetivo": "Secundaria",
        "duracion_estimada": "10 horas",
        "metodologia": "Aprendizaje basado en problemas",
        "modulos": [{"titulo": "Materia", "temas": ["Estados"]}],
    }


def crear_sesion_flask(cliente, usuario=None, epoch=None):
    from controller.auth_controller import AuthController

    with cliente.session_transaction() as sesion:
        sesion[AuthController.SESSION_USER_KEY] = usuario or {
            "id": "usuario-prueba",
            "name": "Usuario de prueba",
            "email": "usuario@localhost",
            "picture": None,
        }
        sesion[AuthController.SESSION_EPOCH_KEY] = epoch or AuthController.SESSION_EPOCH
