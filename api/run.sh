#!/usr/bin/env bash
# Levanta la API o corre sus pruebas desde cualquier carpeta.
#   ./api/run.sh          -> inicia el servidor en modo desarrollo
#   ./api/run.sh test     -> corre las pruebas con pytest
#   ./api/run.sh instalar -> instala las dependencias de la API
set -e

DIR_API="$(cd "$(dirname "$0")" && pwd)"
RAIZ="$(dirname "$DIR_API")"
cd "$RAIZ"

# Carga las variables de api/.env si existe
if [ -f "$DIR_API/.env" ]; then
    set -a
    source "$DIR_API/.env"
    set +a
fi
PUERTO="${PUERTO:-8000}"

case "${1:-servidor}" in
    servidor)
        echo "🚀 API en http://127.0.0.1:$PUERTO  (documentación en /docs)"
        python3 -m uvicorn api.main:app --reload --port "$PUERTO"
        ;;
    test)
        python3 -m pytest api/test_main.py -v
        ;;
    instalar)
        python3 -m pip install -r api/requirements.txt
        ;;
    *)
        echo "Uso: ./api/run.sh [servidor|test|instalar]"
        exit 1
        ;;
esac
