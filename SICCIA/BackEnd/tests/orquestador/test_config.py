import pytest

from app.orquestador import config
from app.orquestador.ejecutores import EjecutorAgno, EjecutorMock, crear_ejecutor


def test_config_modelo_mock_define_valores_predeterminados(monkeypatch):
    # Arrange
    monkeypatch.setattr(config, "_DOTENV", {})

    # Act
    modelo = config.config_modelo("contenido")

    # Assert
    assert (modelo.proveedor, modelo.max_tokens, modelo.timeout_segundos) == ("mock", 32768, 900)


@pytest.mark.parametrize(("rol", "tokens"), [("contenido", 32768), ("evaluacion", 16384)])
def test_config_modelo_asigna_tokens_por_rol(monkeypatch, rol, tokens):
    # Arrange
    monkeypatch.setattr(config, "_DOTENV", {})

    # Act
    modelo = config.config_modelo(rol)

    # Assert
    assert modelo.max_tokens == tokens


def test_config_modelo_lee_proveedor_registrado_y_respaldo(monkeypatch):
    # Arrange
    monkeypatch.setenv("ORQ_VIA_CONTENIDO", "principal")
    monkeypatch.setenv("ORQ_PROVEEDOR_PRINCIPAL_TIPO", "openai_like")
    monkeypatch.setenv("ORQ_PROVEEDOR_PRINCIPAL_MODELO", "modelo-principal")
    monkeypatch.setenv("ORQ_PROVEEDOR_PRINCIPAL_BASE_URL", "https://api.localhost/v1")
    monkeypatch.setenv("ORQ_RESPALDO_CONTENIDO", "alterno")
    monkeypatch.setenv("ORQ_PROVEEDOR_ALTERNO_TIPO", "gemini")

    # Act
    modelo = config.config_modelo("contenido")

    # Assert
    assert modelo.proveedor == "openai_like"
    assert modelo.model_id == "modelo-principal"
    assert modelo.respaldo.proveedor == "gemini"


def test_config_modelo_compatibilidad_lee_variables_por_rol(monkeypatch):
    # Arrange
    monkeypatch.setenv("ORQ_PROVEEDOR_EVALUACION", "openai")
    monkeypatch.setenv("ORQ_MODEL_ID_EVALUACION", "modelo-prueba")

    # Act
    modelo = config.config_modelo("evaluacion")

    # Assert
    assert (modelo.proveedor, modelo.model_id) == ("openai", "modelo-prueba")


def test_config_modelo_lee_respaldo_compatibilidad_por_rol(monkeypatch):
    # Arrange
    monkeypatch.setenv("ORQ_PROVEEDOR_EVALUACION", "openai")
    monkeypatch.setenv("ORQ_PROVEEDOR_RESPALDO_EVALUACION", "gemini")

    # Act
    modelo = config.config_modelo("evaluacion")

    # Assert
    assert modelo.respaldo.proveedor == "gemini"


def test_config_modelo_valor_numerico_invalido_lanza_value_error(monkeypatch):
    # Arrange
    monkeypatch.setenv("ORQ_MAX_TOKENS", "no-numero")

    # Act
    with pytest.raises(ValueError):
        config.config_modelo("contenido")

    # Assert
    assert config._env("MAX_TOKENS", "contenido") == "no-numero"


def test_config_modelo_crear_ejecutor_segun_proveedor(monkeypatch):
    # Arrange
    monkeypatch.setenv("ORQ_PROVEEDOR", "mock")

    # Act
    ejecutor = crear_ejecutor("programa")

    # Assert
    assert isinstance(ejecutor, EjecutorMock)


def test_config_modelo_proveedor_no_mock_crea_ejecutor_agno(monkeypatch):
    # Arrange
    monkeypatch.setenv("ORQ_PROVEEDOR", "openai")

    # Act
    ejecutor = crear_ejecutor("programa")

    # Assert
    assert isinstance(ejecutor, EjecutorAgno)


def test_config_modelo_lee_clave_google(monkeypatch):
    # Arrange
    monkeypatch.setenv("GOOGLE_API_KEY", "valor-de-prueba")

    # Act
    clave = config.clave_google()

    # Assert
    assert clave == "valor-de-prueba"


def test_config_modelo_directorio_salida_personalizado(monkeypatch, tmp_path):
    # Arrange
    salida = tmp_path / "salida"
    monkeypatch.setenv("ORQ_DIR_SALIDA", str(salida))

    # Act
    directorio = config.directorio_salida()

    # Assert
    assert directorio == salida
