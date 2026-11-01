import pytest
from fastapi.testclient import TestClient

from app.config import Config
from app.orquestador.app import crear_app as crear_app_orquestador
from app.server import crear_app


def test_server_monta_fastapi_y_flask_en_una_app():
    # Arrange
    app = crear_app()
    cliente = TestClient(app)

    # Act
    docs = cliente.get("/docs")
    usuario = cliente.get("/auth/me")

    # Assert
    assert docs.status_code == 200
    assert usuario.status_code == 401


def test_server_configuracion_incompleta_falla_al_iniciar(monkeypatch):
    # Arrange
    monkeypatch.setattr(Config, "GOOGLE_CLIENT_ID", None)

    # Act
    with pytest.raises(RuntimeError, match="GOOGLE_CLIENT_ID"):
        crear_app()

    # Assert
    assert Config.GOOGLE_CLIENT_ID is None


@pytest.mark.parametrize(
    "valor",
    [None, "tu-credencial", "cambia-esta", "...", "pon-aqui-la-clave"],
)
def test_config_validate_rechaza_credenciales_ausentes_o_de_ejemplo(monkeypatch, valor):
    # Arrange
    monkeypatch.setattr(Config, "GOOGLE_CLIENT_SECRET", valor)

    # Act
    with pytest.raises(RuntimeError, match="GOOGLE_CLIENT_SECRET"):
        Config.validate()

    # Assert
    assert valor is None or valor.startswith(("tu-", "cambia-")) or valor in {"...", "pon-aqui-la-clave"}


def test_config_validate_acepta_credenciales_falsas_de_prueba():
    # Arrange
    configuracion = Config

    # Act
    resultado = configuracion.validate()

    # Assert
    assert resultado is None


def test_app_orquestador_monta_router_y_ruta_inexistente_devuelve_404():
    # Arrange
    cliente = TestClient(crear_app_orquestador())

    # Act
    respuesta = cliente.get("/no-existe")

    # Assert
    assert respuesta.status_code == 404


def test_app_orquestador_publica_ruta_de_cursos():
    # Arrange
    cliente = TestClient(crear_app_orquestador())

    # Act
    respuesta = cliente.get("/openapi.json")

    # Assert
    assert "/orquestador/cursos" in respuesta.json()["paths"]
