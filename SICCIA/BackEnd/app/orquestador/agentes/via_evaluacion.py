"""Vía 1: actividades evaluativas del curso."""
from __future__ import annotations

from ..schemas import Configurador, CursoPlan
import re
import logging
import unicodedata

from .base import ViaBase, normalizar_notacion_matematica
from ..plantillas import instrucciones_matematicas, perfil_publico

log = logging.getLogger(__name__)


def clasificar_actividad(tipo: str) -> str:
    nombre = "".join(
        caracter for caracter in unicodedata.normalize("NFD", tipo.lower())
        if unicodedata.category(caracter) != "Mn"
    )
    pruebas = ("quiz", "examen", "parcial", "final", "prueba", "test", "cuestionario")
    return "prueba" if any(palabra in nombre for palabra in pruebas) else "practica"


class ViaEvaluacion(ViaBase):
    rol = "evaluacion"
    archivos_esperados = ("evaluaciones.md",)
    instrucciones = (
        "Eres un diseñador de evaluaciones educativas. Creas actividades evaluativas claras, "
        "alineadas con los temas del curso, con criterios de calificación y solucionarios correctos. "
        "Cada opción de selección múltiple debe ocupar una línea independiente. Nunca muestres la "
        "respuesta correcta ni la justificación junto al enunciado; ambas van únicamente al final, "
        "en la sección Solucionario. En preguntas matemáticas, no incluyas dos opciones equivalentes "
        "ni definiciones alternativas que también sean correctas: debe existir exactamente una respuesta."
    )

    def construir_subplantilla(self, config: Configurador, plan: CursoPlan) -> str:
        ev = config.evaluacion
        perfil = perfil_publico(plan.publico_objetivo)
        matematicas = bool(instrucciones_matematicas(plan.tema, perfil))

        if ev.actividades:
            total_cantidades = sum(a.cantidad for a in ev.actividades)
            if ev.total_actividades is not None and ev.total_actividades != total_cantidades:
                log.warning(
                    "total_actividades (%s) no coincide con la suma de cantidad (%s); se usará la suma.",
                    ev.total_actividades,
                    total_cantidades,
                )
            asignado = sum(a.porcentaje or 0 for a in ev.actividades)
            pendientes = [a for a in ev.actividades if a.porcentaje is None]
            porcentaje_pendiente = max(0.0, 100.0 - asignado) / len(pendientes) if pendientes else 0.0
            lineas = []
            filas_tabla = [
                "| Actividad | Categoría | Módulos que cubre | Cantidad | Porcentaje del grupo | Porcentaje por unidad |",
                "|---|---|---|---:|---:|---:|",
            ]
            for a in ev.actividades:
                porcentaje = a.porcentaje if a.porcentaje is not None else porcentaje_pendiente
                por_unidad = porcentaje / a.cantidad
                categoria = clasificar_actividad(a.tipo)
                lineas.append(
                    f"- **{a.tipo}** — categoría: **{categoria}**; cantidad: {a.cantidad}; "
                    f"{porcentaje:g}% para el grupo ({por_unidad:g}% por unidad)."
                )
                filas_tabla.append(
                    f"| {a.tipo} | {categoria} | Distribuir según los módulos | {a.cantidad} "
                    f"| {porcentaje:g}% | {por_unidad:g}% |"
                )
            filas_tabla.append("| **TOTAL** | | | | **100%** | |")
            tabla_resumen = "\n".join(filas_tabla)
            actividades = "\n".join(lineas)
            nota_pct = (
                "Los porcentajes no indicados se distribuyen por igual entre esos grupos; "
                "el total de la evaluación debe ser 100%."
                if pendientes else "Los porcentajes ya suman 100%."
            )
        else:
            actividades = (
                "El usuario no especificó actividades. Diséñalas tú: al menos un examen por cada "
                "grupo de módulos y un examen final, más las actividades prácticas que consideres útiles."
            )
            nota_pct = "Define tú los porcentajes de modo que sumen 100%."
            tabla_resumen = (
                "Diseña una tabla con las columnas actividad, categoría, módulos que cubre, cantidad, "
                "porcentaje del grupo y porcentaje por unidad. La suma final debe ser 100%."
            )

        total = (
            f"Total de actividades evaluativas: **{sum(a.cantidad for a in ev.actividades)}**."
            if ev.actividades else
            "El total de actividades no fue indicado: defínelo según la duración y el número de módulos."
        )
        tipos = (
            ", ".join(ev.tipos_pregunta) if ev.tipos_pregunta
            else "No indicados: usa una combinación variada de tipos de pregunta."
        )
        reglas_actividades = []
        for actividad in ev.actividades:
            tipo = actividad.tipo.lower()
            categoria = clasificar_actividad(actividad.tipo)
            reglas = (
                f"**{actividad.tipo} ({categoria}):** "
                "usa únicamente los tipos de pregunta indicados; Quiz: máximo "
                f"{perfil.max_preguntas_quiz} preguntas; Examen: máximo "
                f"{perfil.max_preguntas_examen}. Incluye opciones en líneas separadas y una sola respuesta correcta."
                if categoria == "prueba"
                else f"**{actividad.tipo} (práctica):** incluye objetivo, enunciado, entregables, criterios "
                "y rúbrica con puntajes."
            )
            if categoria == "practica" and "laboratorio" in tipo and perfil.nivel == "primaria" and matematicas:
                reglas += " Usa material concreto sencillo (fichas, monedas, regletas o papel), pasos numerados y registro de resultados."
            if categoria == "practica" and "investigacion" in tipo and perfil.nivel == "primaria":
                reglas += " Debe ser breve y guiada, con preguntas orientadoras y producto sencillo (cartel, tabla o dibujo); no pidas fuentes externas ni URLs."
            reglas_actividades.append(f"- {reglas}")
        actividades_por_categoria = "\n".join(reglas_actividades) or "- Clasifica cada actividad diseñada como prueba o práctica."

        return f"""# Plantilla específica: Evaluaciones

## Tu tarea
Diseña **todas las actividades evaluativas** del curso. No desarrolles el contenido de los temas:
otro agente lo hace. Tú solo evalúas lo que la estructura de la plantilla base cubre.

## Información del configurador
- **Tipos de pregunta para los exámenes:** {tipos}
- {total}
- **Actividades evaluativas:**
{actividades}
- **Reglas por actividad:**
{actividades_por_categoria}

{nota_pct}

## Cómo proceder
1. Si las indicaciones son vagas (por ejemplo, solo "exámenes"), completa lo que falte con criterio
   pedagógico y explica brevemente tus decisiones al inicio del documento.
2. Distribuye las actividades para cubrir todos los módulos y temas, indicando qué módulos evalúa cada una.
3. Usa la distribución horaria común para que la carga de las actividades sea razonable. Incluye
   una tabla breve con la dedicación estimada de cada actividad, sin superar el total del curso.
4. Las actividades de categoría prueba usan solo los tipos de pregunta indicados (si los hay). Cada pregunta debe tener
   el enunciado y cada opción (`a)`, `b)`, `c)`, `d)`) en una línea separada. No pongas respuestas
   ni justificaciones dentro de las actividades.
   Cada pregunta debe tener exactamente una opción inequívocamente correcta; revisa que los
   distractores no sean parcialmente correctos ni dependan de interpretaciones ambiguas.
   Adapta el ejercicio matemático a las reglas de nivel de la plantilla base. Limita la longitud del Quiz
   y del Examen a las cantidades indicadas en el perfil del público; el Quiz debe tener menos
   preguntas que el Examen.
5. Las actividades de categoría práctica (laboratorios, investigaciones, talleres, etc.) llevan: objetivo,
   enunciado, entregables, criterios de evaluación y rúbrica con puntajes.
6. Adapta dificultad y lenguaje al público objetivo y a la metodología de la plantilla base.
7. Evalúa las mismas evidencias que exige el perfil pedagógico común: no diseñes una evaluación
   puramente memorística si la metodología exige resolver problemas, construir un proyecto, analizar
   casos, colaborar o reflexionar sobre la experiencia.

## Tabla resumen obligatoria
Usa esta tabla como punto de partida y conserva sus porcentajes de grupo:
{tabla_resumen}

## Estructura del documento `evaluaciones.md`
1. `# Evaluaciones del curso`
2. `## Resumen del sistema de evaluación`: tabla con actividad, categoría, módulos que cubre, cantidad,
   porcentaje del grupo y porcentaje por unidad. El total debe sumar 100%.
3. Una sección `## Actividad N: <nombre>` por cada actividad, con su enunciado completo.
4. `## Solucionario`: respuestas y rúbricas, separado de los enunciados.
"""

    def _postprocesar_archivo(self, nombre: str, contenido: str) -> str:
        if nombre != "evaluaciones.md":
            return contenido

        partes = re.split(r"(?im)^##\s+Solucionario\s*$", contenido, maxsplit=1)
        enunciados = partes[0].rstrip()
        solucionario = partes[1].strip() if len(partes) == 2 else ""
        enunciados = normalizar_notacion_matematica(enunciados)
        solucionario = normalizar_notacion_matematica(solucionario)
        enunciados = re.sub(r"[ \t]+(?=[a-d]\))", "\n", enunciados)
        enunciados = re.sub(r"(?m)^([a-d]\).*)$", r"\1  ", enunciados)
        solucionario = re.sub(r"(?m)^([a-d]\).*)$", r"\1  ", solucionario)

        respuestas: list[str] = []

        def extraer_respuesta(match: re.Match[str]) -> str:
            respuestas.append(match.group(0).strip())
            return ""

        enunciados = re.sub(
            r"(?im)^[ \t]*\*{0,2}(?:Respuesta correcta|Justificación)\s*:.*$\n?",
            extraer_respuesta,
            enunciados,
        )
        if respuestas:
            solucionario = (solucionario + "\n\n" if solucionario else "") + "\n".join(respuestas)
        if not solucionario:
            solucionario = "Completar el solucionario con las respuestas y justificaciones."
        return f"{enunciados.rstrip()}\n\n## Solucionario\n\n{solucionario.strip()}\n"
