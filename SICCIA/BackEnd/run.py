"""
Punto de entrada para ejecutar el backend localmente.

Uso:
    python run.py
"""

if __package__:
    from .app import create_app
else:
    from app import create_app

app = create_app()

if __name__ == "__main__":
    # debug=True solo para desarrollo local: recarga automática y
    # mensajes de error detallados. Nunca debe usarse en producción.
    app.run(host="localhost", port=5000, debug=True)
