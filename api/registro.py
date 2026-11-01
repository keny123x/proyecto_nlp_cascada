import time
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.config import LOG_ARCHIVO

FORMATO = "%(asctime)s | %(levelname)s | %(message)s"


def crear_logger() -> logging.Logger:
    """Logger de la API: escribe en consola y, si se configura LOG_ARCHIVO, también en un archivo."""
    logger = logging.getLogger("api_sentimiento")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)

    consola = logging.StreamHandler()
    consola.setFormatter(logging.Formatter(FORMATO, "%Y-%m-%d %H:%M:%S"))
    logger.addHandler(consola)

    if LOG_ARCHIVO:
        archivo = logging.FileHandler(LOG_ARCHIVO, encoding='utf-8')
        archivo.setFormatter(logging.Formatter(FORMATO, "%Y-%m-%d %H:%M:%S"))
        logger.addHandler(archivo)
    return logger


logger = crear_logger()


def registrar_peticiones(app: FastAPI):
    """Middleware que anota cada petición con su ruta, código de respuesta y duración."""
    @app.middleware("http")
    async def medir_peticion(request: Request, call_next):
        inicio = time.perf_counter()
        try:
            respuesta = await call_next(request)
        except Exception as e:
            # Se responde aquí (dentro de CORS) para que el navegador reciba el error real
            # y no un bloqueo CORS genérico.
            logger.exception(f"Error no controlado en {request.method} {request.url.path}")
            respuesta = JSONResponse(
                status_code=500,
                content={"error": "Error interno del servidor", "detalles": [{"campo": None, "mensaje": str(e)}]},
            )
        ms = (time.perf_counter() - inicio) * 1000
        logger.info(f"{request.method} {request.url.path} -> {respuesta.status_code} ({ms:.1f} ms)")
        return respuesta
