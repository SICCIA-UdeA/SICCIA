from __future__ import annotations
import re
from ..schemas import Configurador, CursoPlan
from .base import ViaBase

class ViaVerificacion(ViaBase):
    rol = "verificacion"
    archivos_esperados = ("verificacion.md",)
    instrucciones = (
        "Eres un verificador académico estricto (Fact-Checker). "
        "Tu trabajo es leer el contenido del curso y compararlo con el conocimiento científico y académico establecido."
    )

    def construir_subplantilla(self, config: Configurador, plan: CursoPlan) -> str:
        return """# Plantilla específica: Verificación de Veracidad

## Tu tarea
Acabas de recibir en la plantilla base el **contenido real** que generó el agente de contenido.
Debes leerlo críticamente y buscar alucinaciones, errores conceptuales o datos inventados.

## Estructura del documento `verificacion.md`
1. `# Reporte de Verificación Académica`
2. `## Resumen de Fiabilidad`: Un párrafo indicando si el texto es confiable o si requiere edición humana urgente.
3. `## Conceptos Revisados`: (Tabla con 3 columnas: Concepto / Estado (Correcto, Impreciso, Falso) / Corrección sugerida).
4. `## Sugerencias de Bibliografía Real`: Propón 3 libros o artículos reales (que sepas que existen) para respaldar el tema.
"""