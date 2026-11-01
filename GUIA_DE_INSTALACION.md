# Guía de instalación de SICCIA

Esta guía cubre la primera ejecución local desde una clonación limpia. La lista versionada de dependencias Python es `dependencias.txt`, en la raíz del repositorio.

## 1. Requisitos

- Git.
- Python 3.13 recomendado; el proyecto requiere Python 3.10 como mínimo.
- Node.js y npm, o Bun, para el frontend.
- Una cuenta/proyecto de Google Cloud con credenciales OAuth 2.0 para iniciar sesión con Google.
- Bibliotecas nativas de Pango/GTK para que WeasyPrint pueda generar los PDF.

## 2. Clonar el repositorio

```sh
git clone https://github.com/SICCIA-UdeA/SICCIA.git
cd SICCIA
```

`git` solo descarga el código fuente; las librerías del proyecto se instalan después con `pip`.

## 3. Crear el entorno Python e instalar las dependencias

### Windows (PowerShell)

```powershell
cd .\SICCIA\BackEnd
py -3.13 -m venv .\venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r ..\..\dependencias.txt
Copy-Item .env.example .env
```

Si PowerShell impide activar el entorno, permite scripts locales para el usuario o ejecuta los comandos de Python mediante `.\venv\Scripts\python.exe`.

### macOS / Linux

```sh
cd SICCIA/BackEnd
python3.13 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r ../../dependencias.txt
cp .env.example .env
```

## 4. Instalar los requisitos del sistema para WeasyPrint

Instalar el paquete Python no instala las bibliotecas nativas que representan las fuentes y dibujan el PDF.

- **Windows:** instala un GTK3 runtime compatible o MSYS2 con Pango y sus dependencias. En MSYS2, instala el paquete Pango de 64 bits y agrega el directorio `mingw64\bin` (por ejemplo, `C:\msys64\mingw64\bin`) al `PATH` disponible para Python.
- **Linux Debian/Ubuntu:**

  ```sh
  sudo apt-get update
  sudo apt-get install -y libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libfontconfig1 libgdk-pixbuf-2.0-0 libffi8 shared-mime-info
  ```

- **macOS:**

  ```sh
  brew install pango
  ```

Comprueba que Python puede cargar WeasyPrint y sus bibliotecas nativas:

```sh
python -c "from weasyprint import HTML; print('WeasyPrint disponible')"
```

Si el comando falla, revisa la instalación nativa antes de generar cursos. El backend informa el motivo en `advertencias` y no ofrece un ZIP vacío.

## 5. Configurar el backend y Google OAuth

Edita `SICCIA/BackEnd/.env`, creado desde `.env.example`. Completa los valores de credenciales localmente; no los publiques ni los agregues al repositorio.

```dotenv
BACKEND_PORT=8084
FRONTEND_PORT=8085
GOOGLE_REDIRECT_URI=http://localhost:8084/auth/google/callback
```

El ejemplo incluye también la selección de proveedores de IA y la asociación de proveedores con cada vía. Para una prueba sin claves de IA usa el modo `mock` (por ejemplo, `ORQ_PROVEEDOR=mock` y las vías configuradas como `mock`). Para generar contenido con modelos reales, configura localmente el proveedor y sus claves de API.

En Google Cloud Console, abre **APIs y servicios → Credenciales → cliente OAuth** y agrega esta URI en **URI de redirección autorizadas**:

```text
http://localhost:8084/auth/google/callback
```

## 6. Instalar el frontend

Desde otra terminal, en `SICCIA/FrontEnd`:

```sh
bun install
```

También se puede usar npm:

```sh
npm install
```

Los puertos y la URL del proxy se configuran mediante `BACKEND_PORT`, `FRONTEND_PORT` y, opcionalmente, `BACKEND_URL` en `SICCIA/FrontEnd/.env`.

## 7. Ejecutar la aplicación

Abre dos terminales desde la raíz del repositorio.

**Terminal 1 — backend:**

```powershell
cd .\SICCIA\BackEnd
.\venv\Scripts\Activate.ps1
python run.py
```

**Terminal 2 — frontend:**

```powershell
cd .\SICCIA\FrontEnd
bun run dev
```

Con npm, usa `npm run dev`. Abre **http://localhost:8085**. Usa siempre `localhost` (no `127.0.0.1`) para mantener consistente la cookie de sesión entre el frontend, el proxy y OAuth.

## 8. Ejecutar las pruebas

Con el entorno Python activado:

```powershell
cd .\SICCIA\BackEnd
python -m pytest
```

La suite está aislada de la red, los proveedores externos y el motor nativo de WeasyPrint. Consulta la [matriz de pruebas](SICCIA/BackEnd/tests/MATRIZ_PRUEBAS.md) para ver la trazabilidad funcional y los resultados. Se generan reportes compatibles con SonarCloud en `SICCIA/BackEnd/reports/coverage.xml` (Cobertura) y `SICCIA/BackEnd/reports/junit.xml` (JUnit); ambos se ignoran en Git.

## 9. Solución de problemas

- **`redirect_uri_mismatch`:** la URI configurada en `.env` debe coincidir exactamente con Google Cloud: `http://localhost:8084/auth/google/callback`. Si cambias `BACKEND_PORT`, actualiza también `GOOGLE_REDIRECT_URI` y la URI autorizada en Google Cloud.
- **Puerto ocupado:** cambia `BACKEND_PORT` o `FRONTEND_PORT` en la configuración local. Reinicia el servidor correspondiente después del cambio. Vite usa `strictPort` y falla explícitamente si el puerto frontend solicitado está ocupado.
- **WeasyPrint “cannot load library”:** confirma que Pango/GTK está instalado, que coincide con la arquitectura de Python y que sus directorios de bibliotecas están en `PATH` (Windows) o disponibles para el cargador del sistema (macOS/Linux).
- **ZIP sin PDF:** consulta `GET /orquestador/cursos/{id}` y revisa `estado`, `error` y `advertencias`. Verifica primero WeasyPrint y sus bibliotecas nativas; el backend ya no crea ZIP vacíos con respuesta exitosa.
- **Entrar por `127.0.0.1`:** abre la aplicación mediante `http://localhost:8085`; no alternes entre `localhost` y `127.0.0.1`.
- **Cookie o sesión inesperada:** limpia las cookies locales y vuelve a iniciar sesión. Un reinicio del backend invalida las sesiones anteriores; después de reiniciar, inicia sesión otra vez.

## Flujo de uso

**Login con Google → panel principal → configurar y generar un curso → descargar el ZIP de PDF.**
