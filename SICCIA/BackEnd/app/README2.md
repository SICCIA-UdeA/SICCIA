# Paquete `orquestador`

Genera un curso educativo en paralelo a partir del JSON "configurador" del frontend.

## Flujo
1. `POST /orquestador/cursos` valida el JSON y devuelve un `id` (202). El trabajo corre en segundo plano.
2. **Planificador**: completa lo que el usuario dejó en automático (público, duración, metodología, módulos, temas).
3. Se genera la **plantilla madre** (`interno/plantilla_madre.md`), común a todos los agentes.
4. Tres vías en paralelo (`orquestador/agentes/`), cada una con su subplantilla:
   - `ViaEvaluacion` → `evaluaciones.md`
   - `ViaContenido` → `contenido_curso.md`
   - `ViaPrograma` → `programa_curso.md` y `presentaciones.md`
5. El front consulta `GET /orquestador/cursos/{id}` y descarga con `/descarga` (zip) o `/archivos/{nombre}`.

Una vía que falla no cancela a las otras (estado `completado_con_errores`).

## Probarlo (sin modelos)
    pip install -r ../requirements.txt
    pip install -r requirements.txt
    pytest
    cd ..
    python run.py                 # http://127.0.0.1:8080/docs

## Conectar Gemini
    export ORQ_PROVEEDOR=gemini
    export ORQ_API_KEY=...            # o GOOGLE_API_KEY
    export ORQ_MODEL_ID=gemini-2.5-flash
Se puede cambiar por rol: `ORQ_PROVEEDOR_EVALUACION`, `ORQ_MODEL_ID_CONTENIDO`, etc.
Con el SDK de OpenAI: `ORQ_PROVEEDOR=openai_like` + `ORQ_BASE_URL`.

## Integrar en el backend
El controlador vive en `BackEnd/controller/orquestador_controller.py`; incluir
`OrquestadorController(dependencies=[Depends(...)]).router` y pasar la dependencia de autenticación.

## Pendiente
- Elegir y escribir el agente de cada vía (hoy cada vía llama a un `EjecutorLLM`).
- Conversión md → PDF/PPTX y agente de estética.
- Persistir trabajos (hoy el estado está en memoria).
