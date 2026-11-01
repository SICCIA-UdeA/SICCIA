"""Plantilla madre: contexto común que reciben TODOS los agentes."""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from .schemas import CursoPlan


def _normalizar(texto: str) -> str:
    return "".join(
        caracter for caracter in unicodedata.normalize("NFD", texto.lower())
        if unicodedata.category(caracter) != "Mn"
    )


@dataclass(frozen=True)
class PerfilPublico:
    nivel: str
    grados: tuple[int, int] | None
    edad_aproximada: str
    texto_original: str
    reglas: str
    max_preguntas_quiz: int
    max_preguntas_examen: int
    duracion_actividad: str


_REGLAS_NIVEL = {
    "inicial/preescolar": (
        "Usa frases muy breves, vocabulario concreto, juego guiado, objetos e imágenes descritas "
        "con palabras; evita abstracciones y evalúa mediante observación."
    ),
    "primaria": (
        "Usa frases de máximo 15 palabras y párrafos de 2 a 4 frases. Emplea vocabulario cotidiano "
        "y define cada término nuevo con palabras simples. Usa ejemplos de colegio, tienda, frutas, "
        "juegos y deporte. Da instrucciones numeradas paso a paso y actividades de 10 a 20 minutos. "
        "Mantén un tono cercano y motivador. Escribe enunciados cortos, una sola idea por pregunta, "
        "opciones breves (máximo 4) y sin dobles negaciones."
    ),
    "secundaria": (
        "Explica los conceptos con ejemplos familiares y presenta la terminología técnica de forma "
        "gradual. Organiza actividades guiadas y autónomas con pasos explícitos; las evaluaciones "
        "deben pedir aplicación y explicación, no solo memoria."
    ),
    "media/bachillerato": (
        "Introduce la terminología técnica gradualmente y conecta los conceptos con problemas "
        "aplicados. Pide justificar procedimientos y comparar estrategias con dificultad progresiva."
    ),
    "técnico/tecnólogo": (
        "Prioriza procedimientos, herramientas y situaciones ocupacionales auténticas. Define los "
        "criterios de desempeño y exige productos o evidencias verificables."
    ),
    "universitario/pregrado/posgrado": (
        "Mantén rigor conceptual, terminología disciplinar y fuentes o supuestos explícitos. "
        "Exige argumentación, análisis y aplicación con profundidad acorde al nivel."
    ),
    "adultos/profesionales": (
        "Relaciona el aprendizaje con tareas y decisiones profesionales reales. Respeta la experiencia "
        "previa, usa casos relevantes y define evidencias de aplicación."
    ),
    "general": (
        "Usa lenguaje claro, define términos especializados y adapta ejemplos y dificultad a la "
        "información disponible, sin asumir edad ni conocimientos previos."
    ),
}


