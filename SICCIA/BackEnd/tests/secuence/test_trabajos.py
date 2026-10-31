import pytest

from app.orquestador.trabajos import EstadoTrabajo, GestorTrabajos


def test_trabajo_crear_inicializa_directorios(tmp_path):
    # Arrange
    gestor = GestorTrabajos(tmp_path)

    # Act
    trabajo = gestor.crear()

    # Assert
    assert trabajo.dir_resultados.is_dir()
    assert trabajo.dir_interno.is_dir()


def test_trabajo_obtener_devuelve_trabajo_existente(tmp_path):
    # Arrange
    gestor = GestorTrabajos(tmp_path)
    trabajo = gestor.crear()

    # Act
    encontrado = gestor.obtener(trabajo.id)

    # Assert
    assert encontrado is trabajo


def test_trabajo_obtener_inexistente_devuelve_none(tmp_path):
    # Arrange
    gestor = GestorTrabajos(tmp_path)

    # Act
    encontrado = gestor.obtener("no-existe")

    # Assert
    assert encontrado is None


@pytest.mark.parametrize(
    ("estado", "terminado"),
    [
        (EstadoTrabajo.PENDIENTE, False),
        (EstadoTrabajo.PLANIFICANDO, False),
        (EstadoTrabajo.EJECUTANDO, False),
        (EstadoTrabajo.COMPLETADO, True),
        (EstadoTrabajo.COMPLETADO_CON_ERRORES, True),
        (EstadoTrabajo.ERROR, True),
    ],
)
def test_trabajo_terminado_refleja_estado(estado, terminado, tmp_path):
    # Arrange
    trabajo = GestorTrabajos(tmp_path).crear()
    trabajo.estado = estado

    # Act
    resultado = trabajo.terminado

    # Assert
    assert resultado is terminado
