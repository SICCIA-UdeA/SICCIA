"""Analiza los .md generados por medir.py (o cualquier carpeta de resultados).

Uso (desde BackEnd/):
    python analizar.py experimentos/
    python analizar.py experimentos/20261014_1200_nvidia/run_01/trabajos/<id>/resultados
    python analizar.py experimentos/ --verificar-enlaces --verificar-refs

Escribe experimentos/analisis.csv: una fila por archivo y por corrida.

Métricas automáticas. La legibilidad usa una aproximación de sílabas (grupos de vocales),
así que es orientativa. La revisión pedagógica NO se automatiza: se hace sobre una muestra
fija elegida antes de leer.
"""
import argparse
import csv
import re
import time
from pathlib import Path

import requests

RE_MODULO = re.compile(r"^#{1,4}\s*M[óo]dulo\s*\d+", re.M | re.I)
RE_URL = re.compile(r"https?://[^\s)\]>\"']+")
RE_LATEX = re.compile(r"\\\(|\\\)|\$\$|\\frac|\\text\{|\\begin\{|\\sqrt|\\cdot")
RE_PREGUNTA = re.compile(r"^\s*\d+[\.\)]\s+\S", re.M)
RE_OPCION = re.compile(r"^\s*[A-Da-d]\)\s+\S", re.M)
RE_SECCION_REF = re.compile(r"^#{1,4}\s*.*(Referencias|Bibliograf[ií]a|Fuentes)", re.M | re.I)
VOCALES = "aeiouáéíóúü"
UA = {"User-Agent": "SICCIA-medicion/1.0 (proyecto academico UdeA)"}


def silabas(palabra: str) -> int:
    # Aproximación: cada grupo de vocales cuenta como una sílaba.
    return max(1, len(re.findall(f"[{VOCALES}]+", palabra.lower())))


def legibilidad_fernandez_huerta(texto: str):
    palabras = re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", texto)
    if not palabras:
        return None
    oraciones = max(1, len(re.findall(r"[.!?]+(?:\s|$)", texto)))
    n = len(palabras)
    p = sum(silabas(w) for w in palabras) / n * 100  # sílabas por 100 palabras
    f = n / oraciones                                # palabras por oración
    return round(206.84 - 0.60 * p - 1.02 * f, 1)


def lineas_referencias(texto: str):
    m = RE_SECCION_REF.search(texto)
    if not m:
        return []
    bloque = texto[m.end():]
    refs = []
    for linea in bloque.splitlines():
        limpia = linea.strip(" -*")
        if re.match(r"^\s*(\[\d+\]|[-*]\s|\d+\.\s)", linea) and len(limpia) > 20:
            refs.append(limpia)
    return refs


def estado_url(url: str) -> str:
    try:
        r = requests.get(url, timeout=10, allow_redirects=True, headers=UA)
        return str(r.status_code)
    except requests.RequestException as exc:
        return type(exc).__name__


def verificar_referencia(ref: str):
    """Busca la referencia en Crossref y comprueba que las palabras del título aparezcan en el texto."""
    consulta = re.sub(r"https?://\S+", "", ref)
    try:
        r = requests.get("https://api.crossref.org/works",
                         params={"query.bibliographic": consulta, "rows": 1},
                         timeout=15, headers=UA)
        items = r.json()["message"]["items"]
        if not items:
            return "sin_resultado", ""
        titulo = (items[0].get("title") or [""])[0]
        palabras = {w for w in re.findall(r"\w+", titulo.lower()) if len(w) > 3}
        if not palabras:
            return "sin_titulo", titulo
        presentes = {w for w in re.findall(r"\w+", consulta.lower()) if len(w) > 3}
        cobertura = len(palabras & presentes) / len(palabras)
        return ("encontrada" if cobertura >= 0.6 else "no_coincide"), titulo
    except Exception as exc:  # noqa: BLE001
        return f"error:{type(exc).__name__}", ""
    finally:
        time.sleep(1)  # cortesía con la API


def archivos_md(raiz: Path):
    if raiz.is_file():
        yield raiz
        return
    for p in sorted(raiz.rglob("*.md")):
        if "interno" in p.parts:  # plantillas internas, no son material
            continue
        yield p


def analizar(archivo: Path, raiz: Path, verificar_enlaces: bool, verificar_refs: bool) -> dict:
    texto = archivo.read_text(encoding="utf-8", errors="replace")
    corrida = str(archivo.relative_to(raiz)) if raiz.is_dir() else archivo.name
    palabras = re.findall(r"\w+", texto)
    urls = sorted(set(RE_URL.findall(texto)))
    refs = lineas_referencias(texto)

    fila = {
        "corrida": corrida,
        "archivo": archivo.name,
        "palabras": len(palabras),
        "legibilidad_fh": legibilidad_fernandez_huerta(texto),
        "modulos": len(set(RE_MODULO.findall(texto))),
        "ejemplos": len(re.findall(r"\bejemplo", texto, re.I)),
        "latex_restos": len(RE_LATEX.findall(texto)),
        "preguntas": len(RE_PREGUNTA.findall(texto)),
        "opciones": len(RE_OPCION.findall(texto)),
        "urls": len(urls),
        "urls_ok": "",
        "seccion_referencias": bool(RE_SECCION_REF.search(texto)),
        "referencias": len(refs),
        "refs_encontradas": "",
    }
    if verificar_enlaces and urls:
        estados = {u: estado_url(u) for u in urls}
        fila["urls_ok"] = sum(1 for s in estados.values() if s == "200")
        fila["detalle_urls"] = "; ".join(f"{u}={s}" for u, s in estados.items())
    if verificar_refs and refs:
        resultados = [verificar_referencia(r) for r in refs]
        fila["refs_encontradas"] = sum(1 for estado, _ in resultados if estado == "encontrada")
        fila["detalle_refs"] = " | ".join(f"{estado}: {titulo[:80]}" for estado, titulo in resultados)
    return fila


def main():
    ap = argparse.ArgumentParser(description="Métricas automáticas de los archivos generados.")
    ap.add_argument("ruta", nargs="?", default="experimentos", help="carpeta o archivo .md")
    ap.add_argument("--salida", default="experimentos/analisis.csv")
    ap.add_argument("--verificar-enlaces", action="store_true", help="pide cada URL (requiere red)")
    ap.add_argument("--verificar-refs", action="store_true", help="busca cada referencia en Crossref (requiere red)")
    args = ap.parse_args()

    raiz = Path(args.ruta)
    if not raiz.exists():
        raise SystemExit(f"No existe: {raiz}")
    archivos = list(archivos_md(raiz))
    if not archivos:
        raise SystemExit("No encontré archivos .md (ignoré las carpetas 'interno').")

    filas = [analizar(a, raiz, args.verificar_enlaces, args.verificar_refs) for a in archivos]

    columnas = []
    for f in filas:
        for k in f:
            if k not in columnas:
                columnas.append(k)
    salida = Path(args.salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    with salida.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=columnas, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)

    print(f"{len(filas)} archivo(s) analizados -> {salida}")
    for f in filas:
        print(f"  {f['corrida'][:60]:60} palabras={f['palabras']:>5} "
              f"legib={f['legibilidad_fh']} modulos={f['modulos']} latex={f['latex_restos']} "
              f"urls={f['urls']} refs={f['referencias']}")


if __name__ == "__main__":
    main()