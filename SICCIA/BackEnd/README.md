# SICCIA BackEnd

Backend HTTP construido con Python con autenticación Google mediante Flask y generación de cursos mediante FastAPI. Ambas aplicaciones se montan detrás de un único servidor ASGI con `a2wsgi` y comparten el puerto `8080`; no es necesario separar los servicios por puertos.

## Funcionalidades actuales

- Inicio de sesión con Google (OAuth 2.0 / OpenID Connect).
- Validación completa de la identidad del usuario (firma, emisor, audiencia y expiración del `id_token`), delegada en una librería mantenida (Authlib), sin implementación manual del protocolo.
- Creación de una sesión de aplicación (cookie de Flask) tras el login exitoso.
- Consulta del usuario autenticado.
- Cierre de sesión.
- Persistencia únicamente en la sesión de Flask (sin base de datos) — pensado para incorporar una base de datos más adelante sin reescribir la autenticación.
- Generación asíncrona de cursos con endpoints para consultar el estado y descargar los materiales.
- Ejecución del orquestador en modo simulado sin credenciales externas, o con proveedores Gemini/OpenAI.

**No incluye actualmente:** frontend, HTML, base de datos, login con usuario/contraseña, roles, JWT propio, CORS ni configuración de despliegue/producción. La sesión de autenticación se mantiene con la cookie firmada de Flask; no se emite un token propio. Los trabajos del orquestador se mantienen en memoria y se pierden al reiniciar el proceso.

## Requisitos previos

