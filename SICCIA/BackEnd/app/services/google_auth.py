"""
Integración con Google OAuth 2.0 / OpenID Connect.

Este módulo es el ÚNICO lugar de la aplicación que sabe cómo hablar con
Google. El resto del código (rutas) no conoce detalles de Google: solo
llama a las funciones expuestas aquí. Esto facilita:

- Cambiar de proveedor (o agregar otro) sin tocar las rutas.
- Testear la lógica de rutas sin depender de Google.

Usa Authlib (https://docs.authlib.org/), la librería estándar y
mantenida para clientes OAuth/OIDC en Flask. Authlib se encarga de:

- Construir la URL de autorización de Google.
- Generar y validar el parámetro `state` (protección CSRF del flujo OAuth).
- Intercambiar el `code` devuelto por Google por los tokens.
- Descargar las claves públicas de Google (JWKS) y validar la firma,
  el emisor (`iss`), la audiencia (`aud`) y la expiración del `id_token`.

No se implementa nada de esto manualmente: reimplementar la validación
de un id_token a mano es una fuente común de vulnerabilidades.
"""

from authlib.integrations.flask_client import OAuth

# Instancia global de Authlib. Se inicializa (se "engancha" a la app
# Flask) en app/__init__.py mediante init_app-style, siguiendo el mismo
# patrón que otras extensiones de Flask (SQLAlchemy, LoginManager, etc.).
oauth = OAuth()


def init_google_oauth(app):
    """Registra el proveedor 'google' en el cliente OAuth de Authlib.

    Se le pasa la app de Flask para que Authlib lea GOOGLE_CLIENT_ID y
    GOOGLE_CLIENT_SECRET desde app.config, y se le indica la URL de
    descubrimiento de OpenID Connect para que obtenga automáticamente
    los endpoints y las claves de verificación de Google.
    """
    oauth.init_app(app)
    oauth.register(
        name="google",
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        server_metadata_url=app.config["GOOGLE_DISCOVERY_URL"],
        client_kwargs={
            # openid  -> habilita OpenID Connect (id_token)
            # email   -> solicita el correo electrónico
            # profile -> solicita nombre y foto de perfil
            "scope": "openid email profile",
        },
    )
    return oauth


def get_google_authorize_redirect(redirect_uri):
    """Inicia el flujo: redirige al usuario a la pantalla de login de Google.

    Authlib genera internamente el parámetro `state` (valor aleatorio
    y único por petición) y lo guarda ligado a la sesión del usuario.
    Google lo devuelve tal cual en el callback, y Authlib comprueba que
    coincide antes de continuar. Esto evita ataques de tipo CSRF sobre
    el flujo de login (un atacante no puede forzar a un usuario a
    "aceptar" una sesión iniciada por otra persona).
    """
    return oauth.google.authorize_redirect(redirect_uri)


def get_google_user_info():
    """Procesa la respuesta del callback y devuelve los datos del usuario.

    Pasos que realiza Authlib internamente al llamar a
    `authorize_access_token()`:

    1. Verifica que el `state` recibido coincide con el generado al
       iniciar el flujo (ver `get_google_authorize_redirect`).
    2. Intercambia el `code` de autorización por un `access_token` y un
       `id_token` en el endpoint de token de Google (comunicación
       servidor-a-servidor, usando GOOGLE_CLIENT_SECRET).
    3. Descarga (y cachea) las claves públicas (JWKS) de Google.
    4. Valida la firma criptográfica del `id_token`, su emisor (`iss`
       debe ser Google), su audiencia (`aud` debe ser nuestro
       GOOGLE_CLIENT_ID), y que no esté expirado ni sea válido "a
       futuro" (`exp` / `iat` / `nbf`).

    Solo si todo eso es correcto se devuelven los datos del usuario.
    Si algo falla, Authlib lanza una excepción y no se devuelve nada.
    """
    token = oauth.google.authorize_access_token()

    # 'userinfo' llega ya parseado desde el id_token verificado.
    # Es la fuente de verdad: no volvemos a llamar a Google por separado.
    user_info = token.get("userinfo")
    if not user_info:
        # Algunos proveedores no incluyen 'userinfo' automáticamente en
        # el token; como fallback, se pide explícitamente al endpoint
        # userinfo de Google usando el access_token ya validado.
        user_info = oauth.google.userinfo(token=token)

    # Se extrae y normaliza únicamente lo que la aplicación necesita.
    # 'sub' es el identificador único y estable de la cuenta de Google:
    # a diferencia del email, no cambia si el usuario cambia su correo.
    return {
        "id": user_info["sub"],
        "name": user_info.get("name"),
        "email": user_info.get("email"),
        "picture": user_info.get("picture"),
    }
