"""Orquestador: valida → completa datos → plantilla madre → 2 fases → recolecta → PDF."""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from pathlib import Path

from .agentes import ViaBase, ViaContenido, ViaEvaluacion, ViaPrograma
from .agentes.base import ArchivoGenerado
from .config import directorio_salida
from .ejecutores import EjecutorLLM, crear_ejecutor
from .planificador import Planificador
from .plantillas import construir_plantilla_madre
from .schemas import Configurador, CursoPlan
from .trabajos import EstadoTrabajo, GestorTrabajos, Trabajo

# Vía de verificación: opcional mientras el archivo no exista.
try:
    from .agentes.via_verificacion import ViaVerificacion
except ImportError:
    ViaVerificacion = None

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
        """Devuelve todas las vías registradas para inicializar los estados."""
        vias = [
            ViaEvaluacion(self._fabrica("evaluacion")),
            ViaContenido(self._fabrica("contenido")),
            ViaPrograma(self._fabrica("programa")),
        ]
        if ViaVerificacion:
            vias.append(ViaVerificacion(self._fabrica("verificacion")))
        return vias

    async def _procesar(self, trabajo: Trabajo, config: Configurador) -> None:
        try:
            trabajo.estado = EstadoTrabajo.PLANIFICANDO
            plan = await Planificador(self._fabrica("planificador")).completar(config)
            madre = construir_plantilla_madre(plan)
            self._guardar_interno(trabajo, "configurador.json", config.model_dump_json(indent=2))
            self._guardar_interno(trabajo, "plan_curso.json", plan.model_dump_json(indent=2))
            self._guardar_interno(trabajo, "plantilla_madre.md", madre)

            trabajo.estado = EstadoTrabajo.EJECUTANDO
            trabajo.vias = {v.rol: "pendiente" for v in self._crear_vias()}

            # --- FASE 1: programa y contenido en paralelo ---
            log.info("[%s] Fase 1: programa y contenido", trabajo.id)
            vias_fase_1 = [
                ViaPrograma(self._fabrica("programa")),
                ViaContenido(self._fabrica("contenido")),
            ]
            for v in vias_fase_1:
                trabajo.vias[v.rol] = "en_curso"
            resultados_fase_1 = await asyncio.gather(
                *(self._correr_via(trabajo, v, madre, config, plan) for v in vias_fase_1)
            )

            # --- FASE 2: evaluación y verificación, sobre el contenido real ---
            vias_fase_2 = [ViaEvaluacion(self._fabrica("evaluacion"))]
            if ViaVerificacion:
                vias_fase_2.append(ViaVerificacion(self._fabrica("verificacion")))

            if "contenido_curso.md" not in trabajo.archivos:
                log.warning("[%s] La fase 1 no generó contenido. Se omite la fase 2.", trabajo.id)
                for v in vias_fase_2:
                    trabajo.vias[v.rol] = "omitida"
                resultados_fase_2 = []
            else:
                texto_contenido = trabajo.archivos["contenido_curso.md"].contenido
                madre_fase_2 = (
                    madre
                    + "\n\n## ATENCIÓN: CONTENIDO REAL GENERADO\n"
                    "Básate ESTRICTAMENTE en esta teoría para tu tarea:\n\n"
                    + texto_contenido
                )
                log.info("[%s] Fase 2: evaluación y verificación", trabajo.id)
                for v in vias_fase_2:
                    trabajo.vias[v.rol] = "en_curso"
                resultados_fase_2 = await asyncio.gather(
                    *(self._correr_via(trabajo, v, madre_fase_2, config, plan) for v in vias_fase_2)
                )

            # --- COMPROBACIÓN FINAL ---
            exitosas = sum(resultados_fase_1) + sum(resultados_fase_2)
            total = len(vias_fase_1) + (len(vias_fase_2) if "contenido_curso.md" in trabajo.archivos else 0)

            if exitosas > 0:
                trabajo.estado = (
                    EstadoTrabajo.COMPLETADO if exitosas == total else EstadoTrabajo.COMPLETADO_CON_ERRORES
                )
                self._generar_pdfs(trabajo)
            else:
                trabajo.estado = EstadoTrabajo.ERROR
                trabajo.error = "Ninguna vía logró completarse."

        except Exception as exc:  # noqa: BLE001
            log.exception("Trabajo %s falló", trabajo.id)
            trabajo.estado = EstadoTrabajo.ERROR
            trabajo.error = str(exc)

    # ------------------------------------------------------------- utilidades
    def _generar_pdfs(self, trabajo: Trabajo) -> None:
        """Convierte los .md a PDF y registra los PDF. Un fallo aquí no tumba el trabajo."""
        try:
            from .exportador_pdf import WEASYPRINT_OK, procesar_imagenes_y_pdf
        except ImportError as exc:
            log.warning("[%s] No se generaron PDF: no se pudo cargar el exportador (%s)", trabajo.id, exc)
            return
        if not WEASYPRINT_OK:
            log.warning("[%s] No se generaron PDF: WeasyPrint no está instalado.", trabajo.id)
            return
        try:
            procesar_imagenes_y_pdf(trabajo.dir_resultados, trabajo.archivos)
        except Exception as exc:  # noqa: BLE001
            log.exception("[%s] Falló la generación de PDF: %s", trabajo.id, exc)
            return
        pdfs = sorted(trabajo.dir_resultados.glob("*.pdf"))
        for ruta_pdf in pdfs:
            if ruta_pdf.name not in trabajo.archivos:
                trabajo.archivos[ruta_pdf.name] = ArchivoGenerado(
                    nombre=ruta_pdf.name, contenido="", via="exportador"
                )
        log.info("[%s] PDF registrados: %d", trabajo.id, len(pdfs))

    async def _correr_via(
        self, trabajo: Trabajo, via: ViaBase, madre: str, config: Configurador, plan: CursoPlan
    ) -> bool:
        """Ejecuta una vía individual y guarda sus resultados."""
        try:
            resultado = await via.ejecutar(madre, config, plan)
            self._guardar_interno(trabajo, f"subplantilla_{via.rol}.md", resultado.subplantilla)
            for archivo in resultado.archivos:
                (trabajo.dir_resultados / archivo.nombre).write_text(archivo.contenido, encoding="utf-8")
                trabajo.archivos[archivo.nombre] = archivo
            proveedor = getattr(via._ejecutor, "ultimo_proveedor", None)
            trabajo.vias[via.rol] = (
                f"completada (proveedor: {proveedor})" if proveedor else "completada"
            )
            return True
        except Exception as exc:  # noqa: BLE001
            log.exception("Vía %s falló en el trabajo %s", via.rol, trabajo.id)
            detalle = str(exc) or type(exc).__name__
            trabajo.vias[via.rol] = f"error: {detalle}"
            return False

    @staticmethod
    def _guardar_interno(trabajo: Trabajo, nombre: str, contenido: str) -> None:
        """Guarda un archivo de depuración/log en el directorio interno del trabajo."""
        (trabajo.dir_interno / nombre).write_text(contenido, encoding="utf-8")