def perfil_publico(publico_objetivo: str) -> PerfilPublico:
    """Interpreta niveles y grados comunes sin fallar ante etiquetas no reconocidas."""
    original = publico_objetivo or ""
    texto = _normalizar(original)
    if any(palabra in texto for palabra in ("preescolar", "inicial", "primera infancia")):
        nivel = "inicial/preescolar"
        edades = "3 a 6 años, aproximadamente"
    elif any(palabra in texto for palabra in ("tecnico", "tecnologo", "tecnologica")):
        nivel = "técnico/tecnólogo"
        edades = "adolescentes o adultos; depende del programa"
    elif any(palabra in texto for palabra in ("universitario", "pregrado", "posgrado", "universidad")):
        nivel = "universitario/pregrado/posgrado"
        edades = "desde los 17 años, aproximadamente"
    elif any(palabra in texto for palabra in ("adulto", "profesional", "formador", "tutor")):
        nivel = "adultos/profesionales"
        edades = "adultos"
    elif any(palabra in texto for palabra in ("media", "bachillerato")):
        nivel = "media/bachillerato"
        edades = "15 a 17 años, aproximadamente"
    elif "secundaria" in texto:
        nivel = "secundaria"
        edades = "11 a 15 años, aproximadamente"
    elif any(palabra in texto for palabra in ("primaria", "basica primaria")):
        nivel = "primaria"
        edades = "6 a 11 años, aproximadamente"
    else:
        nivel = "general"
        edades = "no especificada"

    grados: tuple[int, int] | None = None
    if nivel in {"primaria", "secundaria", "media/bachillerato"}:
        expresion = (
            r"(?<!\d)(\d{1,2})\s*(?:\.?\s*(?:º|°|o|ro))?"
            r"\s*(?:a|hasta|-|–|—|/|,|y)\s*"
            r"(\d{1,2})\s*(?:\.?\s*(?:º|°|o|ro))?(?!\d)"
        )
        coincidencia = re.search(expresion, texto)
        if coincidencia:
            primero, segundo = sorted((int(coincidencia.group(1)), int(coincidencia.group(2))))
            grados = (primero, segundo)
            edades = {
                "primaria": f"{max(5, primero + 5)} a {max(5, segundo + 6)} años, aproximadamente",
                "secundaria": f"{max(10, primero + 5)} a {max(10, segundo + 5)} años, aproximadamente",
                "media/bachillerato": f"{max(14, primero + 5)} a {max(14, segundo + 5)} años, aproximadamente",
            }[nivel]

    preguntas = 8 if nivel in {"primaria", "inicial/preescolar"} else 15
    examen = 12 if nivel in {"primaria", "inicial/preescolar"} else 25
    return PerfilPublico(
        nivel=nivel,
        grados=grados,
        edad_aproximada=edades,
        texto_original=original,
        reglas=_REGLAS_NIVEL[nivel],
        max_preguntas_quiz=preguntas,
        max_preguntas_examen=examen,
        duracion_actividad="10 a 20 minutos" if nivel == "primaria" else "acorde al nivel y la tarea",
    )


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
    nombre = _normalizar(metodologia)
    perfiles: list[tuple[tuple[str, ...], str]] = [
        (
            ("resolucion de problemas", "resolver problemas"),
            "Resolución de problemas con las cuatro fases de Pólya en cada tema: "
            "**Comprender** (identificar datos y pregunta), **Planear** (elegir una estrategia: "
            "dibujo, tabla u operación), **Resolver** (ejecutar la estrategia) y **Revisar** "
            "(comprobar y explicar el resultado). Incluye un problema contextualizado resuelto "
            "por fases en cada tema, con dificultad progresiva de fácil a reto. Las evaluaciones "
            "valoran comprensión, estrategia, resultado y comprobación, no solo el cálculo.",
        ),
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
        if any(_normalizar(clave) in nombre for clave in claves):
            return perfil
    return (
        "Metodología personalizada: concreta la metodología en una secuencia de inicio, actividad activa, "
        "aplicación a un contexto y reflexión o retroalimentación. Explica cómo cada actividad demuestra el aprendizaje."
    )


def instrucciones_matematicas(tema: str, publico: str | PerfilPublico = "") -> str:
    """Añade reglas matemáticas ajustadas al nivel educativo."""
    nombre = _normalizar(tema)
    claves = (
        "matem", "cálculo", "calculo", "álgebra", "algebra", "estadíst", "estadist",
        "integral", "derivada", "ecuación", "ecuacion", "geometr", "trigonom",
        "probabilidad", "fracción", "fraccion",
    )
    if not any(_normalizar(clave) in nombre for clave in claves):
        return ""
    perfil = publico if isinstance(publico, PerfilPublico) else perfil_publico(publico)
    if perfil.nivel in {"inicial/preescolar", "primaria"}:
        grados = (
            f" El curso cubre los grados {perfil.grados[0]} a {perfil.grados[1]}."
            if perfil.grados else ""
        )
        return f"""
## Reglas matemáticas para nivel inicial
Este curso es de matemáticas para **{perfil.nivel}**.{grados}
Usa solo operaciones y símbolos simples: +, −, ×, ÷ y =. Limita la notación a esas operaciones
y evita símbolos o contenidos avanzados que no corresponden a estos grados. Presenta las
operaciones verticales en bloques de código.
Trabaja valor posicional, rectas numéricas, dibujos y tablas descritos en texto, material
concreto, cálculo mental y problemas verbales contextualizados. Comprueba el resultado de
cada ejemplo. Ajusta la cantidad de cifras y pasos al grado máximo indicado, aumenta la dificultad
gradualmente y evita exigir contenidos posteriores. Trabaja solo la operación del módulo: no
agregues fracciones ni contenidos de otros módulos que el usuario no haya solicitado.
"""
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
    publico = perfil_publico(plan.publico_objetivo)
    grados = (
        f"{publico.grados[0]} a {publico.grados[1]}"
        if publico.grados else "No especificados"
    )
    return f"""# Plantilla base del curso

> Documento de referencia común. Todos los agentes trabajan sobre esta misma estructura.

## Datos generales
- **Tema del curso:** {plan.tema}
- **Público objetivo / nivel:** {plan.publico_objetivo}
- **Duración estimada:** {plan.duracion_estimada}
- **Metodología de aprendizaje:** {plan.metodologia}

## Perfil del público (obligatorio)
- **Nivel reconocido:** {publico.nivel}
- **Público original:** {publico.texto_original or "No especificado"}
- **Grados:** {grados}
- **Edad aproximada:** {publico.edad_aproximada}
- **Reglas concretas:** {publico.reglas}
- **Preguntas orientativas:** Quiz, máximo {publico.max_preguntas_quiz}; Examen, máximo {publico.max_preguntas_examen}.
- **Duración de actividad orientativa:** {publico.duracion_actividad}.

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

{instrucciones_matematicas(plan.tema, publico)}

## Reglas generales (obligatorias para todos los agentes)
- Escribe en español, con un tono y una profundidad adecuados al público objetivo.
- Respeta la estructura: no cambies, agregues, elimines ni reordenes módulos o temas, y conserva su numeración.
- No inventes datos, citas, cifras ni URLs. Si no estás seguro de algo, omítelo.
- Entrega únicamente Markdown válido, sin HTML, para que luego pueda convertirse a PDF o diapositivas.
- Mantén coherencia con la metodología de aprendizaje indicada.
- No sustituyas la metodología por una clase expositiva genérica: conserva sus fases, roles y evidencias.
- Cuando informes tiempos, usa únicamente la distribución horaria común y conserva sus totales.
"""
