"""Endpoints HTTP para autenticación con Google."""

import logging
import secrets

from flask import Blueprint, current_app, jsonify, make_response, redirect, session, url_for

logger = logging.getLogger(__name__)

if __package__ == "controller":
    from app.services.google_auth import get_google_authorize_redirect, get_google_user_info
else:
    from ..app.services.google_auth import get_google_authorize_redirect, get_google_user_info


class AuthController:
    """Registra las rutas de autenticación de Flask."""

    SESSION_USER_KEY = "user"
    SESSION_EPOCH_KEY = "epoch"
    SESSION_EPOCH = secrets.token_urlsafe(24)

    def __init__(self):
        self.router = Blueprint("auth", __name__, url_prefix="/auth")
        self.router.add_url_rule("/google", endpoint="login_google", view_func=self.login_google)
        self.router.add_url_rule(
            "/google/callback", endpoint="google_callback", view_func=self.google_callback
        )
        self.router.add_url_rule("/me", endpoint="me", view_func=self.me)
        self.router.add_url_rule(
            "/logout", endpoint="logout", view_func=self.logout, methods=["GET", "POST"]
        )

    def login_google(self):
        """Inicia el flujo de autenticación redirigiendo a Google."""
        redirect_uri = current_app.config.get("GOOGLE_REDIRECT_URI") or url_for(
            "auth.google_callback", _external=True
        )
        return get_google_authorize_redirect(redirect_uri)

    def google_callback(self):
        """Valida la respuesta de Google y crea la sesión de la aplicación."""
        try:
            user_info = get_google_user_info()
        except Exception:
            logger.exception("No se pudo procesar el callback OAuth de Google")
            response = make_response(
                jsonify({"error": "No se pudo completar la autenticación con Google"}), 401
            )
            response.headers["Cache-Control"] = "no-store"
            return response

        session[self.SESSION_USER_KEY] = user_info
        session[self.SESSION_EPOCH_KEY] = self.SESSION_EPOCH
        session.permanent = False
        return redirect(url_for("auth.me"))

    def me(self):
        """Devuelve los datos del usuario autenticado en la sesión actual."""
        user = session.get(self.SESSION_USER_KEY)
        autenticado = bool(user) and session.get(self.SESSION_EPOCH_KEY) == self.SESSION_EPOCH
        if autenticado:
            response = make_response(jsonify({
                "authenticated": True,
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "picture": user["picture"],
            }))
        else:
            response = make_response(jsonify({"authenticated": False}), 401)
        response.headers["Cache-Control"] = "no-store"
        return response

    def logout(self):
        """Elimina completamente la sesión y evita cachear la respuesta."""
        session.clear()
        response = make_response(jsonify({"logged_out": True}))
        response.delete_cookie(
            current_app.config.get("SESSION_COOKIE_NAME", "session"),
            path=current_app.config.get("SESSION_COOKIE_PATH", "/"),
        )
        response.headers["Cache-Control"] = "no-store"
        return response