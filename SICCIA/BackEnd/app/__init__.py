"""
Inicialización de la aplicación Flask (application factory).

Se usa el patrón "application factory" (una función `create_app()` que
construye y devuelve la app) en lugar de una instancia global de Flask
en el nivel del módulo. Esto facilita crear varias instancias de la
app (por ejemplo, una para tests con configuración distinta) y evita
problemas de importación circular a medida que la aplicación crezca.
"""

from flask import Flask

from .config import Config
from .services.google_auth import init_google_oauth


def create_app():
    """Crea y configura la instancia de la aplicación Flask."""
    Config.validate()

    app = Flask(__name__)
    app.config.from_object(Config)

    # Registra el proveedor de Google en el cliente OAuth (Authlib).
    init_google_oauth(app)

    # Registra las rutas de autenticación bajo el prefijo /auth.
    from .routes.auth import auth_bp

    app.register_blueprint(auth_bp)

    return app
