import uvicorn

from ..server import crear_app

if __name__ == "__main__":
    uvicorn.run(crear_app(), host="127.0.0.1", port=8080)
