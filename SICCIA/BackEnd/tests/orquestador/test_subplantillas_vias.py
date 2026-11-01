import pytest

from app.orquestador.agentes.via_contenido import ViaContenido
from app.orquestador.agentes.via_evaluacion import ViaEvaluacion, clasificar_actividad
from app.orquestador.agentes.via_programa import ViaPrograma
from app.orquestador.agentes.via_verificacion import ViaVerificacion
from tests.factories import FakeEjecutor


@pytest.mark.parametrize(
    ("tipo", "categoria"),
    [("Quiz", "prueba"), ("Examen", "prueba"), ("Laboratorio", "practica"), ("Taller", "practica"), ("Otro", "practica")],
)
def test_evaluacion_clasifica_actividades(tipo, categoria):
    # Arrange
    actividad = tipo

    # Act
    resultado = clasificar_actividad(actividad)

    # Assert
    assert resultado == categoria


def test_evaluacion_subplantilla_usa_tipos_pregunta_y_pesos(config_referencia, plan_referencia):
    # Arrange
    via = ViaEvaluacion(FakeEjecutor())

    # Act
    plantilla = via.construir_subplantilla(config_referencia, plan_referencia)

    # Assert
    assert "Selección múltiple" in plantilla
    assert "**TOTAL**" in plantilla
    assert "10% para el grupo" in plantilla


def test_evaluacion_subplantilla_calcula_porcentajes_no_especificados(config_referencia, plan_referencia):
    # Arrange
    config_referencia.evaluacion.actividades[0].porcentaje = None
    via = ViaEvaluacion(FakeEjecutor())

    # Act
    plantilla = via.construir_subplantilla(config_referencia, plan_referencia)

    # Assert
    assert "porcentajes no indicados se distribuyen por igual" in plantilla


def test_evaluacion_subplantilla_reporta_total_actividades_inconsistente(config_referencia, plan_referencia):
    # Arrange
    config_referencia.evaluacion.total_actividades = 20
    via = ViaEvaluacion(FakeEjecutor())

    # Act
    plantilla = via.construir_subplantilla(config_referencia, plan_referencia)

    # Assert
    assert "Total de actividades evaluativas: **4**" in plantilla


@pytest.mark.parametrize(
    ("atributo", "frase"),
    [
        ("incluir_ejemplos_practicos", "Ejemplo práctico"),
        ("incluir_talleres_practica", "Taller de práctica"),
        ("incluir_cierre_por_modulo", "Cierre del módulo"),
    ],
)
def test_contenido_subplantilla_refleja_banderas(config_referencia, plan_referencia, atributo, frase):
    # Arrange
    via = ViaContenido(FakeEjecutor())
    setattr(config_referencia.contenido, atributo, False)

    # Act
    plantilla = via.construir_subplantilla(config_referencia, plan_referencia)

    # Assert
    assert f"{frase}" not in plantilla


def test_contenido_subplantilla_prohibe_imagenes(config_referencia, plan_referencia):
    # Arrange
    via = ViaContenido(FakeEjecutor())

    # Act
    plantilla = via.construir_subplantilla(config_referencia, plan_referencia)

    # Assert
    assert "No incluyas imágenes" in plantilla


def test_programa_subplantilla_menciona_grado_minimo(config_referencia, plan_referencia):
    # Arrange
    via = ViaPrograma(FakeEjecutor())

    # Act
    plantilla = via.construir_subplantilla(config_referencia, plan_referencia)

    # Assert
    assert "grado más bajo del rango (3.º)" in plantilla


def test_programa_subplantilla_sin_rango_usa_nivel_generico(config_referencia, plan_referencia):
    # Arrange
    plan_referencia.publico_objetivo = "Público general"
    via = ViaPrograma(FakeEjecutor())

    # Act
    plantilla = via.construir_subplantilla(config_referencia, plan_referencia)

    # Assert
    assert "conocimientos previos para el nivel general" in plantilla


def test_verificacion_subplantilla_exige_veracidad_y_exactitud(config_referencia, plan_referencia):
    # Arrange
    via = ViaVerificacion(FakeEjecutor())

    # Act
    plantilla = via.construir_subplantilla(config_referencia, plan_referencia)

    # Assert
    assert "exactitud aritmética" in plantilla
    assert "Fuentes verificables" in plantilla
