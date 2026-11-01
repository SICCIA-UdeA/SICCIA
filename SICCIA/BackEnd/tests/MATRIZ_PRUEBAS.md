# Matriz de pruebas unitarias

## Trazabilidad funcional

| Área | Funcionalidad cubierta | Pruebas |
|---|---|---|
| `orquestador` | Configuración de proveedores y agentes, validación de esquemas, planificación de cursos, plantillas y subplantillas para las vías de contenido, evaluación y verificación | `orquestador/test_config.py`, `test_schemas.py`, `test_planificador.py`, `test_plantillas.py`, `test_subplantillas_vias.py` |
| `secuence` | Selección y ejecución de proveedores, parsing y validación de respuestas de agentes, flujo por fases, ciclo de vida de trabajos y exportación de PDF/Markdown/ZIP, incluidos errores y dependencias opcionales | `secuence/test_ejecutores.py`, `test_respuestas_vias.py`, `test_flujo_fases.py`, `test_trabajos.py`, `test_exportador_pdf.py` |
| `controller` | Endpoints de autenticación y sesión, integración OAuth simulada, configuración y montaje del servidor, endpoints del orquestador, estados, respuestas de error y descargas | `controller/test_auth_controller.py`, `test_google_auth.py`, `test_server.py`, `test_orquestador_controller.py` |

Las pruebas usan dobles controlados para proveedores y OAuth; bloquean conexiones de red externas, aíslan variables de entorno y directorio de trabajo, y no requieren WeasyPrint nativo.

## Resultado y cobertura

Última ejecución completa, también repetida en orden alternativo de paquetes con el plugin de caché desactivado:

| Paquete | Casos JUnit |
|---|---:|
| `orquestador` | 67 |
| `secuence` | 92 |
| `controller` | 43 |
| **Total** | **202** |

Resultado: **201 pasaron, 1 xfailed, 0 fallaron y 0 se omitieron**. El total cuenta cada caso parametrizado por separado.

| Medida | Resultado | Umbral |
|---|---:|---:|
| Cobertura de líneas | 95.19% | 80% |
| Cobertura de ramas | 86.71% | 80% |

Todos los módulos alcanzan al menos 80% de cobertura de líneas. Los siguientes módulos quedan por debajo de 80% en ramas:

| Módulo | Líneas | Ramas |
|---|---:|---:|
| `controller/auth_controller.py` | 97.8% | 75.0% |
| `app/orquestador/app.py` | 87.5% | 50.0% |
| `app/orquestador/agentes/via_verificacion.py` | 94.6% | 77.8% |

Los reportes completos se generan en `reports/coverage.xml` y `reports/junit.xml`.

## Defecto conocido

`tests/secuence/test_respuestas_vias.py::test_via_separar_archivos_respuesta_vacia_deberia_lanzar_error` es `xfail(strict=True)`: documenta que la vía acepta una respuesta vacía en vez de lanzar `ValueError`. El `xfail` evita ocultar el defecto; si la prueba empieza a pasar, pytest lo reportará como `XPASS` y fallará para que se retire la marca.
