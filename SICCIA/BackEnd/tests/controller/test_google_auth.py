from types import SimpleNamespace

import pytest

from app.services import google_auth


def test_google_auth_normaliza_datos_del_token(monkeypatch):
    # Arrange
    perfil = {"sub": "id-prueba", "name": "Persona", "email": "persona@localhost", "picture": "foto"}
    cliente = SimpleNamespace(authorize_access_token=lambda: {"userinfo": perfil})
    monkeypatch.setattr(google_auth, "oauth", SimpleNamespace(google=cliente))

    # Act
    usuario = google_auth.get_google_user_info()

    # Assert
    assert usuario == {
        "id": "id-prueba",
        "name": "Persona",
        "email": "persona@localhost",
        "picture": "foto",
    }


def test_google_auth_consulta_fallback_de_userinfo(monkeypatch):
    # Arrange
    cliente = SimpleNamespace(
        authorize_access_token=lambda: {"access_token": "valor-de-prueba"},
        userinfo=lambda token: {"sub": token["access_token"]},
    )
    monkeypatch.setattr(google_auth, "oauth", SimpleNamespace(google=cliente))

    # Act
    usuario = google_auth.get_google_user_info()

    # Assert
    assert usuario["id"] == "valor-de-prueba"
    assert usuario["name"] is None


def test_google_auth_propaga_error_del_proveedor(monkeypatch):
    # Arrange
    cliente = SimpleNamespace(
        authorize_access_token=lambda: (_ for _ in ()).throw(RuntimeError("respuesta no válida"))
    )
    monkeypatch.setattr(google_auth, "oauth", SimpleNamespace(google=cliente))

    # Act
    with pytest.raises(RuntimeError, match="respuesta no válida"):
        google_auth.get_google_user_info()

    # Assert
    assert google_auth.oauth.google is cliente


def test_google_auth_inicializa_registro_oauth(monkeypatch):
    # Arrange
    llamadas = []
    oauth_falso = SimpleNamespace(
        init_app=lambda app: llamadas.append(("app", app)),
        register=lambda **kwargs: llamadas.append(("register", kwargs)),
    )
    monkeypatch.setattr(google_auth, "oauth", oauth_falso)
    app = SimpleNamespace(
        config={
            "GOOGLE_CLIENT_ID": "valor-de-prueba",
            "GOOGLE_CLIENT_SECRET": "valor-de-prueba",
            "GOOGLE_DISCOVERY_URL": "https://accounts.google.com/.well-known/openid-configuration",
        }
    )

    # Act
    resultado = google_auth.init_google_oauth(app)

    # Assert
    assert resultado is oauth_falso
    assert llamadas[1][1]["client_kwargs"]["scope"] == "openid email profile"
