"""Punto de entrada para ejecutar todas las APIs del backend en el puerto 8080."""

import uvicorn

if __package__:
    from .app.server import crear_app
else:
    from app.server import crear_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
