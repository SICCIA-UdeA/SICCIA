from __future__ import annotations

import argparse
import importlib.metadata
import os
import shutil
import signal
import subprocess
import sys
import threading
from pathlib import Path
from typing import Iterable, Mapping


ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "SICCIA" / "BackEnd"
FRONTEND_DIR = ROOT / "SICCIA" / "FrontEnd"


def normalize_package_name(name: str) -> str:
    return name.strip().lower().replace("_", "-").replace(".", "-")


def parse_requirements(requirement_file: Path) -> list[str]:
    """Lee nombres de paquetes de requirements.txt."""
    packages: list[str] = []
    for raw_line in requirement_file.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or line.startswith(("-r", "-e", "--")):
            continue
        line = line.split(";", 1)[0].strip()
        package = line
        for operator in ("==", ">=", "<=", "~=", "!=", "<", ">"):
            if operator in package:
                package = package.split(operator, 1)[0]
                break
        package = package.split("[", 1)[0].strip()
        if package:
            packages.append(normalize_package_name(package))
    return packages


def find_missing_packages(
    requirement_files: Iterable[Path],
    installed_packages: Iterable[str] | None = None,
) -> list[str]:
    if installed_packages is None:
        installed_packages = (
            normalize_package_name(distribution.metadata["Name"] or "")
            for distribution in importlib.metadata.distributions()
            if distribution.metadata.get("Name")
        )
    installed = {normalize_package_name(name) for name in installed_packages}
    missing: list[str] = []
    for requirement_file in requirement_files:
        for package in parse_requirements(requirement_file):
            if package not in installed and package not in missing:
                missing.append(package)
    return missing


def choose_frontend_manager() -> str | None:
    if shutil.which("bun"):
        return "bun"
    npm = "npm.cmd" if os.name == "nt" else "npm"
    if shutil.which(npm):
        return "npm"
    return None


def read_backend_port(
    env: Mapping[str, str] | None = None,
    env_file: Path | None = None,
    backend_dir: Path | None = None,
) -> int:
    environment = os.environ if env is None else env
    if "BACKEND_PORT" in environment:
        value = environment["BACKEND_PORT"].strip()
    else:
        if env_file is None:
            directory = BACKEND_DIR if backend_dir is None else backend_dir
            env_file = directory / ".env" if directory.is_dir() else directory
        value = ""
        if env_file.exists():
            for raw_line in env_file.read_text(encoding="utf-8", errors="replace").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, candidate = line.split("=", 1)
                if key.strip() == "BACKEND_PORT":
                    value = candidate.strip()
                    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                        value = value[1:-1].strip()
                    break
    try:
        port = int(value)
        if 1 <= port <= 65535:
            return port
    except (TypeError, ValueError):
        pass
    return 8084


def check_backend_packages(requirement_files: Iterable[Path]) -> list[str]:
    return find_missing_packages(requirement_files)


def install_missing_requirements(requirement_files: Iterable[Path]) -> bool:
    for requirement_file in requirement_files:
        missing = find_missing_packages([requirement_file])
        if not missing:
            continue
        print(
            "Faltan paquetes de Python en "
            f"{requirement_file}: {', '.join(missing)}"
        )
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirement_file)],
                check=True,
            )
        except subprocess.CalledProcessError as error:
            print(
                "Error: pip no pudo instalar las dependencias del backend "
                f"(código {error.returncode}).",
                file=sys.stderr,
            )
            print(
                "Puede ser necesario permitir pip en un entorno gestionado o "
                "activar el entorno correcto.",
                file=sys.stderr,
            )
            return False
        except OSError as error:
            print(f"Error al ejecutar pip: {error}", file=sys.stderr)
            return False
    return True


def check_frontend_tools() -> tuple[bool, str | None, str | None]:
    node = shutil.which("node")
    if node is None:
        return False, None, "Node.js"
    manager = choose_frontend_manager()
    if manager is None:
        return True, None, "Bun o npm"
    return True, manager, None


def install_frontend_dependencies() -> bool:
    node = shutil.which("node")
    if node is None:
        print(
            "Error: Node.js no está disponible. Instale Node.js para ejecutar el frontend.",
            file=sys.stderr,
        )
        return False
    manager = choose_frontend_manager()
    if manager is None:
        print(
            "Error: no se encontró bun ni npm. Instale Bun o Node.js/npm.",
            file=sys.stderr,
        )
        return False
    if (FRONTEND_DIR / "node_modules").exists():
        return True
    command = "bun" if manager == "bun" else ("npm.cmd" if os.name == "nt" else "npm")
    try:
        subprocess.run([command, "install"], cwd=FRONTEND_DIR, check=True)
        return True
    except subprocess.CalledProcessError as error:
        print(
            f"Error: falló la instalación de dependencias del frontend "
            f"(código {error.returncode}).",
            file=sys.stderr,
        )
        return False
    except OSError as error:
        print(f"Error al ejecutar {command}: {error}", file=sys.stderr)
        return False


