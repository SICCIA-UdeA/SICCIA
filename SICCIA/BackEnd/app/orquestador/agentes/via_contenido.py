"""Vía 2: desarrollo del contenido del curso."""
from __future__ import annotations

from ..schemas import Configurador, CursoPlan
from .base import ViaBase


def _si(valor: bool) -> str:
    return "Sí" if valor else "No"


class ViaContenido(ViaBase):
    rol = "contenido"
    archivos_esperados = ("contenido_curso.md",)
    instrucciones = (
        "Eres un autor de material educativo. Explicas con claridad y rigor, con ejemplos útiles, "
        "y nunca inventas datos, citas ni enlaces."
    )

    def construir_subplantilla(self, config: Configurador, plan: CursoPlan) -> str:
        c = config.contenido
        extras: list[str] = []

        if c.incluir_ejemplos_practicos:
            extras.append("**Ejemplo práctico** en CADA tema de cada módulo, concreto y realista para el público objetivo.")
        if c.incluir_talleres_practica:
            extras.append(
                "**Taller de práctica** al final de CADA módulo: actividades de práctica de los conocimientos "
                "del módulo, sin calificación. Incluye indicaciones y, al final, respuestas orientativas."
            )
        if c.incluir_cierre_por_modulo:
            extras.append("**Cierre del módulo**: bloque breve de conclusiones y puntos clave al terminar cada módulo.")

        if c.incluir_enlaces:
            enlaces = (
                "Sugiere recursos externos (sitios, videos o materiales de terceros) que ayuden a comprender cada "
                "tema. Solo recursos muy conocidos y estables; usa la página principal del sitio o canal, nunca "
                "enlaces profundos que no puedas garantizar, y marca cada uno con *(verificar enlace)*."
            )
        else:
            enlaces = "No incluyas enlaces ni recursos externos."

        referencias = (
            f"Si citas fuentes, usa el formato **{c.formato_referencias}** y cita únicamente obras que existan con certeza."
            if c.formato_referencias else
            "No incluyas sección de referencias ni citas bibliográficas."
        )
        imagenes = (
            "Donde una imagen aporte, deja un marcador `![descripción](unsplash:palabras clave en inglés)`; "
            "no uses otras URLs ni imágenes."
            if config.estilo.incluir_imagenes else
            "No incluyas imágenes."
        )
        lista_extras = "\n".join(f"- {e}" for e in extras) or "- (ninguno)"

        return f"""# Plantilla específica: Contenido del curso

## Tu tarea
Desarrolla el **contenido completo del curso**, módulo por módulo y tema por tema, siguiendo la estructura
de la plantilla base. Las evaluaciones, el programa del curso y las presentaciones los hacen otros agentes:
no los incluyas.

## Información del configurador
- Ejemplos prácticos por tema: {_si(c.incluir_ejemplos_practicos)}
- Talleres de práctica sin calificación por módulo: {_si(c.incluir_talleres_practica)}
- Cierre/resumen por módulo: {_si(c.incluir_cierre_por_modulo)}
- Enlaces y materiales de terceros: {_si(c.incluir_enlaces)}
- Formato de referencias: {c.formato_referencias or "No requerido"}

## Elementos obligatorios
{lista_extras}

## Enlaces, referencias e imágenes
- {enlaces}
- {referencias}
- {imagenes}

## Estructura del documento `contenido_curso.md`
- `# {plan.tema}` como título único.
- `## Módulo N: <título>` con una breve introducción del módulo.
- `### N.M <título del tema>` por cada tema, con: objetivos de aprendizaje, explicación desarrollada
  (conceptos, definiciones, procedimientos) y puntos clave. Añade el ejemplo práctico si está activado.
- Al final de cada módulo, en este orden: el taller de práctica y el cierre del módulo, si están activados.
- Usa listas y tablas simples; evita HTML.
"""
