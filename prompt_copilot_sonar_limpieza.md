# Prompt para GitHub Copilot (modo Agente) — Aviso CSRF, limpieza segura y correcciones de SonarQube Cloud

**Cómo usarlo:** abre VS Code en la raíz del repositorio (la carpeta que contiene `SICCIA/`), abre el chat de Copilot en modo **Agent** y pega todo lo que está debajo de `=== INICIO DEL PROMPT ===`.

**Contenido:** (A) aviso de CSRF, (B) archivos seguros de borrar y (C) tres correcciones de los avisos de SonarQube Cloud que **no cambian el comportamiento** (expresiones regulares, PDF en un hilo aparte e imports sin usar). Si no quieres la parte C, bórrala antes de pegar.

=== INICIO DEL PROMPT ===

# Objetivo

Trabaja en `SICCIA/BackEnd` (el frontend **no se toca**) y haz, **en este orden**, las fases 0 a 6. Los cambios deben dejar el comportamiento de la aplicación **idéntico** al actual; solo mejoran robustez y documentan seguridad. Todo se verifica con la suite de pruebas existente.

# Reglas obligatorias

1. **No abras, leas ni modifiques ningún `.env`** (ni `SICCIA/env .txt` si existiera).
2. **No borres ni modifiques nada de `SICCIA/FrontEnd/`.** Tampoco borres `requirements.txt`, `.docx`, `README*.md`, `diagrama_orquestador.md`, `app/orquestador/app.py`, `app/orquestador/__main__.py`, ningún `__init__.py` (salvo el indicado en la Fase 1) ni `.vscode/`.
3. **No apliques cambios opcionales de estabilidad.** Prohibido en esta tarea: límites de longitud en `schemas.py`, retención o limpieza de trabajos, tope de trabajos simultáneos, candado en el CSV de telemetría, cambios en `SESSION_EPOCH`, cambios en los mensajes de error de los trabajos, y cambios en `.gitignore`.
4. **No añadas dependencias** (en particular, **no instales Flask-WTF** ni actives `CSRFProtect`).
5. **Cambios mínimos y localizados.** Conserva los **finales de línea (CRLF)** y el estilo de cada archivo que edites; no reformatees archivos completos.
6. No hagas commits. Si algo de este prompt no coincide con el código real, **detente en ese punto y repórtalo**.
7. Las pruebas nuevas siguen las convenciones del proyecto: pytest, patrón **AAA** con comentarios `# Arrange`, `# Act`, `# Assert`, nombres `test_<unidad>_<escenario>_<resultado>` en español, sin red, sin `sleep` para esperar, y mínimo **dos pruebas por cambio** (una de camino feliz y una de error o caso límite).

---

# FASE 0 — Línea base

Desde `SICCIA/BackEnd` ejecuta `python -m pytest` y anota: pruebas aprobadas, fallidas, omitidas, y cobertura total de líneas y ramas. Debe estar todo en verde. Si no lo está, detente y repórtalo.

---

# FASE 1 — Eliminar archivos y código sin uso (solo backend)

Antes de borrar cada elemento, **verifica con una búsqueda** (excluyendo `venv/`, `.venv/`, `node_modules/` y `__pycache__/`) que realmente no se usa; si encuentras un uso, no lo borres y repórtalo.

1. **`SICCIA/BackEnd/app/routes/__init__.py`** (archivo vacío) y la carpeta `app/routes/` si queda vacía (ignora `__pycache__`). Verifica que nada importe `app.routes`, `routes` ni `from .routes`.
2. **`SICCIA/BackEnd/package-lock.json`**. Verifica que contiene solo `"packages": {}` y que no hay `package.json` en `BackEnd/`.
3. **La constante `ROLES`** en `SICCIA/BackEnd/app/orquestador/config.py` (línea `ROLES = ("planificador", "evaluacion", ...)`). Verifica con búsqueda por palabra completa que no se usa en `app/`, `controller/`, `tests/` ni `run.py`. Quita solo esa línea (y un comentario inmediato si es exclusivo de ella). No toques `_ENV_FILE` ni nada más.

Ejecuta `python -m pytest`: mismo resultado que en la Fase 0.

---

# FASE 2 — Expresiones regulares con rendimiento cuadrático (regla python:S8786)

