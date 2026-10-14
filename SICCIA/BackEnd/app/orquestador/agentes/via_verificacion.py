from __future__ import annotations
from ..schemas import Configurador, CursoPlan
from .base import ViaBase

class ViaVerificacion(ViaBase):
    rol = "verificacion"
    archivos_esperados = ("verificacion.md",)
    
    # CAMBIO CLAVE 1: Restricciones negativas fuertes en el system prompt
    instrucciones = (
        "Eres un verificador académico estricto (Fact-Checker) y epistemólogo. "
        "Tu ÚNICO trabajo es validar la VERACIDAD de las afirmaciones históricas, científicas o teóricas. "
        "ESTÁ ESTRICTAMENTE PROHIBIDO hacer revisiones de código, evaluar sintaxis de programación, "
        "ortografía, gramática, estilo pedagógico o formato Markdown. Solo te importan los hechos."
    )

    def construir_subplantilla(self, config: Configurador, plan: CursoPlan) -> str:
        # CAMBIO CLAVE 2: Enfoque de la tabla hacia "Afirmaciones Factuales"
        return """# Plantilla específica: Verificación de Veracidad

## Tu tarea
Acabas de recibir en la plantilla base el **contenido real** que generó el agente de contenido.
Debes leerlo críticamente enfocándote EXCLUSIVAMENTE en buscar alucinaciones, errores de hechos, anacronismos, datos inventados o imprecisiones científicas.
Ignora por completo el estilo de redacción o el código fuente.

## Estructura ESTRICTA del documento `verificacion.md`
1. `# Reporte de Verificación Académica`
2. `## Resumen de Fiabilidad`: Un párrafo indicando si los hechos presentados son rigurosos y exactos, o si hay riesgo de desinformación (alucinación).
3. `## Afirmaciones Revisadas`: 
   (Crea una tabla con 3 columnas: "Afirmación Factual" / "Estado (Correcto, Impreciso, Falso)" / "Evidencia Científica o Corrección").
   *Nota: No evalúes bloques de código ni opiniones, solo hechos concretos.*
4. `## Sugerencias de Bibliografía Real`: 
   Propón 3 libros, papers o artículos académicos REALES (incluye autor y año comprobable) para respaldar el tema. NO inventes títulos. Si no tienes certeza de que el libro existe, no lo incluyas.
"""