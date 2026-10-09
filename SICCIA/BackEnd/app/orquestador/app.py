"""App FastAPI mínima para ejecutar el orquestador solo (en el backend real basta con el router)."""
from fastapi import FastAPI

if __package__ in {"orquestador", "app.orquestador"}:
    from controller.orquestador_controller import OrquestadorController
else:
    from ...controller.orquestador_controller import OrquestadorController


def crear_app() -> FastAPI:
    app = FastAPI(title="Orquestador de cursos")
    app.include_router(OrquestadorController().router)
    return app
