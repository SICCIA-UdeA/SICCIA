import json

import pytest

from app.orquestador.planificador import Planificador
from app.orquestador.schemas import CursoPlan, ModuloConfig
from tests.factories import FakeEjecutor, crear_configurador, plan_json


@pytest.mark.parametrize(
    ("config", "esperado"),
    [
        (crear_configurador(datos={"publico_objetivo": None}), "publico_objetivo"),
        (crear_configurador(contenido={"modulos_modo": "automatico"}), "modulos y temas"),
    ],
)
def test_planificador_faltantes_identifica_datos_automaticos(config, esperado):
    # Arrange
    entrada = config

    # Act
    faltantes = Planificador._faltantes(entrada)

    # Assert
    assert esperado in faltantes


def test_planificador_plan_desde_config_conserva_modulos(config_referencia):
    # Arrange
    config_referencia.contenido.modulos = [
        ModuloConfig(titulo="Sumas", temas=["Suma"]),
        ModuloConfig(titulo="Restas", temas=["Resta"]),
        ModuloConfig(titulo="Multiplicacion", temas=["Multiplicación"]),
        ModuloConfig(titulo="Division", temas=["División"]),
    ]
    configurador = config_referencia

    # Act
    plan = Planificador._plan_desde_config(configurador)

    # Assert
    assert [modulo.titulo for modulo in plan.modulos] == ["Sumas", "Restas", "Multiplicacion", "Division"]


def test_planificador_parsea_json_embebido_en_texto():
    # Arrange
    texto = f"Plan generado:\n{CursoPlan.model_validate(plan_json()).model_dump_json()}\nFin."

    # Act
    plan = Planificador._parsear(texto)

    # Assert
    assert plan.modulos[0].temas == ["Estados"]


def test_planificador_parsear_sin_json_lanza_value_error():
    # Arrange
    texto = "No hay objeto estructurado"

    # Act
    with pytest.raises(ValueError, match="no se encontró"):
        Planificador._parsear(texto)

    # Assert
    assert texto


def test_planificador_fusiona_preferencias_del_usuario():
    # Arrange
    configurador = crear_configurador(
        datos={"tema": "Tema del usuario", "publico_objetivo": None},
        contenido={"modulos": [{"titulo": "Mi módulo", "temas": []}]},
    )
    generado = CursoPlan.model_validate({**plan_json(), "modulos": [{"titulo": "Mi módulo", "temas": ["Tema sugerido"]}]})

    # Act
    fusionado = Planificador._fusionar(configurador, generado)

    # Assert
    assert fusionado.tema == "Tema del usuario"
    assert fusionado.modulos[0].titulo == "Mi módulo"


def test_planificador_fusionar_modulo_sin_temas_rechaza():
    # Arrange
    configurador = crear_configurador(
        contenido={
            "modulos": [
                {"titulo": "Módulo uno", "temas": []},
                {"titulo": "Sin temas", "temas": []},
            ]
        }
    )
    generado = CursoPlan.model_validate({**plan_json(), "modulos": [{"titulo": "Otro", "temas": ["Tema"]}]})

    # Act
    with pytest.raises(ValueError, match="no devolvió temas") as error:
        Planificador._fusionar(configurador, generado)

    # Assert
    assert "Sin temas" in str(error.value)


def test_planificador_plan_simulado_completa_modulos_manuales(config_referencia):
    # Arrange
    configurador = config_referencia

    # Act
    plan = Planificador._plan_simulado(configurador)

    # Assert
    assert plan.modulos[0].temas
    assert plan.modulos[2].titulo == "Multiplicacion"


@pytest.mark.parametrize("texto", ["429 límite", "rate limit", "provider returned error"])
def test_planificador_detecta_error_del_proveedor(texto):
    # Arrange
    respuesta = texto

    # Act
    es_error = Planificador._es_error_proveedor(respuesta)

    # Assert
    assert es_error


async def test_planificador_completar_sin_datos_faltantes_devuelve_config(config_referencia):
    # Arrange
    config_referencia.contenido.modulos = [
        ModuloConfig(titulo="Sumas", temas=["Suma básica"])
    ]
    planificador = Planificador(FakeEjecutor())

    # Act
    plan = await planificador.completar(config_referencia)

    # Assert
    assert plan.tema == config_referencia.datos.tema


async def test_planificador_completar_reintenta_respuesta_invalida():
    # Arrange
    config = crear_configurador(
        datos={"publico_objetivo": None},
        contenido={"modulos": [{"titulo": "Materia", "temas": []}]},
    )
    fake = FakeEjecutor({"planificador": ["texto", json.dumps(plan_json())]})

    # Act
    plan = await Planificador(fake).completar(config)

    # Assert
    assert plan.tema == config.datos.tema


async def test_planificador_completar_devuelve_error_del_proveedor():
    # Arrange
    config = crear_configurador(datos={"metodologia": None})
    fake = FakeEjecutor({"planificador": ["rate limit: temporal"]})

    # Act
    with pytest.raises(RuntimeError, match="devolvió un error"):
        await Planificador(fake).completar(config)

    # Assert
    assert fake.llamadas[0][0] == "planificador"


async def test_planificador_completar_dos_respuestas_invalidas_falla():
    # Arrange
    config = crear_configurador(datos={"metodologia": None})
    fake = FakeEjecutor({"planificador": ["invalido", "tampoco es JSON"]})

    # Act
    with pytest.raises(RuntimeError, match="no devolvió un plan válido"):
        await Planificador(fake).completar(config)

    # Assert
    assert len(fake.llamadas) == 2


async def test_planificador_completar_proveedor_inaccesible_expone_error():
    # Arrange
    config = crear_configurador(datos={"metodologia": None})
    fake = FakeEjecutor({"planificador": [ConnectionError("sin proveedor") ]})

    # Act
    with pytest.raises(RuntimeError, match="no respondió"):
        await Planificador(fake).completar(config)

    # Assert
    assert len(fake.llamadas) == 1
