"""Plantilla madre: contexto común que reciben TODOS los agentes."""
from __future__ import annotations

import re

from .schemas import CursoPlan


def _rango_horas(duracion: str, cantidad_temas: int) -> tuple[int, int]:
    rango = re.search(
        r"(\d+)\s*(?:-|a|hasta)\s*(\d+)\s*horas?", duracion, flags=re.IGNORECASE
    )
    if rango:
        numeros = [int(rango.group(1)), int(rango.group(2))]
    else:
        horas = re.search(r"(\d+)\s*horas?", duracion, flags=re.IGNORECASE)
        numeros = [int(horas.group(1))] if horas else []
    if not numeros:
        minimo = maximo = cantidad_temas
    elif len(numeros) == 1:
        minimo = maximo = numeros[0]
    else:
        minimo, maximo = sorted(numeros[:2])
    minimo = max(minimo, cantidad_temas)
    maximo = max(maximo, minimo)
    return minimo, maximo


def _repartir(total: int, cantidades: list[int]) -> list[int]:
    base, resto = divmod(total, len(cantidades))
    return [base + (i < resto) for i in range(len(cantidades))]


def distribucion_horaria(plan: CursoPlan) -> str:
    """Construye una distribución común y verificable para todos los agentes."""
    temas = [(modulo.titulo, tema) for modulo in plan.modulos for tema in modulo.temas]
    minimo, maximo = _rango_horas(plan.duracion_estimada, len(temas))
    minimas = _repartir(minimo, [1] * len(temas))
    maximas = _repartir(maximo, [1] * len(temas))
    filas = [
        "| Módulo | Tema | Horas mínimas | Horas máximas |",
        "|---|---|---:|---:|",
    ]
    indice = 0
    for modulo in plan.modulos:
        for tema in modulo.temas:
            filas.append(
                f"| {modulo.titulo} | {tema} | {minimas[indice]} | {maximas[indice]} |"
            )
            indice += 1
    filas.append(f"| **TOTAL** | | **{sum(minimas)}** | **{sum(maximas)}** |")
    return "\n".join(filas)


def perfil_metodologia(metodologia: str) -> str:
    """Convierte una etiqueta del configurador en reglas didácticas verificables."""
    nombre = metodologia.lower()
    perfiles: list[tuple[tuple[str, ...], str]] = [
        (
            ("problema", "problem"),
            "Aprendizaje basado en problemas: inicia cada módulo con un problema auténtico o simulado; "
            "guía la investigación, aplicación y justificación de una solución. El docente actúa como facilitador.",
        ),
        (
            ("proyecto",),
            "Aprendizaje basado en proyectos: define un producto final; cada módulo debe aportar un entregable "
            "del proyecto, con planificación, ejecución, revisión y presentación final.",
        ),
        (
            ("caso",),
            "Aprendizaje basado en casos: presenta una situación realista con información suficiente; pide "
            "analizar evidencias, comparar alternativas, tomar una decisión y justificarla.",
        ),
        (
            ("invertida", "flipped"),
            "Aula invertida: separa preparación previa (lectura, video o guía breve) de la sesión de aplicación; "
            "usa el tiempo de práctica para resolver dudas, ejercicios y retroalimentación.",
        ),
        (
            ("experiencial", "experiencia"),
            "Aprendizaje experiencial: estructura cada secuencia como experiencia concreta, reflexión guiada, "
            "conceptualización y nueva aplicación; incluye autoevaluación.",
        ),
        (
            ("cooperativo", "colaborativo"),
            "Aprendizaje cooperativo: organiza equipos pequeños con roles, responsabilidad individual, "
            "interdependencia positiva y una evidencia de aporte de cada estudiante.",
        ),
        (
            ("lúdico", "juego"),
            "Aprendizaje lúdico: usa retos, reglas y retroalimentación inmediata con propósito curricular; "
            "explicita qué aprendizaje demuestra cada dinámica.",
        ),
        (
            ("práctica", "hacer", "learning to do"),
            "Aprender haciendo: presenta una demostración breve, práctica guiada, práctica autónoma y un "
            "producto observable por tema.",
        ),
    ]
    for claves, perfil in perfiles:
        if any(clave in nombre for clave in claves):
            return perfil
    return (
        "Metodología personalizada: concreta la metodología en una secuencia de inicio, actividad activa, "
        "aplicación a un contexto y reflexión o retroalimentación. Explica cómo cada actividad demuestra el aprendizaje."
    )


