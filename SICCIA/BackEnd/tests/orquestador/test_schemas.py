import pytest
from pydantic import ValidationError

from app.orquestador.schemas import Configurador, TrabajoRespuesta


def test_configurador_valido_con_actividad_y_campos_extra_ignora_extras(config_referencia):
    # Arrange
    datos = config_referencia.model_dump()
    datos["estilo"] = "campo antiguo"

    # Act
    configurador = Configurador.model_validate(datos)

    # Assert
    assert configurador.datos.tema == "Matematicas"
    assert not hasattr(configurador, "estilo")


@pytest.mark.parametrize("tema", ["", "ab"])
def test_configurador_tema_corto_rechaza(tema):
    # Arrange
    datos = {"datos": {"tema": tema}}

    # Act
    with pytest.raises(ValidationError):
        Configurador.model_validate(datos)

    # Assert
    assert tema == "" or len(tema) < 3


def test_contenido_manual_sin_modulos_rechaza():
    # Arrange
    datos = {"datos": {"tema": "Matematicas"}, "contenido": {"modulos_modo": "manual"}}

    # Act
    with pytest.raises(ValidationError, match="requiere al menos un módulo") as error:
        Configurador.model_validate(datos)

    # Assert
    assert "manual" in str(error.value)


@pytest.mark.parametrize(
    "porcentajes",
    [[40, 50], [60, 50]],
)
def test_evaluacion_porcentajes_no_suman_cien_rechaza(porcentajes):
    # Arrange
    datos = {
        "datos": {"tema": "Matematicas"},
        "evaluacion": {
            "actividades": [
                {"tipo": "Quiz", "porcentaje": porcentajes[0]},
                {"tipo": "Examen", "porcentaje": porcentajes[1]},
            ]
        },
    }

    # Act
    with pytest.raises(ValidationError, match="porcentajes de evaluación suman"):
        Configurador.model_validate(datos)

    # Assert
    assert sum(porcentajes) != 100


def test_trabajo_respuesta_incluye_advertencias():
    # Arrange
    datos = {
        "id": "trabajo-prueba",
        "estado": "completado_con_errores",
        "creado_en": "2026-01-01T00:00:00Z",
        "vias": {},
        "archivos": [],
        "advertencias": ["PDF no disponible"],
    }

    # Act
    respuesta = TrabajoRespuesta.model_validate(datos)

    # Assert
    assert respuesta.advertencias == ["PDF no disponible"]


def test_actividad_porcentaje_superior_a_cien_rechaza():
    # Arrange
    datos = {
        "datos": {"tema": "Matematicas"},
        "evaluacion": {"actividades": [{"tipo": "Quiz", "porcentaje": 101}]},
    }

    # Act
    with pytest.raises(ValidationError):
        Configurador.model_validate(datos)

    # Assert
    assert datos["evaluacion"]["actividades"][0]["porcentaje"] > 100