def read_dev_command() -> list[str] | None:
    package_file = FRONTEND_DIR / "package.json"
    if not package_file.exists():
        print("Error: no existe SICCIA/FrontEnd/package.json.", file=sys.stderr)
        return None
    try:
        import json

        package = json.loads(package_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"Error al leer package.json: {error}", file=sys.stderr)
        return None
    if "dev" not in package.get("scripts", {}):
        print("Error: package.json no contiene el script \"dev\".", file=sys.stderr)
        return None
    manager = choose_frontend_manager()
    if manager is None:
        print("Error: no se encontró bun ni npm.", file=sys.stderr)
        return None
    command = "bun" if manager == "bun" else ("npm.cmd" if os.name == "nt" else "npm")
    return [command, "run", "dev"]


def process_group_kwargs() -> dict:
    if os.name == "nt":
        return {"creationflags": getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)}
    return {"start_new_session": True}


def terminate_process(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/T", "/F", "/PID", str(process.pid)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    else:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            return
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/T", "/F", "/PID", str(process.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        else:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def stream_output(process: subprocess.Popen, label: str) -> None:
    if process.stdout is None:
        return
    for raw_line in iter(process.stdout.readline, ""):
        if not raw_line:
            break
        line = raw_line.rstrip("\r\n")
        print(f"[{label}] {line}", flush=True)
        if label == "frontend" and "Local:" in line:
            for part in line.split():
                if part.startswith("http://") or part.startswith("https://"):
                    print(f"\n  >>> Frontend disponible en: {part.rstrip(' ,')} <<<\n", flush=True)
                    break


def run_project() -> int:
    if not (BACKEND_DIR / ".env").exists():
        print(
            "Advertencia: no existe SICCIA/BackEnd/.env. Cree uno desde "
            ".env.example; sin él los roles pueden caer en modo simulado.",
        )

    backend_port = read_backend_port()
    print(f"Backend: http://127.0.0.1:{backend_port}")

    dev_command = read_dev_command()
    if dev_command is None:
        return 1

    backend_env = os.environ.copy()
    backend_env["PYTHONUNBUFFERED"] = "1"
    try:
        backend = subprocess.Popen(
            [sys.executable, "-u", "run.py"],
            cwd=BACKEND_DIR,
            env=backend_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            **process_group_kwargs(),
        )
    except OSError as error:
        print(f"Error al iniciar el backend: {error}", file=sys.stderr)
        return 1
    try:
        frontend = subprocess.Popen(
            dev_command,
            cwd=FRONTEND_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            **process_group_kwargs(),
        )
    except OSError as error:
        print(f"Error al iniciar los procesos: {error}", file=sys.stderr)
        terminate_process(backend)
        return 1

    threads = [
        threading.Thread(target=stream_output, args=(backend, "backend"), daemon=True),
        threading.Thread(target=stream_output, args=(frontend, "frontend"), daemon=True),
    ]
    for thread in threads:
        thread.start()

    try:
        while True:
            backend_code = backend.poll()
            frontend_code = frontend.poll()
            if backend_code is not None:
                print(
                    f"El proceso backend terminó con código de salida {backend_code}.",
                    file=sys.stderr,
                )
                terminate_process(frontend)
                return backend_code if backend_code != 0 else 1
            if frontend_code is not None:
                print(
                    f"El proceso frontend terminó con código de salida {frontend_code}.",
                    file=sys.stderr,
                )
                terminate_process(backend)
                return frontend_code if frontend_code != 0 else 1
            threading.Event().wait(0.2)
    except KeyboardInterrupt:
        print("\nInterrupción recibida. Cerrando backend y frontend...", flush=True)
        terminate_process(frontend)
        terminate_process(backend)
        return 130


def check_only(requirement_files: Iterable[Path]) -> int:
    missing = check_backend_packages(requirement_files)
    if missing:
        print("Paquetes de Python faltantes: " + ", ".join(missing))
    else:
        print("Dependencias de Python: listas")

    node = shutil.which("node")
    if node is None:
        print("Node.js: falta")
    else:
        print("Node.js: disponible")

    manager = choose_frontend_manager()
    if manager is None:
        print("Gestor frontend: falta bun y npm")
    else:
        print(f"Gestor frontend: {manager} disponible")

    if (FRONTEND_DIR / "node_modules").exists():
        print("node_modules: disponible")
    else:
        print("node_modules: falta")

    all_ready = (
        not missing
        and node is not None
        and manager is not None
        and (FRONTEND_DIR / "node_modules").exists()
    )
    return 0 if all_ready else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Orquestador de backend y frontend SICCIA")
    parser.add_argument("--check", action="store_true", help="Solo verifica dependencias")
    args = parser.parse_args()

    requirement_files = [
        BACKEND_DIR / "requirements.txt",
        BACKEND_DIR / "app" / "requirements.txt",
    ]
    if args.check:
        return check_only(requirement_files)

    if shutil.which("node") is None:
        print(
            "Error: Node.js no está disponible. Instale Node.js para ejecutar el frontend.",
            file=sys.stderr,
        )
        return 1

    if not install_missing_requirements(requirement_files):
        return 1
    if not install_frontend_dependencies():
        return 1
    return run_project()


if __name__ == "__main__":
    raise SystemExit(main())
