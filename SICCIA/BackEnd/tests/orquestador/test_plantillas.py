import pytest

from app.orquestador.plantillas import (
    _rango_horas,
    construir_plantilla_madre,
    distribucion_horaria,
    formatear_estructura,
    instrucciones_matematicas,
    perfil_metodologia,
    perfil_publico,
)


@pytest.mark.parametrize(
    ("texto", "grados"),
    [
        ("Básica primaria · Grados 3.º a 5.º", (3, 5)),
        ("Primaria 3° a 5°", (3, 5)),
        ("Primaria grados 3 a 5", (3, 5)),
        ("Primaria grados 3-5", (3, 5)),
    ],
)
def test_perfil_publico_primaria_reconoce_rangos(texto, grados):
    # Arrange
    entrada = texto

    # Act
    perfil = perfil_publico(entrada)

    # Assert
    assert perfil.nivel == "primaria"
    assert perfil.grados == grados


def test_perfil_publico_desconocido_devuelve_perfil_general():
    # Arrange
    texto = "Público sin nivel descrito"

    # Act
    perfil = perfil_publico(texto)

    # Assert
    assert perfil.nivel == "general"
    assert perfil.grados is None


def test_perfil_metodologia_resolucion_problemas_incluye_fases():
    # Arrange
    metodologia = "Resolución de problemas"

    # Act
    perfil = perfil_metodologia(metodologia)

    # Assert
    assert all(fase in perfil for fase in ("Comprender", "Planear", "Resolver", "Revisar"))


def test_perfil_metodologia_abp_conserva_aprendizaje_basado_en_problemas():
    # Arrange
    metodologia = "Aprendizaje basado en problemas"

    # Act
    perfil = perfil_metodologia(metodologia)

    # Assert
    assert "Aprendizaje basado en problemas" in perfil


def test_perfil_metodologia_desconocida_es_personalizada():
    # Arrange
    metodologia = "Método propio"

    # Act
    perfil = perfil_metodologia(metodologia)

    # Assert
    assert "Metodología personalizada" in perfil


def test_instrucciones_matematicas_primaria_evitan_contenido_avanzado():
    # Arrange
    publico = "Básica primaria · Grados 3.º a 5.º"

    # Act
    instrucciones = instrucciones_matematicas("Matematicas", publico)

    # Assert
    assert "derivadas" not in instrucciones.lower()
    assert "∫" not in instrucciones


def test_instrucciones_matematicas_tema_no_matematico_devuelve_vacio():
    # Arrange
    tema = "Historia del arte"

    # Act
    instrucciones = instrucciones_matematicas(tema)

    # Assert
    assert instrucciones == ""


def test_instrucciones_matematicas_nivel_superior_incluye_simbolos():
    # Arrange
    publico = "Universitario"

    # Act
    instrucciones = instrucciones_matematicas("Cálculo integral", publico)

    # Assert
    assert "∫" in instrucciones
    assert "d/dx" in instrucciones


@pytest.mark.parametrize(
    ("duracion", "esperado"),
    [("12-16 horas", (12, 16)), ("10 horas", (10, 10)), ("sin dato", (3, 3))],
)
def test_rango_horas_resuelve_rango_cifra_y_sin_dato(duracion, esperado):
    # Arrange
    cantidad_temas = 3

    # Act
    rango = _rango_horas(duracion, cantidad_temas)

    # Assert
    assert rango == esperado


def test_distribucion_horaria_conserva_totales_del_plan(plan_referencia):
    # Arrange
    plan = plan_referencia

    # Act
    tabla = distribucion_horaria(plan)

    # Assert
    assert "| **TOTAL** | | **12** | **16** |" in tabla
    assert tabla.count("| Sumas |") == 2


def test_formatear_estructura_numera_modulos_y_temas(plan_referencia):
    # Arrange
    plan = plan_referencia

    # Act
    estructura = formatear_estructura(plan)

    # Assert
    assert "### Módulo 1: Sumas\n1.1. Sumas sin llevar" in estructura


def test_construir_plantilla_madre_incluye_datos_perfil_y_reglas(plan_referencia):
    # Arrange
    plan = plan_referencia

    # Act
    plantilla = construir_plantilla_madre(plan)

    # Assert
    assert all(texto in plantilla for texto in ("Matematicas", "primaria", "Distribución horaria", "Reglas generales"))
