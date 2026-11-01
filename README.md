# Opinómetro

Aplicación web para clasificar el sentimiento de reseñas de hoteles en español
y explorar el recorrido NLP. Proyecto de Tópicos y Programación Avanzada.

## Instalación en Windows

Requisito: Python 3.12 y conexión para instalar dependencias y stop words la
primera vez. Ejecutar desde la raíz del repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r api/requirements.txt
$env:NLTK_DATA = Join-Path (Get-Location) '.venv\nltk_data'
.\.venv\Scripts\python.exe -c "import nltk,os; nltk.download('stopwords', download_dir=os.environ['NLTK_DATA'], raise_on_error=True)"
```

El modelo y las métricas se incluyen en `src/models/`. No hace falta reentrenar
para usar la aplicación. El frontend no requiere Node.js ni instalación de npm.

## Iniciar la aplicación

Abrir dos terminales PowerShell en la raíz. Mantener ambas abiertas:

```powershell
# Terminal 1: backend
.\iniciar.ps1 api
```

```powershell
# Terminal 2: frontend
.\iniciar.ps1 frontend
```

Abrir http://127.0.0.1:5173. FastAPI: http://127.0.0.1:8000/docs.
Ctrl+C detiene cada servidor.

Si PowerShell no permite ejecutar scripts, usar estos comandos sin modificar
su política de ejecución:

```powershell
# Terminal 1
$env:NLTK_DATA = Join-Path (Get-Location) '.venv\nltk_data'
.\.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000
# Terminal 2
.\.venv\Scripts\python.exe -m http.server 5173 --bind 127.0.0.1 --directory frontend
```

## Funciones

- Predicción individual con probabilidades positiva y negativa.
- Lotes de hasta 50 reseñas: una por línea, hasta 2000 caracteres cada una.
- Detalle: normalización, tokens, stop words y pares palabra/raíz.
- Reproducción visual del NLP; no representa procesamiento en vivo.
- Métricas, matriz de confusión, experimentos y configuración final.
- Teclado, adaptación móvil y opción de pausar el movimiento.
- Ctrl+Enter envía texto. No se guarda historial en el navegador.

## Modelo y datos

Muestra balanceada de 1000 reseñas hoteleras de Rest-Mex 2025; el script
`descargar_datos.py` contiene el origen y preparación. Se usan 800 reseñas para
entrenamiento y 200 para prueba, semilla 42.

Pipeline final: stemming + TF-IDF (unigramas) + Regresión Logística.
Evaluación reproducida: accuracy 0.935, F1 ponderado redondeado 0.935;
matriz `[[92, 8], [5, 95]]` (orden negativo, positivo). Los cuatro experimentos
comparativos usan lematización; la optimización final es separada con GridSearchCV.

El clasificador es binario: no tiene clase neutral ni mide intensidad emocional.
Puede fallar con opiniones mixtas y otros dominios. La probabilidad de una reseña
no es la exactitud general del modelo.

## Pruebas y entrenamiento

```powershell
.\iniciar.ps1 tests
# Opcional: reentrenar y reemplazar los artefactos (puede tardar)
$env:NLTK_DATA = Join-Path (Get-Location) '.venv\nltk_data'
.\.venv\Scripts\python.exe src/models/train.py
```

Reiniciar el backend después de reentrenar: carga el pipeline al arrancar.
Si falta el modelo, las predicciones son simuladas; si faltan las métricas, ese
endpoint devuelve valores de prueba. La interfaz distingue ambos modos.

## Organización

```text
data/                 Dataset
notebooks/            Análisis exploratorio
src/nlp/              Preprocesamiento
src/models/           Entrenamiento, pipeline y métricas
api/                  FastAPI, validación y pruebas
frontend/             HTML, CSS y JavaScript modular
docs/                 Integración y guía de demostración
iniciar.ps1           Inicio y pruebas en Windows
CONTRIBUCIONES.md      Responsabilidades y estado
```

URL del backend: `frontend/src/services/api.js`. Configuración: `api/config.py`.
Si se cambia `MAX_CARACTERES` del backend, ajustar el límite del frontend (2000).
Google Fonts es opcional: sin conexión se usan fuentes locales alternativas.
El modelo no depende de servicios de IA externos.

Ver `docs/guia_demostracion.md` y `frontend/README.md`. El frontend y el ajuste
de descarga de NLTK se desarrollaron con asistencia de IA (Codex); el equipo debe
revisarlos, comprenderlos y declarar ese uso en el informe, según la consigna.
