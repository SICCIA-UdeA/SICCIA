"""Configuración común de pruebas: no leer .env, no llamar proveedores, forzar mock."""
import os

import dotenv

dotenv.load_dotenv = lambda *args, **kwargs: False  # debe ir ANTES de importar app.config

for _var in list(os.environ):
    if _var.startswith("ORQ_") or _var.endswith("_API_KEY"):
        del os.environ[_var]

os.environ["ORQ_PROVEEDOR"] = "mock"
