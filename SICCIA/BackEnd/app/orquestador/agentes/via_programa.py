"""Vía 3: programa del curso y presentaciones. Solo consume la plantilla madre."""
from __future__ import annotations

from ..schemas import Configurador, CursoPlan
from .base import ViaBase


class ViaPrograma(ViaBase):
    rol = "programa"
    archivos_esperados = ("programa_curso.md", "presentaciones.md")
    instrucciones = (
        "Eres un coordinador académico y diseñador de presentaciones. Redactas programas de curso "
        "profesionales y presentaciones claras, sintéticas y visuales."
    )

    def construir_subplantilla(self, config: Configurador, plan: CursoPlan) -> str:
        n_temas = sum(len(m.temas) for m in plan.modulos)
        return f"""# Plantilla específica: Programa del curso y presentaciones

## Tu tarea
Produce dos entregables a partir de la plantilla base (solo con esa información; no desarrolles el contenido
de los temas ni diseñes evaluaciones, otros agentes lo hacen).

## Entregable 1: `programa_curso.md` (programa profesional del curso)
Incluye, en este orden:
1. `# Programa del curso: <tema>`
2. `## Ficha técnica`: tema, público objetivo, duración estimada, metodología.
3. `## Descripción del curso`
4. `## Objetivo general` y `## Objetivos específicos` (uno o más por módulo).
5. `## Conocimientos previos requeridos`: lista concreta de lo que el estudiante debe saber antes de empezar,
   acorde al público objetivo.
6. `## Metodología de aprendizaje`: cómo se aplica la metodología indicada a lo largo del curso.
7. `## Contenido programático`: cada módulo con sus temas (solo títulos) y una línea con el propósito del módulo.
8. `## Distribución sugerida del tiempo`: tabla por módulo, proporcional a la duración estimada.
9. `## Sistema de evaluación`: descríbelo en general, sin porcentajes ni cantidades (están en otro documento).

## Entregable 2: `presentaciones.md` (diapositivas)
Cada diapositiva es un bloque de Markdown y las diapositivas se separan con una línea que contenga solo `---`.
Cada una lleva un título (`##`) y entre 3 y 6 viñetas cortas. Cuando convenga, añade una línea
`> Notas del presentador: ...`. Las presentaciones, en este orden:
1. **Presentación de introducción al curso:** portada, objetivos, público y conocimientos previos,
   metodología, mapa de módulos y cierre/siguientes pasos.
2. **Una presentación por cada tema** de cada módulo ({n_temas} en total), cada una encabezada por
   `# Presentación N.M: <título del tema>` y con: portada, objetivos del tema, de 3 a 6 diapositivas con los
   conceptos clave, un ejemplo o caso, y una diapositiva final de resumen.

Usa exactamente los títulos y la numeración de la plantilla base.
"""
