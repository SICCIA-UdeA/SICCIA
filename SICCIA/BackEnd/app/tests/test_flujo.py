"""Pruebas con el ejecutor simulado (no requieren modelos ni agno). Ejecutar: pytest"""
import json
import time
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import Config
from app.server import crear_app as crear_backend_app
from controller.orquestador_controller import OrquestadorController
from app.orquestador import Configurador, Orquestador
from app.orquestador.ejecutores import ConfiguracionProveedorError, EjecutorAgno, EjecutorMock
from app.orquestador.agentes.via_contenido import ViaContenido
from app.orquestador.agentes.base import normalizar_notacion_matematica
from app.orquestador.agentes.via_evaluacion import ViaEvaluacion
from app.orquestador.agentes.via_verificacion import ViaVerificacion
from app.orquestador.config import config_modelo
import app.orquestador.config as config_module
from app.orquestador.plantillas import (
    construir_plantilla_madre,
    distribucion_horaria,
    instrucciones_matematicas,
    perfil_metodologia,
)
from app.orquestador.planificador import Planificador

EJEMPLO = json.loads((Path(__file__).parent.parent / "ejemplo_configurador.json").read_text(encoding="utf-8"))


def _cliente(tmp_path):
    orq = Orquestador(directorio=tmp_path, fabrica_ejecutor=lambda rol: EjecutorMock())
    app = FastAPI()
    app.include_router(OrquestadorController(orq).router)
    return TestClient(app)


def test_flujo_completo_con_mock(tmp_path):
    with _cliente(tmp_path) as cliente:
        r = cliente.post("/orquestador/cursos", json=EJEMPLO)
        assert r.status_code == 202
        trabajo_id = r.json()["id"]

        for _ in range(1200):
            estado = cliente.get(f"/orquestador/cursos/{trabajo_id}").json()
            if estado["estado"] not in ("pendiente", "planificando", "ejecutando"):
                break
            time.sleep(0.05)

        assert estado["estado"] == "completado", estado
        nombres = {a["nombre"] for a in estado["archivos"] if a["nombre"].endswith(".md")}
        assert nombres == {"evaluaciones.md", "contenido_curso.md", "programa_curso.md", "presentaciones.md", "verificacion.md"}
        assert cliente.get(f"/orquestador/cursos/{trabajo_id}/descarga").status_code == 200
        assert (tmp_path / trabajo_id / "interno" / "plantilla_madre.md").exists()


def test_porcentajes_invalidos_dan_422(tmp_path):
    malo = json.loads(json.dumps(EJEMPLO))
    malo["evaluacion"]["actividades"][0]["porcentaje"] = 10
    with _cliente(tmp_path) as cliente:
        assert cliente.post("/orquestador/cursos", json=malo).status_code == 422


def test_auth_y_orquestador_comparten_servidor(monkeypatch, tmp_path):
    monkeypatch.setattr(Config, "SECRET_KEY", "test-secret-key")
    monkeypatch.setattr(Config, "GOOGLE_CLIENT_ID", "test-client")
    monkeypatch.setattr(Config, "GOOGLE_CLIENT_SECRET", "test-secret")
    monkeypatch.setenv("ORQ_PROVEEDOR", "mock")
    for rol in ("PLANIFICADOR", "EVALUACION", "CONTENIDO", "PROGRAMA", "VERIFICACION"):
        monkeypatch.setenv(f"ORQ_PROVEEDOR_{rol}", "mock")
        monkeypatch.setenv(f"ORQ_VIA_{rol}", "mock")
        monkeypatch.setenv(f"ORQ_RESPALDO_{rol}", "")
    monkeypatch.setenv("ORQ_DIR_SALIDA", str(tmp_path))

    with TestClient(crear_backend_app()) as cliente:
        auth = cliente.get("/auth/me")
        assert auth.status_code == 401
        assert auth.json() == {"authenticated": False}

        inicio = cliente.post("/orquestador/cursos", json=EJEMPLO)
        assert inicio.status_code == 202
        trabajo_id = inicio.json()["id"]

        for _ in range(1200):
            estado = cliente.get(f"/orquestador/cursos/{trabajo_id}").json()
            if estado["estado"] not in ("pendiente", "planificando", "ejecutando"):
                break
            time.sleep(0.05)

        assert estado["estado"] == "completado", estado


