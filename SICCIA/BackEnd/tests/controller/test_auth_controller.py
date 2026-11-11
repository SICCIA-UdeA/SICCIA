import logging
from types import SimpleNamespace

import pytest

from app.config import Config
from app.services import google_auth
from controller.auth_controller import AuthController
from tests.factories import crear_sesion_flask


def test_auth_google_redirige_con_uri_y_prompt_configurados(cliente_flask, monkeypatch):
    # Arrange
    llamadas = []

    def autorizar(uri):
        llamadas.append(uri)
        from flask import redirect

        return redirect("https://accounts.google.com/?prompt=select_account&state=estado-prueba")

    monkeypatch.setattr("controller.auth_controller.get_google_authorize_redirect", autorizar)

    # Act
    respuesta = cliente_flask.get("/auth/google")

    # Assert
    assert respuesta.status_code == 302
    assert llamadas == [Config.GOOGLE_REDIRECT_URI]
    assert "prompt=select_account" in respuesta.headers["Location"]
    assert "state=estado-prueba" in respuesta.headers["Location"]


def test_auth_google_error_proveedor_devuelve_error_controlado(cliente_flask, monkeypatch):
    # Arrange
    monkeypatch.setattr(
        "controller.auth_controller.get_google_authorize_redirect",
        lambda uri: (_ for _ in ()).throw(RuntimeError("proveedor fuera")),
    )

    # Act
    respuesta = cliente_flask.get("/auth/google")

    # Assert
    assert respuesta.status_code == 500
    assert b"Internal Server Error" in respuesta.data


def test_auth_callback_usuario_crea_sesion_temporal_y_redirige(cliente_flask, monkeypatch):
    # Arrange
    usuario = {"id": "id-prueba", "name": "Persona", "email": "persona@localhost", "picture": None}
    monkeypatch.setattr("controller.auth_controller.get_google_user_info", lambda: usuario)

    # Act
    respuesta = cliente_flask.get("/auth/google/callback")

    # Assert
    assert respuesta.status_code == 302
    with cliente_flask.session_transaction() as sesion:
        assert sesion["user"] == usuario
        assert sesion["epoch"] == AuthController.SESSION_EPOCH
        assert sesion.permanent is False


def test_auth_callback_sesion_establece_cookie_segura(cliente_flask, monkeypatch):
    # Arrange
    monkeypatch.setattr(
        "controller.auth_controller.get_google_user_info",
        lambda: {"id": "id", "name": "Persona", "email": "persona@localhost", "picture": None},
    )

    # Act
    respuesta = cliente_flask.get("/auth/google/callback")

    # Assert
    cookie = respuesta.headers["Set-Cookie"]
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie


def test_auth_rutas_con_cambios_de_estado_solo_permiten_logout():
    # Arrange
    from app import create_app

    # Act
    rutas = {
        (regla.rule, frozenset(regla.methods & {"POST", "PUT", "PATCH", "DELETE"}))
        for regla in create_app().url_map.iter_rules()
        if regla.methods & {"POST", "PUT", "PATCH", "DELETE"}
    }

    # Assert
    assert rutas == {("/auth/logout", frozenset({"POST"}))}


def test_auth_callback_estado_invalido_no_crea_sesion(cliente_flask):
    # Arrange
    cliente = cliente_flask

    # Act
    respuesta = cliente.get("/auth/google/callback?state=invalido&code=x")

    # Assert
    assert respuesta.status_code == 401
    assert respuesta.json == {"error": "No se pudo completar la autenticación con Google"}
    assert cliente.get("/auth/me").status_code == 401


def test_auth_callback_error_devuelve_401_y_registra_excepcion(cliente_flask, monkeypatch, caplog):
    # Arrange
    monkeypatch.setattr(
        "controller.auth_controller.get_google_user_info",
        lambda: (_ for _ in ()).throw(RuntimeError("detalle interno")),
    )

    # Act
    with caplog.at_level(logging.ERROR, logger="controller.auth_controller"):
        respuesta = cliente_flask.get("/auth/google/callback")

    # Assert
    assert respuesta.status_code == 401
    assert b"detalle interno" not in respuesta.data
    assert "No se pudo procesar el callback" in caplog.text


def test_auth_me_sesion_valida_no_cachea_y_devuelve_usuario(cliente_flask):
    # Arrange
    crear_sesion_flask(cliente_flask)

    # Act
    respuesta = cliente_flask.get("/auth/me")

    # Assert
    assert respuesta.status_code == 200
    assert respuesta.json["authenticated"] is True
    assert respuesta.headers["Cache-Control"] == "no-store"


@pytest.mark.parametrize("epoch", ["epoch-antiguo", None])
def test_auth_me_sesion_ausente_o_epoch_antiguo_no_autentica(cliente_flask, epoch):
    # Arrange
    if epoch:
        crear_sesion_flask(cliente_flask, epoch=epoch)

    # Act
    respuesta = cliente_flask.get("/auth/me")

    # Assert
    assert respuesta.status_code == 401
    assert respuesta.json == {"authenticated": False}


@pytest.mark.parametrize("metodo", ["get", "post"])
def test_auth_logout_limpia_sesion_de_manera_idempotente(cliente_flask, metodo):
    # Arrange
    crear_sesion_flask(cliente_flask)

    # Act
    respuesta = getattr(cliente_flask, metodo)("/auth/logout")

    # Assert
    assert respuesta.status_code == 200
    assert respuesta.json == {"logged_out": True}
    assert respuesta.headers["Cache-Control"] == "no-store"
    assert cliente_flask.get("/auth/me").status_code == 401


def test_auth_logout_sin_sesion_sigue_respondiendo_ok(cliente_flask):
    # Arrange
    cliente = cliente_flask

    # Act
    respuesta = cliente.get("/auth/logout")

    # Assert
    assert respuesta.status_code == 200
    assert respuesta.json["logged_out"] is True


def test_auth_controller_login_con_uri_derivada(cliente_flask, monkeypatch):
    # Arrange
    monkeypatch.setattr(Config, "GOOGLE_REDIRECT_URI", None)
    llamadas = []
    monkeypatch.setattr(
        "controller.auth_controller.get_google_authorize_redirect",
        lambda uri: llamadas.append(uri) or SimpleNamespace(status_code=200),
    )

    # Act
    with cliente_flask.application.test_request_context():
        respuesta = AuthController().login_google()

    # Assert
    assert respuesta.status_code == 200
    assert llamadas[0].endswith("/auth/google/callback")


def test_google_auth_helper_pide_seleccion_de_cuenta(monkeypatch):
    # Arrange
    llamadas = []
    cliente = SimpleNamespace(
        authorize_redirect=lambda uri, **kwargs: llamadas.append((uri, kwargs)) or "redirigido"
    )
    monkeypatch.setattr(google_auth, "oauth", SimpleNamespace(google=cliente))

    # Act
    resultado = google_auth.get_google_authorize_redirect(Config.GOOGLE_REDIRECT_URI)

    # Assert
    assert resultado == "redirigido"
    assert llamadas[0][1] == {"prompt": "select_account"}
