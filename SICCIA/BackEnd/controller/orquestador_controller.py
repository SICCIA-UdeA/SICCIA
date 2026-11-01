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
                ArchivoInfo(nombre=a.nombre, via=a.via, tamano_bytes=self._tamano(trabajo, a))
                for a in trabajo.archivos.values()
            ],
            error=trabajo.error,
            advertencias=list(trabajo.advertencias),
        )

    async def descargar_archivo(self, trabajo_id: str, nombre: str) -> FileResponse:
        trabajo = self._obtener(trabajo_id)
        if "/" in nombre or "\\" in nombre:
            raise HTTPException(400, "El nombre del archivo no puede contener separadores de ruta")
        if nombre not in trabajo.archivos:
            raise HTTPException(404, "Archivo no encontrado")
        ruta = trabajo.dir_resultados / nombre
        if ruta.resolve().parent != trabajo.dir_resultados.resolve():
            raise HTTPException(400, "Nombre de archivo no válido")
        if not ruta.exists():
            raise HTTPException(404, "El archivo ya no está en disco")
        tipo = "application/pdf" if nombre.endswith(".pdf") else "text/markdown; charset=utf-8"
        return FileResponse(ruta, media_type=tipo, filename=nombre)

    async def descargar_zip(self, trabajo_id: str) -> Response:
        trabajo = self._obtener(trabajo_id)
        if not trabajo.terminado:
            raise HTTPException(409, f"El trabajo sigue en estado '{trabajo.estado.value}'")
        if trabajo.estado.value == "error":
            raise HTTPException(409, trabajo.error or "El trabajo terminó con error")
        pdfs = [nombre for nombre in trabajo.archivos if nombre.lower().endswith(".pdf")]
        if not pdfs:
            motivo = "; ".join(trabajo.advertencias) or trabajo.error or "No se generó ningún PDF."
            raise HTTPException(500, f"No hay PDF disponibles: {motivo}")
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for nombre in pdfs:
                ruta = trabajo.dir_resultados / nombre
                if not ruta.is_file() or ruta.stat().st_size == 0:
                    raise HTTPException(
                        410, f"El PDF '{nombre}' ya no está disponible o está vacío en disco"
                    )
                zf.write(ruta, arcname=nombre)
        return Response(
            content=buffer.getvalue(),
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="curso_{trabajo.id[:8]}.zip"'},
        )

    def _tamano(self, trabajo: Trabajo, archivo) -> int:
        ruta = trabajo.dir_resultados / archivo.nombre
        if ruta.exists():
            return ruta.stat().st_size
        return len(archivo.contenido.encode("utf-8"))

    def _obtener(self, trabajo_id: str) -> Trabajo:
        trabajo = self.orquestador.trabajos.obtener(trabajo_id)
        if trabajo is None:
            raise HTTPException(404, "Trabajo no encontrado")
        return trabajo