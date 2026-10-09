"""Endpoints del orquestador de cursos."""

import io
import zipfile

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse

if __package__ == "controller":
    from app.orquestador.orquestador import Orquestador
    from app.orquestador.schemas import ArchivoInfo, Configurador, TrabajoCreado, TrabajoRespuesta
    from app.orquestador.trabajos import Trabajo
else:
    from ..app.orquestador.orquestador import Orquestador
    from ..app.orquestador.schemas import ArchivoInfo, Configurador, TrabajoCreado, TrabajoRespuesta
    from ..app.orquestador.trabajos import Trabajo


class OrquestadorController:
    def __init__(self, orquestador: Orquestador | None = None, dependencies: list | None = None):
        self.orquestador = orquestador or Orquestador()
        self.router = APIRouter(prefix="/orquestador", tags=["Orquestador"], dependencies=dependencies or [])
        r = self.router
        r.add_api_route("/cursos", self.crear_curso, methods=["POST"], status_code=202,
                        response_model=TrabajoCreado, summary="Inicia la generación de un curso")
        r.add_api_route("/cursos/{trabajo_id}", self.estado_curso, methods=["GET"],
                        response_model=TrabajoRespuesta, summary="Estado y archivos del trabajo")
        r.add_api_route("/cursos/{trabajo_id}/descarga", self.descargar_zip, methods=["GET"],
                        summary="Descarga todos los materiales en un .zip")
        r.add_api_route("/cursos/{trabajo_id}/archivos/{nombre}", self.descargar_archivo, methods=["GET"],
                        summary="Descarga un material")

    async def crear_curso(self, configurador: Configurador) -> TrabajoCreado:
        trabajo = self.orquestador.iniciar(configurador)
        return TrabajoCreado(id=trabajo.id, estado=trabajo.estado.value)

    async def estado_curso(self, trabajo_id: str) -> TrabajoRespuesta:
        trabajo = self._obtener(trabajo_id)
        return TrabajoRespuesta(
            id=trabajo.id,
            estado=trabajo.estado.value,
            creado_en=trabajo.creado_en,
            vias=dict(trabajo.vias),
            archivos=[
                ArchivoInfo(nombre=a.nombre, via=a.via, tamano_bytes=len(a.contenido.encode("utf-8")))
                for a in trabajo.archivos.values()
            ],
            error=trabajo.error,
        )

    async def descargar_archivo(self, trabajo_id: str, nombre: str) -> FileResponse:
        trabajo = self._obtener(trabajo_id)
        if nombre not in trabajo.archivos:
            raise HTTPException(404, "Archivo no encontrado")
        return FileResponse(
            trabajo.dir_resultados / nombre, media_type="text/markdown; charset=utf-8", filename=nombre
        )

    async def descargar_zip(self, trabajo_id: str) -> Response:
        trabajo = self._obtener(trabajo_id)
        if not trabajo.terminado:
            raise HTTPException(409, f"El trabajo sigue en estado '{trabajo.estado.value}'")
        if not trabajo.archivos:
            raise HTTPException(404, "El trabajo no generó archivos")
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for nombre, archivo in trabajo.archivos.items():
                zf.writestr(nombre, archivo.contenido)
        return Response(
            content=buffer.getvalue(),
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="curso_{trabajo.id[:8]}.zip"'},
        )

    def _obtener(self, trabajo_id: str) -> Trabajo:
        trabajo = self.orquestador.trabajos.obtener(trabajo_id)
        if trabajo is None:
            raise HTTPException(404, "Trabajo no encontrado")
        return trabajo