Sonar marca expresiones que, con entradas largas y adversas, tardan tiempo cuadrático. Ya fueron probadas contra las originales con 60.000 entradas aleatorias cada una: **0 diferencias** en `_limpiar`, `_RE_SEPARADOR`, `_RE_NUMERADO` y grados; en horas, la única diferencia es que números de 7 o más cifras dejan de reconocerse. Aplica **exactamente** estos cambios:

### 2.1 `SICCIA/BackEnd/app/orquestador/agentes/base.py`
Reemplaza la definición de `_CERCA`:
```python
_CERCA = re.compile(r"```(?:markdown|md)?[^\S\n]*\n(.*)\n```", re.DOTALL)
```
y en `ViaBase._limpiar` cambia `_CERCA.match(texto)` por **`_CERCA.fullmatch(texto)`** (el texto ya llega con `.strip()`, así que los `\s*` de los extremos sobraban). El resto de `_limpiar` no cambia.

### 2.2 `SICCIA/BackEnd/app/orquestador/exportador_pdf.py`
- Reemplaza `_RE_SEPARADOR` por:
```python
_RE_SEPARADOR = re.compile(r"(?<!\s)\s+-\s+(?=\S)")
```
- **Elimina** `_RE_NUMERADO` y añade esta función (sin regex, tiempo lineal), junto a las demás funciones auxiliares:
```python
def _parsear_numerado(linea: str) -> tuple[str, str] | None:
    """Devuelve (prefijo, cuerpo) si la línea es '  12.  texto'; si no, None. Tiempo lineal."""
    i, n = 0, len(linea)
    while i < n and linea[i].isspace():
        i += 1
    j = i
    while j < n and linea[j].isdecimal():
        j += 1
    if j == i or j >= n or linea[j] != ".":
        return None
    k = j + 1
    while k < n and linea[k].isspace():
        k += 1
    if k == j + 1:
        return None
    return linea[:k], linea[k:]
```
- En `separar_listas_pegadas`, sustituye el uso de `_RE_NUMERADO` por:
```python
            m = _parsear_numerado(linea)
            if m:
                tipo, prefijo, cuerpo = "numerado", m[0], m[1]
```
(el `else` posterior queda igual). Verifica que `_RE_NUMERADO` ya no aparece en `app/` ni en `tests/`; si una prueba lo importa, actualízala para usar `_parsear_numerado`.

### 2.3 `SICCIA/BackEnd/app/orquestador/plantillas.py`
En `_rango_horas`, reemplaza las dos expresiones (conserva `flags=re.IGNORECASE`):
```python
rango = re.search(
    r"(?<!\d)(\d{1,6})\s{0,5}(?:-|a|hasta)\s{0,5}(\d{1,6})\s{0,5}horas?", duracion, flags=re.IGNORECASE
)
...
horas = re.search(r"(?<!\d)(\d{1,6})\s{0,5}horas?", duracion, flags=re.IGNORECASE)
```
En `perfil_publico`, reemplaza el texto de `expresion` (los `\s*` consecutivos eran la causa del costo cuadrático) por:
```python
        expresion = (
            r"(?<!\d)(\d{1,2})(?:\s*(?:\.\s*)?(?:º|°|o|ro))?"
            r"\s*(?:a|hasta|-|–|—|/|,|y)\s*"
            r"(\d{1,2})(?:\s*(?:\.\s*)?(?:º|°|o|ro))?(?!\d)"
        )
```
El resto de la función no cambia.

