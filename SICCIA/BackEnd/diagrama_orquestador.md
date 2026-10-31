# Diagrama del orquestador de SICCIA

## Piezas

- **Orquestador** (`app/orquestador/orquestador.py`): decide el orden de las vías y el estado del trabajo. Usa asyncio.
- **Vía** (`app/orquestador/agentes/via_*.py`): arma el prompt de su tarea y separa la respuesta en archivos.
- **Ejecutor** (`EjecutorAgno`, en `ejecutores.py`): llama al modelo, valida la respuesta, reintenta y registra tokens.
- **Agno**: librería que ejecuta cada llamada (`Agent` + `arun`). No coordina nada: solo habla con el modelo.

## 1. Flujo del trabajo (orquestador)

```mermaid
flowchart TD
    A[Front o JSON del configurador] -->|POST /orquestador/cursos| B{Validación Pydantic}
    B -->|inválido| X1[422: no se crea el trabajo]
    B -->|válido| C[Trabajo creado<br/>responde 202 con id]
    C -->|en segundo plano| D[PLANIFICANDO<br/>rol: planificador]
    D -->|falla| ERR[ERROR]
    D --> E[Plan completo<br/>módulos y temas automáticos]
    E --> F[Plantilla madre<br/>común a todas las vías]
    F --> G[EJECUTANDO]
    G --> H1[Fase 1 en paralelo]
    H1 --> P[Vía programa<br/>programa_curso.md<br/>presentaciones.md]
    H1 --> K[Vía contenido<br/>contenido_curso.md]
    P --> Q{¿Existe contenido_curso.md?}
    K --> Q
    Q -->|no| OM[Fase 2 omitida<br/>vías en estado omitida]
    Q -->|sí| R[Plantilla madre<br/>más contenido real]
    R --> H2[Fase 2 en paralelo]
    H2 --> V1[Vía evaluación<br/>evaluaciones.md]
    H2 --> V2[Vía verificación<br/>verificacion.md]
    V1 --> Z{¿Cuántas vías terminaron bien?}
    V2 --> Z
    OM --> Z
    Z -->|todas| FIN[COMPLETADO]
    Z -->|algunas| CE[COMPLETADO_CON_ERRORES]
    Z -->|ninguna| ERR
    FIN --> PDF[Convertir .md a PDF<br/>si al menos una vía terminó]
    CE --> PDF
    PDF --> DL[Descarga: estado, archivo o ZIP]
```

## 2. Dentro de una vía (Agno)

```mermaid
flowchart TD
    V1[La vía recibe la plantilla madre<br/>y su subplantilla] --> V2[Arma el prompt]
    V2 --> V3[Ejecutor.generar]
    V3 --> V4[Agno: Agent con el modelo del proveedor]
    V4 --> V5[arun: llamada al modelo]
    V5 --> V6{¿Respuesta válida?<br/>no vacía, sin JSON de error}
    V6 -->|no| V7[Espera 2 s, 4 s...<br/>y reintenta]
    V7 -->|a partir del penúltimo fallo| V8[Respaldo: Gemini<br/>si está configurado]
    V8 --> V5
    V7 -->|más intentos| V5
    V6 -->|sí| V9[Registro de tokens y tiempo<br/>registro_pruebas_siccia.csv]
    V9 --> V10[Separa la respuesta en archivos<br/>por marcadores]
    V10 --> V11[Guarda los archivos en resultados]
```

## 3. Clase de Agno según el proveedor

| Proveedor (`ORQ_PROVEEDOR_*`) | Clase de Agno | Uso típico |
|---|---|---|
| `gemini` | `agno.models.google.Gemini` | Google AI Studio |
| `openai_like` | `agno.models.openai.like.OpenAILike` | Cualquier API compatible con OpenAI: OpenRouter, Groq, NVIDIA |
| `openai` | `agno.models.openai.OpenAIChat` | OpenAI |
| Respaldo (automático) | Proveedor configurado en `ORQ_PROVEEDOR_RESPALDO_<ROL>` | Tras reintentos de errores transitorios del proveedor principal |

Cada proveedor se registra una sola vez con `ORQ_PROVEEDOR_<NOMBRE>_TIPO`, `_MODELO`,
`_API_KEY` y `_BASE_URL`. Las vías se asocian mediante `ORQ_VIA_<ROL>` y el respaldo mediante
`ORQ_RESPALDO_<ROL>`. Para Gemini se acepta la clave del registro o `GOOGLE_API_KEY`; para
`openai_like` se necesita clave y URL.
Los errores de configuración no se reintentan y se comunican explícitamente.

## 4. Roles

| Rol | Qué genera | Proveedor configurable |
|---|---|---|
| planificador | Módulos y temas automáticos | `ORQ_PROVEEDOR_PLANIFICADOR` o `ORQ_PROVEEDOR` |
| programa | `programa_curso.md`, `presentaciones.md` | `ORQ_PROVEEDOR_PROGRAMA` o `ORQ_PROVEEDOR` |
| contenido | `contenido_curso.md` | `ORQ_PROVEEDOR_CONTENIDO` o `ORQ_PROVEEDOR` |
| evaluación | `evaluaciones.md` | `ORQ_PROVEEDOR_EVALUACION` o `ORQ_PROVEEDOR` |
| verificación | `verificacion.md` | `ORQ_PROVEEDOR_VERIFICACION` o `ORQ_PROVEEDOR` |

## 5. Estados de una vía

`pendiente` → `en_curso` → `completada`, `omitida` o `error`.

## 6. Calidad y fuentes

- La verificación consulta el contenido real generado y conserva únicamente URLs que responden
  y pertenecen a dominios académicos u oficiales permitidos.
- El solucionario queda al final de `evaluaciones.md`.
- Las presentaciones salen de la vía programa.
- El frontend consulta el backend mediante `/api`.