- Python 3.10 o superior.
- Una cuenta de Google y un proyecto en [Google Cloud Console](https://console.cloud.google.com/) con credenciales OAuth 2.0 (Client ID y Client Secret). Ver sección [Configuración de Google Cloud](#configuración-de-google-cloud).

## Dependencias

Las dependencias están separadas por servicio en dos manifiestos. Instala ambos para disponer de todo el backend:

| Manifiesto | Librerías principales | Uso |
|---|---|---|
| `requirements.txt` | `Flask`, `Authlib`, `python-dotenv`, `requests` | API de autenticación Google, sesiones y configuración. |
| `app/requirements.txt` | `fastapi`, `uvicorn[standard]`, `a2wsgi`, `pydantic`, `agno`, `google-genai`, `openai`, `pytest`, `pytest-asyncio`, `httpx` | Servidor unificado ASGI, integración WSGI de Flask, API del orquestador, proveedores LLM y pruebas. |

`agno`, `google-genai` y `openai` se usan al seleccionar sus proveedores correspondientes. El modo `mock` del orquestador no necesita claves de modelo.

## Instalación

Desde la raíz del workspace, entra al backend antes de crear el entorno virtual:

```bash
cd SICCIA/BackEnd

# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate.bat       # Windows (cmd)
venv\Scripts\Activate.ps1       # Windows (PowerShell)

# 3. Instalar dependencias de autenticación y del orquestador
pip install -r requirements.txt
pip install -r app/requirements.txt

# 4. Crear el archivo de configuración
cp .env.example .env            # en Windows: copy .env.example .env
```

Edita `.env` y completa:

```text
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
FLASK_SECRET_KEY=...
SESSION_COOKIE_SECURE=False
```

`FLASK_SECRET_KEY` se puede generar con:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Configuración de Google Cloud

1. Entra a [console.cloud.google.com](https://console.cloud.google.com/) y crea un proyecto (o usa uno existente).
2. Ve a **APIs & Services → OAuth consent screen**, elige tipo **External**, y completa nombre de la app y correo de soporte. Los scopes `openid`, `email` y `profile` son básicos y no requieren revisión de Google.
3. Ve a **APIs & Services → Credentials → Create Credentials → OAuth client ID**.
4. En **tipo de aplicación**, elige **Web application**.
5. En **URI de redirección autorizada**, agrega exactamente:
   ```
   http://localhost:8080/auth/google/callback
   ```
6. Copia el **Client ID** y **Client Secret** generados a tu archivo `.env`.

## Ejecución

Desde la raíz del workspace, activa el entorno virtual del backend y ejecuta el módulo como paquete:

```powershell
& .\SICCIA\BackEnd\venv\Scripts\Activate.ps1
python -m SICCIA.BackEnd.run
```

También puedes ejecutar el punto de entrada directamente desde la carpeta del backend:

```powershell
cd SICCIA\BackEnd
python run.py
```

El servidor unificado escucha en `http://127.0.0.1:8080`. Uvicorn sirve la API FastAPI y monta la aplicación Flask mediante `a2wsgi`.

La documentación interactiva de FastAPI se encuentra en `http://127.0.0.1:8080/docs`. No inicies un segundo proceso para el orquestador: el mismo servidor expone ambos grupos de endpoints.

El orquestador usa `mock` por defecto, por lo que puede ejecutarse sin credenciales de IA. Para Gemini configura `ORQ_PROVEEDOR=gemini` y `ORQ_API_KEY` (o `GOOGLE_API_KEY`). También acepta `ORQ_PROVEEDOR=openai` con `ORQ_API_KEY`, o `ORQ_PROVEEDOR=openai_like` con `ORQ_API_KEY` y `ORQ_BASE_URL`. Las variables específicas por rol (`PLANIFICADOR`, `EVALUACION`, `CONTENIDO`, `PROGRAMA`) pueden sobrescribir `ORQ_PROVEEDOR`, `ORQ_MODEL_ID`, `ORQ_API_KEY`, `ORQ_BASE_URL` y `ORQ_TEMPERATURA`; los valores comunes tienen el prefijo `ORQ_`.

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/auth/google` | Inicia el flujo: redirige al usuario a la pantalla de login de Google. |
| `GET` | `/auth/google/callback` | URL de retorno de Google. Valida la respuesta y crea la sesión; no se llama manualmente. |
| `GET` | `/auth/me` | Devuelve los datos del usuario autenticado, o `401` si no hay sesión activa. |
| `GET` | `/auth/logout` | Elimina de la sesión los datos del usuario de la aplicación. No cierra la sesión de Google. |

### Orquestador de cursos (FastAPI, puerto 8080)

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/orquestador/cursos` | Inicia un trabajo de generación y devuelve su `id` y estado inicial (`202`). El cuerpo es un objeto `Configurador`; `datos.tema` es obligatorio. |
| `GET` | `/orquestador/cursos/{trabajo_id}` | Consulta estado, vías ejecutadas, archivos disponibles y posibles errores. |
| `GET` | `/orquestador/cursos/{trabajo_id}/descarga` | Descarga todos los materiales como ZIP; responde `409` si el trabajo no ha terminado y `404` si no generó archivos. |
| `GET` | `/orquestador/cursos/{trabajo_id}/archivos/{nombre}` | Descarga un archivo Markdown generado. |

El configurador acepta `datos`, `contenido`, `evaluacion` y `estilo`. Puedes usar [`app/ejemplo_configurador.json`](app/ejemplo_configurador.json) como referencia. Ejemplo de inicio desde `SICCIA/BackEnd`:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8080/orquestador/cursos `
   -ContentType 'application/json' `
   -InFile .\app\ejemplo_configurador.json
```

La respuesta incluye un identificador de trabajo. Úsalo para consultar su estado o descargar los resultados:

```text
GET http://127.0.0.1:8080/orquestador/cursos/{trabajo_id}
GET http://127.0.0.1:8080/orquestador/cursos/{trabajo_id}/descarga
GET http://127.0.0.1:8080/orquestador/cursos/{trabajo_id}/archivos/{nombre}
```

Los estados posibles son `pendiente`, `planificando`, `ejecutando`, `completado`, `completado_con_errores` y `error`. El identificador solo está disponible mientras el proceso que creó el trabajo siga activo.

Aunque ambas APIs comparten el servidor y puerto, los endpoints del orquestador no están protegidos por la sesión de autenticación Google en la configuración actual.

**Respuesta de `/auth/me` autenticado:**
```json
{
  "authenticated": true,
  "id": "1234567890",
  "name": "Nombre Apellido",
  "email": "usuario@gmail.com",
  "picture": "https://..."
}
```

**Respuesta de `/auth/me` sin sesión:**
```json
{ "authenticated": false }
```
(con código HTTP `401`)

## Probar el flujo (sin frontend)

1. Abrir en el navegador: `http://localhost:8080/auth/google`.
2. Iniciar sesión con una cuenta de Google → redirige automáticamente a `/auth/me` mostrando los datos del usuario.
3. Verificar sin sesión:
   ```bash
   curl -i http://localhost:8080/auth/me
   ```
4. Cerrar sesión:
   ```bash
   curl -i http://localhost:8080/auth/logout
   ```

El login en sí debe probarse desde el navegador, porque requiere la pantalla interactiva de Google; `curl`/Postman sirven para inspeccionar `/auth/me` y `/auth/logout` reutilizando la cookie de sesión del navegador.

## Arquitectura del paquete

La factoría `app.server.crear_app()` crea la API FastAPI del orquestador y monta la app Flask con `a2wsgi`. Uvicorn sirve ambas en el mismo puerto; Flask conserva la gestión de sesiones y Authlib.

```mermaid
flowchart LR
   Client[Cliente HTTP o futuro frontend] -->|Solicitudes HTTP| Run[run.py]
   Run --> Server[app.server.crear_app]
   Server --> Orchestrator[FastAPI app.orquestador.app]
   Server --> WSGI[a2wsgi WSGIMiddleware]
   WSGI --> Flask[app.create_app]
   Flask --> Config[app.config.Config]
   Flask --> AuthController[controller.auth_controller]
   Flask --> OAuthInit[app.services.google_auth]
   Orchestrator --> CourseController[controller.orquestador_controller]
   CourseController -->|POST, consulta y descargas| Client
   AuthController -->|Iniciar login y procesar callback| OAuthInit
   OAuthInit <-->|OAuth 2.0 / OIDC| Google[Google Identity]
   AuthController <-->|Lee y modifica| Session[Cookie de sesión Flask]
   AuthController -->|JSON o redirección| Client
   Config -->|Variables de entorno y .env| Flask
```

### Estructura actual

```text
SICCIA/
├── __init__.py
└── BackEnd/
   ├── __init__.py
   ├── run.py
   ├── controller/
   │  ├── __init__.py
   │  ├── auth_controller.py
   │  └── orquestador_controller.py
   ├── requirements.txt
   ├── .env.example
   ├── README.md
   └── app/
      ├── __init__.py
      ├── config.py
      ├── server.py
      ├── requirements.txt
      ├── ejemplo_configurador.json
      ├── tests/
      ├── orquestador/
         ├── __main__.py
         ├── app.py
         ├── orquestador.py
         ├── schemas.py
         └── agentes/
      └── services/
         └── google_auth.py
```

- `SICCIA/__init__.py` y `SICCIA/BackEnd/__init__.py` permiten importar el backend como paquete (`SICCIA.BackEnd`).
- `run.py` es el punto de entrada único y admite `python -m SICCIA.BackEnd.run` desde la raíz o `python run.py` desde `SICCIA/BackEnd`; ambos inician Uvicorn en el puerto `8080`.
- `app/server.py` monta la aplicación Flask de autenticación en FastAPI usando `a2wsgi`.
- `app/__init__.py` define `create_app()`; `config.py` carga `.env` y valida las credenciales requeridas.
- `controller/auth_controller.py` expone los endpoints de autenticación, `controller/orquestador_controller.py` expone los endpoints de cursos y `app/services/google_auth.py` encapsula la integración con Authlib.
- `app/orquestador/` contiene la API FastAPI, los esquemas, la planificación y los agentes que generan los materiales.
- `.env` contiene la configuración local y no debe publicarse. `.env.example` sirve como plantilla.

## Flujo de los endpoints

El flujo de login empieza en `/auth/google`. Authlib genera y conserva el `state`; Google devuelve el navegador a `/auth/google/callback`. Tras validar la respuesta, la aplicación guarda solo los datos de perfil necesarios en la sesión y redirige a `/auth/me`.

```mermaid
flowchart TD
   Start([Cliente]) --> Choice{Endpoint solicitado}

   Choice -->|GET /auth/google| Login[Construir URL del callback]
   Login --> Authorize[Authlib crea state y URL de autorización]
   Authorize --> GoogleLogin[Redirección a Google]
   GoogleLogin --> UserLogin[El usuario inicia sesión y autoriza]
   UserLogin --> GoogleReturn[Google redirige a /auth/google/callback con code y state]
   GoogleReturn --> Validate[Authlib valida state e intercambia code por tokens]
   Validate --> TokenValid{Respuesta OIDC válida}
   TokenValid -->|No, ocurre una excepción| AuthError[JSON de error, HTTP 401]
   TokenValid -->|Sí| Profile[Obtener userinfo verificado]
   Profile --> SaveSession[Guardar id, name, email y picture en sesión Flask]
   SaveSession --> RedirectMe[Redirigir a /auth/me]

   Choice -->|GET /auth/me| CheckSession{¿Hay usuario en la sesión?}
   RedirectMe --> CheckSession
   CheckSession -->|No| Anonymous[JSON authenticated false, HTTP 401]
   CheckSession -->|Sí| UserData[JSON authenticated true con datos del perfil, HTTP 200]

   Choice -->|GET /auth/logout| RemoveUser[Eliminar user de la sesión]
   RemoveUser --> LoggedOut[JSON logged_out true, HTTP 200]
```

`/auth/me` y `/auth/logout` pueden llamarse directamente, sin completar el login. La cookie de sesión debe conservarse entre solicitudes para que el cliente siga autenticado. Como no hay CORS configurado, un futuro frontend servido desde otro origen requerirá definir explícitamente CORS y el envío de credenciales/cookies.

### Qué recibe realmente el backend

Del `id_token` ya verificado se extrae `sub` (identificador único y estable de la cuenta, usado como `id`), `name`, `email` y `picture`. Eso es lo único que se guarda en la sesión de Flask. El `access_token` y el `id_token` crudo se usan una sola vez durante el callback y no se persisten. Nunca se recibe ni se almacena la contraseña del usuario.

### Conceptos clave

- **OAuth 2.0**: protocolo de *autorización* — permite acceder a recursos en nombre del usuario sin conocer su contraseña.
- **OpenID Connect (OIDC)**: capa de *autenticación* sobre OAuth 2.0; añade el `id_token`, que identifica quién es el usuario.
- **ID token**: JWT firmado por Google que certifica la identidad.
- **Access token**: credencial para llamar a APIs de Google en nombre del usuario (aquí solo se usa como respaldo si el `id_token` no trae `userinfo`).
- **Sesión de Flask**: cookie firmada por el propio backend que mantiene al usuario "logueado" entre peticiones, independiente de Google.
- **`sub` de Google**: identificador único y permanente de la cuenta — más confiable que el email como clave de usuario, ya que el email puede cambiar.

## Seguridad implementada

- `state` generado y validado automáticamente en el flujo OAuth (protección contra CSRF).
- Validación completa del `id_token` (firma contra las claves públicas de Google, emisor, audiencia y expiración).
- `sub` usado como identificador estable, no el email.
- Cookies de sesión `HttpOnly` y `SameSite=Lax`; `Secure` activable vía `SESSION_COOKIE_SECURE` para producción (HTTPS).
- `GOOGLE_CLIENT_SECRET` y `FLASK_SECRET_KEY` solo en `.env`, excluido de git mediante `.gitignore`.
- No se almacenan contraseñas, tokens de Google ni información innecesaria del usuario.
- Los errores del proceso de autenticación no exponen detalles internos al cliente.

## Extensibilidad

La separación entre `controller/` (HTTP) y `app/services/` (integración con Google) permite, por ejemplo, incorporar una base de datos más adelante sustituyendo `session[...] = user_info` por una función que busque o cree el usuario usando `sub` como clave, sin tocar la integración OAuth.