### 2.4 Pruebas de la Fase 2
Añade (en los archivos de prueba correspondientes: `tests/secuence/test_respuestas_vias.py`, `tests/secuence/test_exportador_pdf.py`, `tests/orquestador/test_plantillas.py`):
- **`_limpiar`:** `"```markdown\nhola\n```"` → `"hola\n"`; `"```md\n\n  hola\n```"` → `"hola\n"`; texto sin cerca → mismo texto con `"\n"` final; `"```python\ncodigo\n```"` no se desenvuelve (conserva las cercas).
- **`_parsear_numerado`:** `"1. Texto"` → `("1. ", "Texto")`; `"  12.   x"` → `("  12.   ", "x")`; `"1. "` → `("1. ", "")`; `"1."`, `"a. x"` y `"1.x"` → `None`.
- **`_RE_SEPARADOR` vía `_partir`:** `"Pregunta - A) uno - B) dos"` se parte en 3; una línea con un solo ` - ` devuelve `None`.
- **`_rango_horas`:** conserva los casos existentes y añade `"12-16 horas"`, `"8 a 12 horas"`, `"de 5 hasta 10 horas"`, `"30 horas"`, `"sin dato"`.
- **`perfil_publico`:** `"Básica primaria · Grados 3.º a 5.º"` → grados `(3, 5)`; `"Grados 6 a 9"` en secundaria → `(6, 9)`.
- **Rendimiento (una prueba por expresión):** entradas adversas de **50.000** caracteres deben resolverse en **menos de 1 segundo** (`time.perf_counter()`): `_limpiar("```\n" + "\n" * 50_000 + "x")`, `_RE_SEPARADOR.split("a" + " " * 50_000 + "b")`, `_parsear_numerado("1." + " " * 50_000 + "x" * 50_000)`, `_rango_horas("1" * 50_000 + "x", 3)` y `perfil_publico("primaria 3" + " " * 50_000 + "x")`. (Las versiones antiguas tardaban minutos con esa entrada; las nuevas, milisegundos.)

Ejecuta `python -m pytest`: todo en verde.

---

# FASE 3 — La generación de PDF no debe congelar el servidor

`Orquestador._procesar` llama de forma síncrona a `self._generar_pdfs(trabajo)` (WeasyPrint es intensivo en CPU): mientras genera los PDF, el servidor deja de responder (incluido el sondeo de estado del frontend y `/auth/me`).

1. En `SICCIA/BackEnd/app/orquestador/orquestador.py` cambia
   `pdfs, errores_pdf = self._generar_pdfs(trabajo)`
   por
   `pdfs, errores_pdf = await asyncio.to_thread(self._generar_pdfs, trabajo)`.
   **No cambies la firma ni el cuerpo de `_generar_pdfs`** (las pruebas lo invocan directamente).
2. Como ahora `_generar_pdfs` modifica `trabajo.archivos` en otro hilo mientras el endpoint de estado puede recorrerlo, en `SICCIA/BackEnd/controller/orquestador_controller.py` (línea ~46, dentro de `estado_curso`) recorre una **copia**: cambia `for a in trabajo.archivos.values()` por `for a in list(trabajo.archivos.values())`. No cambies nada más del controlador.
3. Pruebas (en `tests/secuence/test_flujo_fases.py`):
   - **Camino feliz:** con un `_generar_pdfs` simulado que usa `time.sleep(0.2)` y devuelve `(["curso.pdf"], [])`, ejecuta `_procesar` junto a una corrutina "latido" que hace `await asyncio.sleep(0.01)` repetidamente y cuenta ticks; comprueba que el latido avanzó **al menos 5 veces** mientras se generaba el PDF (el loop no se bloquea) y que el trabajo termina en el estado esperado.
   - **Error:** con `_generar_pdfs` que lanza una excepción, el trabajo termina en `ERROR` (o el estado que hoy produce) sin romper el loop.
   - Conserva las pruebas existentes que sustituyen `_generar_pdfs` por una función síncrona.

Ejecuta `python -m pytest`: todo en verde.

---

# FASE 4 — Imports sin usar en pruebas

Elimina estos imports sin uso (verifica que de verdad no se usan en cada archivo):
- `tests/controller/test_orquestador_controller.py`: `crear_configurador`
- `tests/factories.py`: `asyncio`
- `tests/secuence/test_flujo_fases.py`: `pytest` y `ArchivoGenerado`

---

# FASE 5 — Aviso de CSRF (python:S4502, Security Hotspot en `app/__init__.py`)

**Contexto:** SonarQube Cloud marca `app = Flask(__name__)` en `SICCIA/BackEnd/app/__init__.py` con *"Make sure disabling CSRF protection is safe here"*. Es un **Security Hotspot**: no es un defecto de código, sino una revisión que debe quedar justificada. El análisis es que es seguro porque: el servicio Flask solo expone `/auth/google` y `/auth/google/callback` (flujo OAuth protegido por el parámetro `state`), `/auth/me` (solo lectura) y `/auth/logout` (solo cierra la sesión); no hay formularios ni endpoints que modifiquen datos del usuario; y la cookie de sesión es `HttpOnly` y `SameSite=Lax`, por lo que el navegador no la envía en peticiones POST entre sitios.

