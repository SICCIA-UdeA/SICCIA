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

## Reglas generales (obligatorias para todos los agentes)
- Escribe en español, con un tono y una profundidad adecuados al público objetivo.
- Respeta la estructura: no cambies, agregues, elimines ni reordenes módulos o temas, y conserva su numeración.
- No inventes datos, citas, cifras ni URLs. Si no estás seguro de algo, omítelo.
- Entrega únicamente Markdown válido, sin HTML, para que luego pueda convertirse a PDF o diapositivas.
- Mantén coherencia con la metodología de aprendizaje indicada.
- Cuando informes tiempos, usa únicamente la distribución horaria común y conserva sus totales.
"""
