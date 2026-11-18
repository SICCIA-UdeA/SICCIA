"""
Inicialización de la aplicación Flask (application factory).

Se usa el patrón "application factory" (una función `create_app()` que
construye y devuelve la app) en lugar de una instancia global de Flask
en el nivel del módulo. Esto facilita crear varias instancias de la
app (por ejemplo, una para tests con configuración distinta) y evita
problemas de importación circular a medida que la aplicación crezca.
"""

from flask import Flask
from flask_wtf.csrf import CSRFProtect

from .config import Config
from .services.google_auth import init_google_oauth


def create_app():
    """Crea y configura la instancia de la aplicación Flask."""
    Config.validate()

    # Seguridad (CSRF), Security Hotspot python:S4502 revisado:
    # se habilita CSRFProtect para proteger todas las peticiones con estado:
    #  - /auth/google y /auth/google/callback: flujo OAuth protegido por el parámetro `state`.
    #  - /auth/me: solo lectura.
    #  - /auth/logout: únicamente cierra la sesión.
    # CSRFProtect aplica a solicitudes de estado sin eximir rutas ni formularios.
    # La cookie de sesión es HttpOnly y SameSite=Lax (ver Config).
    app = Flask(__name__)
    csrf = CSRFProtect()
    csrf.init_app(app)
    app.config.from_object(Config)

    # Registra el proveedor de Google en el cliente OAuth (Authlib).
    init_google_oauth(app)

    # Registra las rutas de autenticación bajo el prefijo /auth.
    if __package__ == "app":
        from controller.auth_controller import AuthController
    else:
        from ..controller.auth_controller import AuthController

    app.register_blueprint(AuthController().router)

    return app
