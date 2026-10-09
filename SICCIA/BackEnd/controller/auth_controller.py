"""Endpoints HTTP para autenticación con Google."""

from flask import Blueprint, jsonify, redirect, session, url_for

if __package__ == "controller":
    from app.services.google_auth import get_google_authorize_redirect, get_google_user_info
else:
    from ..app.services.google_auth import get_google_authorize_redirect, get_google_user_info


class AuthController:
    """Registra las rutas de autenticación de Flask."""

    SESSION_USER_KEY = "user"

    def __init__(self):
        self.router = Blueprint("auth", __name__, url_prefix="/auth")
        self.router.add_url_rule("/google", endpoint="login_google", view_func=self.login_google)
        self.router.add_url_rule(
            "/google/callback", endpoint="google_callback", view_func=self.google_callback
        )
        self.router.add_url_rule("/me", endpoint="me", view_func=self.me)
        self.router.add_url_rule("/logout", endpoint="logout", view_func=self.logout)

    def login_google(self):
        """Inicia el flujo de autenticación redirigiendo a Google."""
        redirect_uri = url_for("auth.google_callback", _external=True)
        return get_google_authorize_redirect(redirect_uri)

    def google_callback(self):
        """Valida la respuesta de Google y crea la sesión de la aplicación."""
        try:
            user_info = get_google_user_info()
        except Exception:
            return jsonify({"error": "No se pudo completar la autenticación con Google"}), 401

        session[self.SESSION_USER_KEY] = user_info
        session.permanent = True
        return redirect(url_for("auth.me"))

    def me(self):
        """Devuelve los datos del usuario autenticado en la sesión actual."""
        user = session.get(self.SESSION_USER_KEY)
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

    def logout(self):
        """Elimina de la sesión los datos de usuario de la aplicación."""
        session.pop(self.SESSION_USER_KEY, None)
        return jsonify({"logged_out": True})