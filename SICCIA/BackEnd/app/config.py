"""
Configuración de la aplicación.

Este módulo centraliza la lectura de variables de entorno y expone
una clase `Config` que Flask usa para configurarse (app.config.from_object).

Mantener la configuración separada del resto del código permite:
- Agregar nuevas variables sin tocar la lógica de negocio.
- Cambiar de entorno (desarrollo / producción) sin modificar código.
- Evitar valores "hardcodeados" dispersos por la aplicación.
"""

import os

from dotenv import load_dotenv

# Carga las variables definidas en el archivo .env al entorno del proceso.
# Debe ejecutarse antes de leer cualquier os.environ / os.getenv.
load_dotenv()


class Config:
    """Configuración de la aplicación Flask."""

    # Clave usada por Flask para firmar la cookie de sesión.
    # Sin esta clave, Flask no puede crear sesiones seguras.
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")

    # Credenciales de OAuth 2.0 / OpenID Connect obtenidas en Google Cloud Console.
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

    # Documento de descubrimiento de OpenID Connect de Google.
    # Authlib lo usa para obtener automáticamente los endpoints de
    # autorización, token, userinfo y las claves públicas (JWKS)
    # necesarias para validar el id_token.
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

    # Cookies de sesión solo por HTTPS. En desarrollo local (http://localhost)
    # esto debe ser False; en producción (detrás de HTTPS) debe ser True.
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "False") == "True"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    @staticmethod
    def validate():
        """Verifica que las variables obligatorias estén definidas.

        Se llama al iniciar la aplicación para fallar rápido y con un
        mensaje claro si falta configuración, en lugar de fallar más
        tarde de forma confusa durante el flujo OAuth.
        """
        required = {
            "FLASK_SECRET_KEY": Config.SECRET_KEY,
            "GOOGLE_CLIENT_ID": Config.GOOGLE_CLIENT_ID,
            "GOOGLE_CLIENT_SECRET": Config.GOOGLE_CLIENT_SECRET,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeError(
                "Faltan variables de entorno obligatorias: "
                f"{', '.join(missing)}. Revisa tu archivo .env "
                "(puedes basarte en .env.example)."
            )
