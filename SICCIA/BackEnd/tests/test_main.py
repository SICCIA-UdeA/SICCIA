from __future__ import annotations

import importlib.util
import os
import shutil
import sys
from pathlib import Path


MAIN_PATH = Path(__file__).resolve().parents[3] / "main.py"
spec = importlib.util.spec_from_file_location("siccia_main", MAIN_PATH)
assert spec and spec.loader
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)


def test_parse_requirements_comments_extras_versions_and_includes(tmp_path):
    file = tmp_path / "requirements.txt"
    file.write_text(
        """
# comentario completo
Flask==3.1.0
uvicorn[standard]
pydantic>=2
google-genai   # necesario para Gemini
-r otras.txt
-e git+https://example.com/pkg
--extra-index-url https://example.com
requests!=2.32.3; python_version >= "3.10"
""".strip(),
        encoding="utf-8",
    )

    assert main.parse_requirements(file) == [
        "flask",
        "uvicorn",
        "pydantic",
        "google-genai",
        "requests",
    ]


def test_find_missing_packages_with_simulated_installed(tmp_path):
    file = tmp_path / "requirements.txt"
    file.write_text(
        "FastAPI>=0.1\npython_dotenv==1.0\nuvicorn[standard]\n",
        encoding="utf-8",
    )

    assert main.find_missing_packages([file], {"fastapi", "python-dotenv"}) == [
        "uvicorn"
    ]


def test_choose_frontend_manager_prefers_bun(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: "/bin/tool" if name in ("bun", "npm") else None)

    assert main.choose_frontend_manager() == "bun"


def test_choose_frontend_manager_uses_npm(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: "/bin/npm" if name in ("npm", "npm.cmd") else None)

    assert main.choose_frontend_manager() == "npm"


def test_choose_frontend_manager_returns_none(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: None)

    assert main.choose_frontend_manager() is None


def test_read_backend_port_from_environment(monkeypatch):
    monkeypatch.setenv("BACKEND_PORT", "9090")

    assert main.read_backend_port(env=os.environ, env_file=Path("/no/existe/.env")) == 9090


def test_read_backend_port_from_dotenv(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "# no exponer secretos\nOTRA=valor\nBACKEND_PORT='8181'\n",
        encoding="utf-8",
    )

    assert main.read_backend_port(env={}, env_file=env_file) == 8181


def test_read_backend_port_defaults_to_8084(tmp_path):
    assert main.read_backend_port(env={}, env_file=tmp_path / ".env") == 8084