@pytest.mark.asyncio
async def test_plantilla_madre_contiene_estructura():
    config = Configurador.model_validate(EJEMPLO)
    plan = await Planificador(EjecutorMock()).completar(config)
    madre = construir_plantilla_madre(plan)
    assert "### Módulo 4" in madre and "4.3." in madre
    assert config.datos.publico_objetivo in madre  # lo dado por el usuario se conserva


@pytest.mark.asyncio
async def test_distribucion_horaria_reparte_y_conserva_totales():
    config = Configurador.model_validate(EJEMPLO)
    plan = await Planificador(EjecutorMock()).completar(config)

    tabla = distribucion_horaria(plan)

    assert "| **TOTAL** | | **30** | **30** |" in tabla
    assert tabla.count("| Módulo") == sum(len(m.temas) for m in plan.modulos) + 1
    assert "## Distribución horaria común y obligatoria" in construir_plantilla_madre(plan)


def test_distribucion_horaria_acepta_rango_y_no_repite_duracion_por_tema():
    config = Configurador.model_validate(EJEMPLO)
    config.datos.duracion_estimada = "12-16 horas"
    plan = Planificador._plan_simulado(config).model_copy(
        update={"duracion_estimada": config.datos.duracion_estimada}
    )

    tabla = distribucion_horaria(plan)

    assert "| **TOTAL** | | **12** | **16** |" in tabla
    assert tabla.count("| **TOTAL**") == 1


@pytest.mark.parametrize(
    ("metodologia", "frase"),
    [
        ("Resolución de problemas", "problema auténtico"),
        ("Aprendizaje por proyectos", "producto final"),
        ("Aula invertida", "preparación previa"),
        ("Aprendizaje experiencial", "experiencia concreta"),
        ("Aprendizaje cooperativo", "roles"),
    ],
)
def test_metodologia_se_convierte_en_reglas_didacticas(metodologia, frase):
    assert frase in perfil_metodologia(metodologia)


def test_tema_matematico_exige_formulas_visibles():
    reglas = instrucciones_matematicas("Integrales y derivadas")

    assert "∫" in reglas
    assert "f′(x)" in reglas
    assert "No uses delimitadores LaTeX" in reglas


def test_planificador_parsea_json_entre_texto():
    plan = Planificador._parsear(
        'Aquí está el plan:\n```json\n{"tema":"Python","publico_objetivo":"Docentes",'
        '"duracion_estimada":"10 horas","metodologia":"Práctica",'
        '"modulos":[{"titulo":"Bases","temas":["Variables"]}]}\n```\n'
    )
    assert plan.modulos[0].temas == ["Variables"]


def test_planificador_detecta_error_del_proveedor_en_el_contenido():
    assert Planificador._es_error_proveedor(
        "Error code: 429 - Rate limit exceeded: free-models-per-day"
    )


def test_via_no_guarda_respuestas_nulas():
    via = ViaContenido(EjecutorMock())

    with pytest.raises(ValueError, match="respuesta nula"):
        via._separar_archivos("None")


def test_contenido_tiene_presupuesto_ampliado():
    assert config_modelo("contenido").max_tokens == 32768


