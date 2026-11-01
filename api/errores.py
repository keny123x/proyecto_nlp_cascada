from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.config import MAX_CARACTERES

# Traducción de los errores de Pydantic más comunes
MENSAJES = {
    'missing': "Este campo es obligatorio.",
    'string_type': "El valor debe ser un texto.",
    'string_too_long': f"La reseña no puede superar los {MAX_CARACTERES} caracteres.",
    'too_short': "La lista debe tener al menos una reseña.",
    'too_long': "La lista tiene demasiadas reseñas.",
    'list_type': "Se esperaba una lista de textos.",
    'json_invalid': "El cuerpo de la petición no es un JSON válido.",
    'model_attributes_type': "Se esperaba un objeto JSON, por ejemplo {\"texto\": \"...\"}.",
}


def traducir_error(error: dict) -> dict:
    """Convierte un error de validación de FastAPI en un mensaje simple en español."""
    campo = ".".join(str(p) for p in error.get('loc', []) if p != 'body') or 'body'
    if error.get('type') == 'json_invalid':
        campo = 'body'
    if error.get('type') == 'value_error':
        # Mensajes propios de los validadores (ej: "La reseña no puede estar vacía.")
        mensaje = str(error.get('ctx', {}).get('error', error.get('msg')))
    else:
        mensaje = MENSAJES.get(error.get('type'), error.get('msg'))
    return {"campo": campo, "mensaje": mensaje}


def registrar_manejadores(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def error_validacion(request: Request, exc: RequestValidationError):
        detalles = [traducir_error(e) for e in exc.errors()]
        return JSONResponse(
            status_code=422,
            content={"error": "Datos inválidos", "detalles": detalles},
        )

    @app.exception_handler(Exception)
    async def error_interno(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"error": "Error interno del servidor", "detalles": [{"campo": None, "mensaje": str(exc)}]},
        )
