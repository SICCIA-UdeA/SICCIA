import re
import markdown
import requests
import os
from pathlib import Path

# Intenta importar WeasyPrint (si falla en Codespaces, avisa, pero el código queda listo)
try:
    from weasyprint import HTML
    WEASYPRINT_OK = True
except ImportError:
    WEASYPRINT_OK = False

def obtener_imagen_unsplash(palabras_clave: str) -> str:
    """Tu función original para obtener imágenes de Unsplash."""
    # Como no tenemos la API key de Unsplash a la mano, usamos Source Unsplash que es libre y no pide Key:
    terminos = palabras_clave.replace(" ", ",")
    return f"https://source.unsplash.com/800x400/?{terminos}"

def procesar_imagenes_y_pdf(directorio_trabajo: Path, archivos_generados: dict):
    """Reemplaza los tags de Unsplash de Steven y convierte a PDF con tu código WeasyPrint."""
    
    for nombre_archivo, archivo_obj in archivos_generados.items():
        if nombre_archivo.endswith(".md"):
            texto_md = archivo_obj.contenido
            
            # 1. Tu lógica: Buscar y reemplazar imágenes de Unsplash
            # Busca: ![alt](unsplash:perro feliz) y lo cambia por la URL real
            def reemplazo_img(match):
                alt_text = match.group(1)
                keywords = match.group(2)
                url = obtener_imagen_unsplash(keywords)
                return f"![{alt_text}]({url})"
                
            texto_md_con_imgs = re.sub(r"!\[(.*?)\]\(unsplash:(.*?)\)", reemplazo_img, texto_md)
            
            # 2. Tu lógica: Convertir a PDF (Si WeasyPrint está instalado)
            if WEASYPRINT_OK:
                # Convertir MD a HTML
                html_base = markdown.markdown(texto_md_con_imgs, extensions=['tables', 'fenced_code'])
                html_completo = f"""
                <html><head><style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }}
                    h1, h2, h3 {{ color: #2C3E50; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    img {{ max-width: 100%; border-radius: 8px; }}
                </style></head><body>{html_base}</body></html>
                """
                
                nombre_pdf = nombre_archivo.replace(".md", ".pdf")
                ruta_pdf = directorio_trabajo / nombre_pdf
                
                # WeasyPrint hace la magia
                HTML(string=html_completo).write_pdf(ruta_pdf)
                print(f"✅ PDF Generado exitosamente: {nombre_pdf}")