def test_configuracion_lee_proveedor_de_respaldo_por_rol(monkeypatch):
    monkeypatch.setitem(config_module._DOTENV, "ORQ_VIA_CONTENIDO", "")
    monkeypatch.setitem(config_module._DOTENV, "ORQ_RESPALDO_CONTENIDO", "")
    monkeypatch.setenv("ORQ_PROVEEDOR_CONTENIDO", "openai_like")
    monkeypatch.setenv("ORQ_MODEL_ID_CONTENIDO", "modelo-principal")
    monkeypatch.setenv("ORQ_PROVEEDOR_RESPALDO_CONTENIDO", "gemini")
    monkeypatch.setenv("ORQ_MODEL_ID_RESPALDO_CONTENIDO", "modelo-respaldo")

    cfg = config_modelo("contenido")

    assert cfg.proveedor == "openai_like"
    assert cfg.model_id == "modelo-principal"
    assert cfg.respaldo is not None
    assert cfg.respaldo.proveedor == "gemini"
    assert cfg.respaldo.model_id == "modelo-respaldo"


def test_configuracion_asocia_vias_a_un_registro_de_proveedores(monkeypatch):
    monkeypatch.setenv("ORQ_VIA_CONTENIDO", "nvidia")
    monkeypatch.setenv("ORQ_RESPALDO_CONTENIDO", "gemini")
    monkeypatch.setenv("ORQ_PROVEEDOR_NVIDIA_TIPO", "openai_like")
    monkeypatch.setenv("ORQ_PROVEEDOR_NVIDIA_API_KEY", "nvidia-key")
    monkeypatch.setenv("ORQ_PROVEEDOR_NVIDIA_BASE_URL", "https://nvidia.example/v1")
    monkeypatch.setenv("ORQ_PROVEEDOR_NVIDIA_MODELO", "nvidia/model")
    monkeypatch.setenv("ORQ_PROVEEDOR_GEMINI_TIPO", "gemini")
    monkeypatch.setenv("ORQ_PROVEEDOR_GEMINI_API_KEY", "gemini-key")
    monkeypatch.setenv("ORQ_PROVEEDOR_GEMINI_MODELO", "gemini-model")

    cfg = config_modelo("contenido")

    assert (cfg.proveedor, cfg.model_id, cfg.api_key) == (
        "openai_like", "nvidia/model", "nvidia-key"
    )
    assert cfg.base_url == "https://nvidia.example/v1"
    assert cfg.respaldo is not None
    assert (cfg.respaldo.proveedor, cfg.respaldo.model_id, cfg.respaldo.api_key) == (
        "gemini", "gemini-model", "gemini-key"
    )


