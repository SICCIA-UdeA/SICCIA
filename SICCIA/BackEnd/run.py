"""Punto de entrada para ejecutar todas las APIs del backend."""

import os
import uvicorn

if __package__:
    from .app.server import crear_app
else:
    from app.server import crear_app

app = crear_app()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("BACKEND_PORT", "8084")))
