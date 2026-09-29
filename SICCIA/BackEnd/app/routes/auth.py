"""
Endpoints de autenticación.

Este módulo SOLO define rutas HTTP: recibe peticiones, llama a la
lógica de app/services/google_auth.py, y traduce el resultado en una
respuesta HTTP (JSON o redirect). No conoce detalles internos de cómo
se habla con Google: eso vive en el servicio.
"""

from flask import Blueprint, jsonify, redirect, session, url_for

from ..services.google_auth import get_google_authorize_redirect, get_google_user_info

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Clave usada dentro de session[...] para guardar los datos del usuario.
# Centralizarla en una constante evita errores de tipeo repetidos.
SESSION_USER_KEY = "user"


@auth_bp.route("/google")
def login_google():
    """GET /auth/google

    Inicia el flujo de autenticación redirigiendo al usuario a Google.
    """
    # url_for(..., _external=True) construye la URL absoluta del
    # callback (ej. http://localhost:5000/auth/google/callback), que es
    # la misma que debe estar registrada en Google Cloud Console.
    redirect_uri = url_for("auth.google_callback", _external=True)
    return get_google_authorize_redirect(redirect_uri)


@auth_bp.route("/google/callback")
def google_callback():
    """GET /auth/google/callback

    Google redirige aquí después de que el usuario inicia sesión (o
    cancela). Se valida la respuesta, se obtienen los datos del
    usuario y se crea la sesión de la aplicación.
    """
    try:
        user_info = get_google_user_info()
    except Exception:
        # No se expone el detalle interno del error (podría filtrar
        # información sensible sobre la integración con Google).
        return jsonify({"error": "No se pudo completar la autenticación con Google"}), 401

    # Solo se guarda en la sesión de Flask la información mínima
    # necesaria para identificar al usuario en peticiones futuras.
    # No se guarda el access_token ni el id_token de Google.
    session[SESSION_USER_KEY] = user_info
    session.permanent = True

    # Como todavía no hay frontend, se responde con un mensaje simple.
    # Cuando exista un frontend, este redirect apuntaría a su URL
    # (ej. redirect("http://localhost:3000/dashboard")).
    return redirect(url_for("auth.me"))


@auth_bp.route("/me")
def me():
    """GET /auth/me

    Devuelve los datos del usuario autenticado en la sesión actual.
    """
    user = session.get(SESSION_USER_KEY)
    if not user:
        return jsonify({"authenticated": False}), 401

    return jsonify(
        {
            "authenticated": True,
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "picture": user["picture"],
        }
    )


@auth_bp.route("/logout")
def logout():
    """GET /auth/logout

    Elimina la sesión de la aplicación. Esto NO cierra la sesión de
    Google en el navegador (eso lo gestiona Google, no esta app); solo
    hace que esta aplicación deje de reconocer al usuario como
    autenticado.
    """
    session.pop(SESSION_USER_KEY, None)
    return jsonify({"logged_out": True})