**No actives `CSRFProtect`, no añadas dependencias y no uses `# NOSONAR`**: el aviso se resuelve revisándolo en la interfaz de SonarQube Cloud.

1. **Documenta la justificación en el código.** En `app/__init__.py`, justo encima de `app = Flask(__name__)`, añade este comentario (en español, conservando la sangría):
```python
    # Seguridad (CSRF), Security Hotspot python:S4502 revisado:
    # no se habilita CSRFProtect porque este servicio solo expone rutas de autenticación:
    #  - /auth/google y /auth/google/callback: flujo OAuth protegido por el parámetro `state`.
    #  - /auth/me: solo lectura.
    #  - /auth/logout: únicamente cierra la sesión.
    # No hay formularios ni endpoints que modifiquen datos del usuario, y la cookie de sesión
    # es HttpOnly y SameSite=Lax (ver Config), por lo que no viaja en peticiones POST entre sitios.
    # Si se agregan endpoints que cambien estado, hay que reevaluar esto y activar CSRFProtect.
```
2. **Pruebas que respaldan esas premisas** (en `tests/controller/test_auth_controller.py`, reutiliza las fixtures y los dobles existentes; evita duplicar pruebas que ya existen):
   - **OK:** tras el callback con usuario simulado (`get_google_user_info` sustituido), la cabecera `Set-Cookie` de la sesión contiene `HttpOnly` y `SameSite=Lax`.
   - **OK:** con `create_app()`, las únicas rutas que aceptan métodos que cambian estado (`POST`, `PUT`, `PATCH`, `DELETE`) son `/auth/logout` (solo `POST`); el resultado exacto del conjunto (ruta, métodos) debe ser `{("/auth/logout", {"POST"})}`. Si una ruta futura rompe esto, la prueba falla y obliga a reevaluar CSRF.
   - **Error:** `GET /auth/google/callback?state=invalido&code=x` sin estado previo en la sesión responde `401` con JSON genérico y **no** crea sesión (`/auth/me` posterior → `401`). Si Authlib intentara descargar metadatos de Google, sustituye `load_server_metadata` por un doble; la red sigue bloqueada en las pruebas.
3. No modifiques `Config` ni los endpoints.

---

# FASE 6 — Verificación final

1. `python -m pytest` desde `SICCIA/BackEnd`: **0 fallidas, 0 omitidas**, cobertura de líneas y ramas **≥ 80 %**, y regenera `reports/coverage.xml` y `reports/junit.xml`.
2. Ejecuta la suite una segunda vez para confirmar que no hay dependencia entre pruebas.
3. Búsqueda global (sin `venv/`, `.venv/`, `node_modules/`): confirma que no quedan referencias a `_RE_NUMERADO`, `ROLES` (como constante de `config.py`) ni a `app.routes`.
4. `git status`: solo deben aparecer los archivos que tocaste y los eliminados; nada de `FrontEnd/` ni `.env`.

# Reporte final

Entrega: (a) por fase, archivos modificados y eliminados; (b) resultados de pruebas antes y después (aprobadas, fallidas, omitidas, cobertura); (c) cualquier punto donde el código real no coincidió con este prompt y qué hiciste; (d) lo que **no** pudiste verificar.

**Pasos manuales para el usuario (no los hagas tú):**
- En SonarQube Cloud: *Security Hotspots → python:S4502 (`app/__init__.py`) → Review → Safe*, con este comentario: *"Revisado: el servicio Flask solo expone rutas de autenticación (OAuth protegido por `state`, lectura de sesión y cierre de sesión); no hay formularios ni endpoints que modifiquen datos, y la cookie de sesión es HttpOnly y SameSite=Lax. Cubierto por pruebas en tests/controller/test_auth_controller.py. Reevaluar si se agregan endpoints que cambien estado."*
- Tras subir los cambios, esperar al análisis de GitHub Actions y confirmar que desaparecen los 5 avisos python:S8786.

=== FIN DEL PROMPT ===
