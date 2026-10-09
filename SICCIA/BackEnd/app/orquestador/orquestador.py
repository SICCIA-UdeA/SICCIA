"""Orquestador: valida → completa datos → plantilla madre → 3 vías en paralelo → recolecta."""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from pathlib import Path

from .agentes import ViaBase, ViaContenido, ViaEvaluacion, ViaPrograma
from .config import directorio_salida
from .ejecutores import EjecutorLLM, crear_ejecutor
from .planificador import Planificador
from .plantillas import construir_plantilla_madre
from .schemas import Configurador, CursoPlan
from .trabajos import EstadoTrabajo, GestorTrabajos, Trabajo

log = logging.getLogger(__name__)


class Orquestador:
    def __init__(
        self,
        directorio: Path | None = None,
        fabrica_ejecutor: Callable[[str], EjecutorLLM] = crear_ejecutor,
    ):
        self.trabajos = GestorTrabajos(directorio or directorio_salida())
        self._fabrica = fabrica_ejecutor
        self._tareas: set[asyncio.Task] = set()

    # ------------------------------------------------------------------ API
    def iniciar(self, config: Configurador) -> Trabajo:
        """Registra el trabajo y lo lanza en segundo plano. Debe llamarse con el loop activo."""
        trabajo = self.trabajos.crear()
        tarea = asyncio.create_task(self._procesar(trabajo, config))
        self._tareas.add(tarea)
        tarea.add_done_callback(self._tareas.discard)
        return trabajo

    # --------------------------------------------------------------- pipeline
    def _crear_vias(self) -> list[ViaBase]:
        return [
            ViaEvaluacion(self._fabrica("evaluacion")),
            ViaContenido(self._fabrica("contenido")),
            ViaPrograma(self._fabrica("programa")),
        ]

    async def _procesar(self, trabajo: Trabajo, config: Configurador) -> None:
        try:
            trabajo.estado = EstadoTrabajo.PLANIFICANDO
            plan = await Planificador(self._fabrica("planificador")).completar(config)
            madre = construir_plantilla_madre(plan)
            self._guardar_interno(trabajo, "configurador.json", config.model_dump_json(indent=2))
            self._guardar_interno(trabajo, "plan_curso.json", plan.model_dump_json(indent=2))
            self._guardar_interno(trabajo, "plantilla_madre.md", madre)

            vias = self._crear_vias()
            trabajo.estado = EstadoTrabajo.EJECUTANDO
            trabajo.vias = {v.rol: "en_curso" for v in vias}
            resultados = await asyncio.gather(*(self._correr_via(trabajo, v, madre, config, plan) for v in vias))

            exitosas = sum(resultados)
            if exitosas == len(vias):
                trabajo.estado = EstadoTrabajo.COMPLETADO
            elif exitosas > 0:
                trabajo.estado = EstadoTrabajo.COMPLETADO_CON_ERRORES
            else:
                trabajo.estado = EstadoTrabajo.ERROR
                trabajo.error = "Ninguna vía de trabajo terminó correctamente"
        except Exception as exc:  # noqa: BLE001 - el trabajo debe quedar marcado, no perderse
            log.exception("Trabajo %s falló", trabajo.id)
            trabajo.estado = EstadoTrabajo.ERROR
            trabajo.error = str(exc)

    async def _correr_via(
        self, trabajo: Trabajo, via: ViaBase, madre: str, config: Configurador, plan: CursoPlan
    ) -> bool:
        """Una vía que falla no cancela a las demás."""
        try:
            resultado = await via.ejecutar(madre, config, plan)
            self._guardar_interno(trabajo, f"subplantilla_{via.rol}.md", resultado.subplantilla)
            for archivo in resultado.archivos:
                (trabajo.dir_resultados / archivo.nombre).write_text(archivo.contenido, encoding="utf-8")
                trabajo.archivos[archivo.nombre] = archivo
            trabajo.vias[via.rol] = "completada"
            return True
        except Exception as exc:  # noqa: BLE001
            log.exception("Vía %s falló en el trabajo %s", via.rol, trabajo.id)
            trabajo.vias[via.rol] = f"error: {exc}"
            return False

    @staticmethod
    def _guardar_interno(trabajo: Trabajo, nombre: str, contenido: str) -> None:
        (trabajo.dir_interno / nombre).write_text(contenido, encoding="utf-8")
