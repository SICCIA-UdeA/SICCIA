"""Experimento reproducible con el orquestador real.

Uso (desde BackEnd/, con el .env configurado):
    python medir.py --etiqueta nvidia-tema1 --repeticiones 3 --confirmar
    python medir.py --etiqueta prueba-mock --repeticiones 1 --confirmar   (sin proveedores)

Sin --confirmar no hace nada: cada repetición llama a los proveedores y consume cuota.
Cada repetición va a experimentos/<fecha>_<etiqueta>/run_NN/ con su propio registro de tokens.
Una fila por corrida se agrega a experimentos/experimento.csv.
"""
import argparse
import asyncio
import csv
import hashlib
import json
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent
load_dotenv(RAIZ / ".env")
sys.path.insert(0, str(RAIZ))

from app.orquestador import Configurador, Orquestador  # noqa: E402
from app.orquestador.config import config_modelo  # noqa: E402

TIMEOUT_S = 1800  # 30 min por corrida
COLUMNAS = ["fecha", "etiqueta", "corrida", "repeticion", "config_sha", "modelos", "estado",
            "duracion_s", "archivos", "llamadas_registradas", "prompt_tokens", "completion_tokens",
            "vias", "error"]


def snapshot_modelos() -> str:
    roles = ("planificador", "evaluacion", "contenido", "programa", "verificacion")
    return ";".join(
        f"{rol}={config_modelo(rol).proveedor}:{config_modelo(rol).model_id}" for rol in roles
    )


def resumen_tokens(dir_run: Path):
    registro = dir_run / "registro_pruebas_siccia.csv"
    if not registro.exists():
        return 0, 0, 0
    pt = ct = n = 0
    with registro.open(encoding="utf-8") as fh:
        for fila in csv.DictReader(fh, delimiter=";"):
            n += 1
            try:
                pt += int(fila.get("Prompt_Tokens") or 0)
                ct += int(fila.get("Completion_Tokens") or 0)
            except ValueError:
                pass
    return pt, ct, n


async def correr_una(config_dict: dict, dir_run: Path):
    cfg = Configurador.model_validate(config_dict)
    dir_run.mkdir(parents=True, exist_ok=True)
    cwd_previo = os.getcwd()
    os.chdir(dir_run)  # log_prueba escribe el registro en el directorio actual
    try:
        orq = Orquestador(directorio=dir_run / "trabajos")
        t0 = time.time()
        trabajo = orq.iniciar(cfg)
        while not trabajo.terminado and time.time() - t0 < TIMEOUT_S:
            await asyncio.sleep(0.5)
        return trabajo, time.time() - t0
    finally:
        os.chdir(cwd_previo)


def main():
    ap = argparse.ArgumentParser(description="Corre el orquestador N veces con la misma configuración.")
    ap.add_argument("--etiqueta", required=True, help="nombre corto del experimento, sin espacios")
    ap.add_argument("--config", default="app/ejemplo_configurador.json")
    ap.add_argument("--repeticiones", type=int, default=3)
    ap.add_argument("--confirmar", action="store_true",
                    help="obligatorio: cada repetición llama a los proveedores configurados")
    args = ap.parse_args()

    if not args.confirmar:
        raise SystemExit("No corrí nada. Agrega --confirmar: cada repetición consume cuota.")

    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = RAIZ / config_path
    config_dict = json.loads(config_path.read_text(encoding="utf-8"))
    config_sha = hashlib.sha256(config_path.read_bytes()).hexdigest()[:12]
    modelos = snapshot_modelos()
    if "mock" in modelos:
        print("AVISO: algún rol usa 'mock'. Esto no mide modelos reales.")

    base = RAIZ / "experimentos" / f"{datetime.now():%Y%m%d_%H%M}_{args.etiqueta}"
    base.mkdir(parents=True, exist_ok=True)
    shutil.copy(config_path, base / "config.json")  # para reproducir el experimento

    ruta_csv = RAIZ / "experimentos" / "experimento.csv"
    nuevo = not ruta_csv.exists()
    with ruta_csv.open("a", newline="", encoding="utf-8") as fh:
        escritor = csv.DictWriter(fh, fieldnames=COLUMNAS, delimiter=";")
        if nuevo:
            escritor.writeheader()

        for i in range(1, args.repeticiones + 1):
            dir_run = base / f"run_{i:02d}"
            print(f"\n== Repetición {i}/{args.repeticiones} ({args.etiqueta}) ==")
            trabajo, duracion = asyncio.run(correr_una(config_dict, dir_run))
            pt, ct, n = resumen_tokens(dir_run)
            errores = [k for k, v in trabajo.vias.items() if str(v).startswith("error")]
            fila = {
                "fecha": datetime.now().isoformat(timespec="seconds"),
                "etiqueta": args.etiqueta,
                "corrida": dir_run.name,
                "repeticion": i,
                "config_sha": config_sha,
                "modelos": modelos,
                "estado": trabajo.estado.value,
                "duracion_s": round(duracion, 1),
                "archivos": len(trabajo.archivos),
                "llamadas_registradas": n,
                "prompt_tokens": pt,
                "completion_tokens": ct,
                "vias": json.dumps(trabajo.vias, ensure_ascii=False),
                "error": (trabajo.error or "") + (f" vias_con_error={errores}" if errores else ""),
            }
            escritor.writerow(fila)
            fh.flush()
            print(f"   estado={fila['estado']} tokens={pt}+{ct} archivos={fila['archivos']} "
                  f"duración={fila['duracion_s']}s")

    print(f"\nListo. Carpeta: {base}\nResumen acumulado: {ruta_csv}")


if __name__ == "__main__":
    main()