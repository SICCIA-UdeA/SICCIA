"""Vía 1: actividades evaluativas del curso."""
from __future__ import annotations

from ..schemas import Configurador, CursoPlan
from .base import ViaBase


class ViaEvaluacion(ViaBase):
    rol = "evaluacion"
    archivos_esperados = ("evaluaciones.md",)
    instrucciones = (
        "Eres un diseñador de evaluaciones educativas. Creas actividades evaluativas claras, "
        "alineadas con los temas del curso, con criterios de calificación y solucionarios correctos."
    )

    def construir_subplantilla(self, config: Configurador, plan: CursoPlan) -> str:
        ev = config.evaluacion

        if ev.actividades:
            lineas = []
            for a in ev.actividades:
                pct = f"{a.porcentaje:g}% de la nota final" if a.porcentaje is not None else "porcentaje por definir"
                lineas.append(f"- {a.cantidad} × **{a.tipo}** ({pct}, el total del grupo)")
            actividades = "\n".join(lineas)
            pendientes = [a for a in ev.actividades if a.porcentaje is None]
            nota_pct = (
                "Reparte el porcentaje restante entre las actividades sin porcentaje hasta sumar 100%."
                if pendientes else "Los porcentajes ya suman 100%."
            )
        else:
            actividades = (
                "El usuario no especificó actividades. Diséñalas tú: al menos un examen por cada "
                "grupo de módulos y un examen final, más las actividades prácticas que consideres útiles."
            )
            nota_pct = "Define tú los porcentajes de modo que sumen 100%."

        total = (
            f"Total de actividades evaluativas: **{ev.total_actividades}**."
            if ev.total_actividades else
            "El total de actividades no fue indicado: defínelo según la duración y el número de módulos."
        )
        tipos = (
            ", ".join(ev.tipos_pregunta) if ev.tipos_pregunta
            else "No indicados: usa una combinación variada de tipos de pregunta."
        )

        return f"""# Plantilla específica: Evaluaciones

## Tu tarea
Diseña **todas las actividades evaluativas** del curso. No desarrolles el contenido de los temas:
otro agente lo hace. Tú solo evalúas lo que la estructura de la plantilla base cubre.

## Información del configurador
- **Tipos de pregunta para los exámenes:** {tipos}
- {total}
- **Actividades evaluativas:**
{actividades}

{nota_pct}

## Cómo proceder
1. Si las indicaciones son vagas (por ejemplo, solo "exámenes"), completa lo que falte con criterio
   pedagógico y explica brevemente tus decisiones al inicio del documento.
2. Distribuye las actividades para cubrir todos los módulos y temas, indicando qué módulos evalúa cada una.
3. Los exámenes usan solo los tipos de pregunta indicados (si los hay). Incluye la respuesta correcta
   y una breve justificación de cada pregunta en el solucionario.
4. Las actividades que no son examen (laboratorios, investigaciones, talleres, etc.) llevan: objetivo,
   enunciado, entregables, criterios de evaluación y rúbrica con puntajes.
5. Adapta dificultad y lenguaje al público objetivo y a la metodología de la plantilla base.

## Estructura del documento `evaluaciones.md`
1. `# Evaluaciones del curso`
2. `## Resumen del sistema de evaluación`: tabla con actividad, módulos que cubre y porcentaje (suma 100%).
3. Una sección `## Actividad N: <nombre>` por cada actividad, con su enunciado completo.
4. `## Solucionario`: respuestas y rúbricas, separado de los enunciados.
"""