def instrucciones_matematicas(tema: str) -> str:
    """Añade reglas de notación cuando el curso trata matemáticas."""
    nombre = tema.lower()
    claves = (
        "matem", "cálculo", "calculo", "álgebra", "algebra", "estadíst", "estadist",
        "integral", "derivada", "ecuación", "ecuacion", "geometr", "trigonom",
        "probabilidad", "fracción", "fraccion",
    )
    if not any(clave in nombre for clave in claves):
        return ""
    return """
## Notación matemática obligatoria
Este es un curso de matemáticas. Expresa los conceptos con fórmulas y símbolos visibles, no solo
con palabras. Usa Markdown compatible con PDF y Unicode matemático: ∫, ∑, √, ∞, Δ, ≤, ≥, ≠,
f′(x), d/dx, ∫ₐᵇ f(x) dx y expresiones como `f(x) = x² + 3x`. Incluye al menos una fórmula
relevante y un ejemplo resuelto en cada tema cuando corresponda. No uses delimitadores LaTeX,
MathJax ni `$`; la prohibición es sobre esos formatos, no sobre los símbolos matemáticos Unicode
ni las fórmulas escritas como texto o código.
"""


def formatear_estructura(plan: CursoPlan) -> str:
    bloques = []
    for i, modulo in enumerate(plan.modulos, start=1):
        temas = "\n".join(f"{i}.{j}. {t}" for j, t in enumerate(modulo.temas, start=1))
        bloques.append(f"### Módulo {i}: {modulo.titulo}\n{temas}")
    return "\n\n".join(bloques)


def construir_plantilla_madre(plan: CursoPlan) -> str:
    return f"""# Plantilla base del curso

> Documento de referencia común. Todos los agentes trabajan sobre esta misma estructura.

## Datos generales
- **Tema del curso:** {plan.tema}
- **Público objetivo / nivel:** {plan.publico_objetivo}
- **Duración estimada:** {plan.duracion_estimada}
- **Metodología de aprendizaje:** {plan.metodologia}

## Estructura del curso
Solo títulos: el contenido de cada tema lo desarrolla el agente que corresponda.

{formatear_estructura(plan)}

## Distribución horaria común y obligatoria
La siguiente tabla es la única distribución válida para todos los documentos. Las horas son
horas de aprendizaje del estudiante e incluyen explicación, práctica y trabajo autónomo del
tema. No sumes la duración general otra vez por cada tema ni inventes otra distribución.

{distribucion_horaria(plan)}

## Perfil pedagógico obligatorio
{perfil_metodologia(plan.metodologia)}
Cada módulo y cada evaluación debe mostrar evidencias de este perfil. No basta con mencionar el
nombre de la metodología: aplícala en las actividades, productos y criterios de evaluación.

{instrucciones_matematicas(plan.tema)}

## Reglas generales (obligatorias para todos los agentes)
- Escribe en español, con un tono y una profundidad adecuados al público objetivo.
- Respeta la estructura: no cambies, agregues, elimines ni reordenes módulos o temas, y conserva su numeración.
- No inventes datos, citas, cifras ni URLs. Si no estás seguro de algo, omítelo.
- Entrega únicamente Markdown válido, sin HTML, para que luego pueda convertirse a PDF o diapositivas.
- Mantén coherencia con la metodología de aprendizaje indicada.
- No sustituyas la metodología por una clase expositiva genérica: conserva sus fases, roles y evidencias.
- Cuando informes tiempos, usa únicamente la distribución horaria común y conserva sus totales.
"""