def test_gemini_sin_clave_falla_con_error_de_configuracion(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("ORQ_API_KEY", raising=False)
    monkeypatch.setattr("app.orquestador.ejecutores.clave_google", lambda: None)
    cfg = config_modelo("gemini_test")
    cfg = cfg.__class__(
        proveedor="gemini", model_id="modelo", api_key=None, base_url=None,
        temperatura=0.4, max_tokens=100, timeout_segundos=1,
    )

    with pytest.raises(ConfiguracionProveedorError, match="GOOGLE_API_KEY"):
        EjecutorAgno(cfg)._crear_modelo()


def test_clasificacion_de_errores_transitorios():
    assert EjecutorAgno._reintentable(RuntimeError("429 rate limit"))
    assert EjecutorAgno._reintentable(TimeoutError("timeout"))
    assert not EjecutorAgno._reintentable(ValueError("clave inválida"))


def test_evaluacion_separa_opciones_y_mueve_respuestas_al_final():
    via = ViaEvaluacion(EjecutorMock())
    texto = (
        "## Actividad 1\n\n"
        "1. ¿Cuál es correcta? a) Primera b) Segunda c) Tercera d) Cuarta\n"
        "**Respuesta correcta: b**\n"
        "**Justificación:** Porque corresponde.\n"
    )

    resultado = via._postprocesar_archivo("evaluaciones.md", texto)

    assert "a) Primera  \nb) Segunda  \nc) Tercera  \nd) Cuarta" in resultado
    assert resultado.index("## Solucionario") > resultado.index("d) Cuarta")
    actividad, solucionario = resultado.split("## Solucionario", 1)
    assert "Respuesta correcta" not in actividad
    assert "Justificación" not in actividad
    assert "Respuesta correcta" in solucionario


def test_evaluacion_normaliza_formulas_y_salta_linea_las_opciones():
    via = ViaEvaluacion(EjecutorMock())
    resultado = via._postprocesar_archivo(
        "evaluaciones.md",
        "## Actividad 1\n\n"
        "1. ¿Cuál es la derivada? a) $f'(x)=\\frac{1}{2}\\sqrt{x}$ "
        "b) $f'(x)=x^2$\n",
    )

    assert "$" not in resultado
    assert "√(x)" in resultado
    assert "a) f'(x)=(1)/(2)√(x)  \n" in resultado
    assert "b) f'(x)=x^2\n" in resultado


def test_normalizar_formula_convierte_simbolos_basicos():
    assert normalizar_notacion_matematica(r"\lim_{h \to 0} \frac{x+h}{h}") == "lim_h → 0 (x+h)/(h)"


def test_verificacion_conserva_solo_urls_comprobadas(monkeypatch):
    via = ViaVerificacion(EjecutorMock())
    disponible = "https://docs.python.org/3/"
    no_disponible = "https://ejemplo.invalid/fuente"

    monkeypatch.setattr(
        ViaVerificacion,
        "_url_disponible",
        staticmethod(lambda url: url == disponible),
    )
    resultado = via._postprocesar_archivo(
        "verificacion.md",
        f"## Fuentes verificables\n- Python: {disponible}\n- Otra: {no_disponible}\n",
    )

    assert disponible in resultado
    assert no_disponible not in resultado.split("## Estado de las URLs", 1)[1]
    assert "Fuente no verificada y excluida" not in resultado


def test_verificacion_exige_dominio_academico_u_oficial(monkeypatch):
    via = ViaVerificacion(EjecutorMock())
    oficial = "https://ocw.mit.edu/courses/18-01-single-variable-calculus-fall-2006/"
    comercial = "https://ejemplo.com/curso"

    monkeypatch.setattr(ViaVerificacion, "_url_disponible", staticmethod(lambda url: True))
    resultado = via._postprocesar_archivo(
        "verificacion.md",
        f"## Fuentes verificables\n- Oficial: {oficial}\n- Comercial: {comercial}\n",
    )

    assert oficial in resultado
    assert comercial not in resultado


@pytest.mark.asyncio
async def test_planificador_no_disfraza_error_del_proveedor():
    class EjecutorFallido:
        es_simulado = False

        async def generar(self, *, rol, instrucciones, prompt):
            raise ValueError("429: rate limit")

    config = Configurador.model_validate(EJEMPLO)
    with pytest.raises(RuntimeError, match="proveedor.*429: rate limit"):
        await Planificador(EjecutorFallido()).completar(config)


def test_pdf_se_descarga_como_pdf_y_entra_al_zip(tmp_path):
    import io
    import zipfile

    with _cliente(tmp_path) as cliente:
        trabajo_id = cliente.post("/orquestador/cursos", json=EJEMPLO).json()["id"]
        for _ in range(1200):
            estado = cliente.get(f"/orquestador/cursos/{trabajo_id}").json()
            if estado["estado"] not in ("pendiente", "planificando", "ejecutando"):
                break
            time.sleep(0.05)

        pdfs = [a["nombre"] for a in estado["archivos"] if a["nombre"].endswith(".pdf")]
        assert pdfs, "no se registró ningún PDF (revisa que WeasyPrint esté instalado)"

        r = cliente.get(f"/orquestador/cursos/{trabajo_id}/archivos/{pdfs[0]}")
        assert r.status_code == 200
        assert r.headers["content-type"] == "application/pdf"
        assert r.content[:4] == b"%PDF"

        z = cliente.get(f"/orquestador/cursos/{trabajo_id}/descarga")
        assert z.status_code == 200
        with zipfile.ZipFile(io.BytesIO(z.content)) as zf:
            assert all(nombre.endswith(".pdf") for nombre in zf.namelist())
            assert zf.read(pdfs[0])[:4] == b"%PDF"