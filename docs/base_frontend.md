# Base de integración para Opinómetro

## Alcance

La rama `codex/integracion-frontend-base` reúne el backend de `anghy` y el
modelado de `origin/ramaNico` mediante merge, conservando sus commits.
El dominio de entrenamiento es reseñas de hoteles en español (Rest-Mex 2025).
Las categorías de ejemplos de la API no implican evaluación en otros dominios.

## Ejecución en Windows

Desde la raíz, con Python 3.12:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r api/requirements.txt
$env:NLTK_DATA = Join-Path (Get-Location) '.venv\nltk_data'
.\.venv\Scripts\python.exe -c "import nltk,os; nltk.download('stopwords', download_dir=os.environ['NLTK_DATA'], raise_on_error=True)"
.\.venv\Scripts\python.exe -m pytest api/test_main.py -q
.\.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

NLTK necesita el corpus `stopwords`; el preprocesador intenta descargarlo solo
si no está instalado. La primera ejecución puede requerir conexión a internet.
Definir `NLTK_DATA` también en cada terminal nueva antes de iniciar el servidor.

## Contrato para la interfaz

- `GET /status`: disponibilidad, `modelo_cargado` y `modo`.
- `POST /predict`: recibe `{ "texto": "..." }`; devuelve sentimiento,
  probabilidades de ambas clases, modo y etapas NLP en `pasos`.
- `GET /ejemplos?categoria=hotel`: ejemplos hoteleros.
- `POST /predict/lote`: recibe `{ "textos": ["..."] }`, entre 1 y 50 reseñas.
- `GET /metrics`: accuracy, F1 ponderado, F1 de validación cruzada,
  matriz de confusión, tamaño del test, hiperparámetros y experimentos.
- Límite predeterminado: 2000 caracteres por reseña, configurable en el servidor.
- Errores: `error` y lista `detalles` con `campo` y `mensaje`.

El modo simulado debe identificarse visiblemente. Las métricas ausentes no se
convierten en ceros. La interfaz no realiza otra implementación de la limpieza.
La API actual no expone pesos TF-IDF ni atribuciones de la predicción.

## Métricas registradas

El JSON entregado registra accuracy 0.935, F1 ponderado 0.935 y 200 muestras de
prueba; matriz `[[92, 8], [5, 95]]`, orden negativo/positivo según el script.
La configuración elegida usa stemming y unigramas. La comparación de cuatro
experimentos usa lematización: debe distinguirse de la búsqueda final optimizada.
Leer el JSON no equivale a reproducir estas métricas con el modelo.

## Verificación realizada (1 de noviembre de 2026)

- Referencias de GitHub actualizadas con `git fetch origin`.
- Dependencias instaladas en `.venv`; `pip check` sin incompatibilidades.
- 22 pruebas existentes del backend aprobadas con el modelo real disponible.
  Aviso no bloqueante: Starlette anuncia deprecación de su integración con httpx.
- Evaluación del modelo guardado sobre el split estratificado del script,
  semilla 42: accuracy 0.935, F1 ponderado 0.9349853717086344,
  matriz `[[92, 8], [5, 95]]`. Coincide con el JSON al redondear.
- En las 200 reseñas de test, concatenar las raíces de la API coincide con
  la salida del preprocesador guardado en el modelo: cero diferencias.
- No se reentrenó ni se reemplazó el modelo. No se publicó la rama.

Las pruebas requirieron ejecución fuera del aislamiento de herramientas:
el aislamiento bloqueaba la creación del socket local de asyncio en Windows.
Esto no requirió cambios en el backend.

## Bloques de frontend

1. Boceto, identidad visual y componentes.
2. Análisis individual conectado: validaciones, carga, errores y resultados.
3. Laboratorio NLP: normalización, tokens, stop words y raíces.
4. Métricas y lotes con los campos disponibles.
5. Portada animada, accesibilidad, móvil y documentación.

Verificar cada bloque antes de incorporar el siguiente.
