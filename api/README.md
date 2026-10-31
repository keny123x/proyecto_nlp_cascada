# ⚙️ API REST de Sentimiento (Backend)

**Integrante 3 – Responsable de Backend:** Luis Angel (KAO)

Servidor en **FastAPI** que carga el modelo entrenado por el Integrante 2 (`src/models/pipeline_modelo.pkl`) y clasifica reseñas de productos, hoteles o restaurantes en **Positivo** o **Negativo**. También devuelve el paso a paso del NLP para que el Frontend lo muestre en pantalla.

## 🔗 Cómo se conecta con el resto del equipo

```
Keny (src/nlp/preprocess.py) ──► Nicolás (pipeline_modelo.pkl) ──► API (api/main.py) ──► Angela (frontend/)
        limpieza                       TF-IDF + modelo              joblib.load + rutas       fetch()
```

- El `.pkl` guarda referencias a `NLPPreprocessor` de Keny, por eso la API agrega la raíz del repo al `sys.path`.
- **Modo simulado:** si todavía no existe `pipeline_modelo.pkl`, `/predict` responde siempre *Positivo 90%*. Así el Frontend puede trabajar sin esperar al modelo. Cuando el archivo aparece, la API lo usa automáticamente.

## 🚀 Cómo levantar el servidor

Desde la raíz del repositorio:

```bash
./api/run.sh instalar   # instala las dependencias (una sola vez)
./api/run.sh            # inicia el servidor en http://127.0.0.1:8000
./api/run.sh test       # corre las pruebas
```

O directamente con uvicorn:

```bash
pip3 install -r api/requirements.txt
uvicorn api.main:app --reload
```

La documentación interactiva queda en **http://127.0.0.1:8000/docs**.

> **Mac:** si NLTK falla al descargar las stop words con `CERTIFICATE_VERIFY_FAILED`, ejecuta una vez `open "/Applications/Python 3.14/Install Certificates.command"`.

## 📡 Rutas

| Método | Ruta | Qué hace |
|---|---|---|
| `POST` | `/predict` | Clasifica una reseña y devuelve la probabilidad y el paso a paso del NLP |
| `POST` | `/predict/lote` | Clasifica hasta 50 reseñas en una sola petición |
| `GET` | `/metrics` | Precisión y métricas del modelo (de `metricas.json`) |
| `GET` | `/status` | Estado del servidor y si el modelo real está cargado |
| `GET` | `/ejemplos` | Reseñas de demostración (filtro opcional `?categoria=hotel`) |

### `POST /predict`

**Petición**
```json
{ "texto": "El hotel estaba sucio y NO lo recomiendo para nada" }
```

**Respuesta** (con el modelo real)
```json
{
  "sentimiento": "Negativo",
  "probabilidad": 0.9866,
  "porcentaje": "98.7%",
  "probabilidades": { "Negativo": 0.9866, "Positivo": 0.0134 },
  "modo": "real",
  "pasos": {
    "texto_original": "El hotel estaba sucio y NO lo recomiendo para nada",
    "paso1_normalizado": "el hotel estaba sucio y no lo recomiendo para nada",
    "paso2_tokens": ["el", "hotel", "estaba", "sucio", "y", "no", "lo", "recomiendo", "para", "nada"],
    "paso3_sin_stopwords": ["hotel", "sucio", "no", "recomiendo", "nada"],
    "paso3_stopwords_eliminadas": ["el", "estaba", "y", "lo", "para"],
    "paso3_negaciones_conservadas": ["no", "nada"],
    "paso4_stemming": ["hotel", "suci", "no", "recom", "nad"],
    "paso5_resultado": "Negativo - 98.7% de probabilidad"
  }
}
```

Los campos de `pasos` son exactamente los 5 pasos que pide el Requisito 5.2:

| Paso | Campo | Qué muestra |
|---|---|---|
| 1 | `paso1_normalizado` | Minúsculas, sin tildes, signos, números ni URLs |
| 2 | `paso2_tokens` | El texto separado en palabras |
| 3 | `paso3_sin_stopwords` | Sin conectores; `paso3_negaciones_conservadas` muestra que el "no" se mantiene |
| 4 | `paso4_stemming` | Raíces de las palabras (la técnica que ganó en el GridSearchCV) |
| 5 | `paso5_resultado` | Veredicto con su porcentaje |

### `POST /predict/lote`

```json
{ "textos": ["La comida estuvo deliciosa", "El servicio fue pésimo"] }
```
Devuelve `total`, `positivos`, `negativos` y `resultados` (una respuesta de `/predict` por cada reseña).

### `GET /metrics`

```json
{ "modo": "real", "modelo": "Regresión Logística + TF-IDF", "accuracy": 0.935, "f1_weighted": 0.935, "...": "..." }
```

### `GET /status`

```json
{ "estado": "ok", "modelo_cargado": true, "modo": "real", "activo_desde": "2026-10-30T23:54:55" }
```

## 🛡️ Validaciones y errores

La API rechaza con **422** las reseñas vacías, las que son solo espacios, las que no tienen ninguna letra y las que superan 2000 caracteres. Todos los errores tienen el mismo formato y están en español:

```json
{
  "error": "Datos inválidos",
  "detalles": [{ "campo": "texto", "mensaje": "La reseña no puede estar vacía." }]
}
```

## 🌐 Ejemplo para el Frontend (JavaScript)

```js
const respuesta = await fetch("http://127.0.0.1:8000/predict", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ texto: "El hotel estaba sucio" })
});
const datos = await respuesta.json();

if (!respuesta.ok) {
  alert(datos.detalles[0].mensaje);         // ej: "La reseña no puede estar vacía."
} else {
  caja.style.background = datos.sentimiento === "Positivo" ? "green" : "red";
  caja.textContent = datos.pasos.paso5_resultado;
}
```

## ⚙️ Configuración

Copia `api/.env.example` como `api/.env` para cambiar:

| Variable | Por defecto | Para qué sirve |
|---|---|---|
| `PUERTO` | `8000` | Puerto del servidor (lo usa `run.sh`) |
| `RUTA_MODELO` | `src/models/pipeline_modelo.pkl` | Modelo a cargar |
| `RUTA_METRICAS` | `src/models/metricas.json` | Métricas a devolver |
| `ORIGENES_PERMITIDOS` | `*` | Orígenes que acepta CORS, separados por coma |
| `MAX_CARACTERES` | `2000` | Largo máximo de una reseña |
| `LOG_ARCHIVO` | *(vacío)* | Archivo donde guardar el registro de peticiones |

## 📁 Archivos

| Archivo | Contenido |
|---|---|
| `main.py` | Aplicación FastAPI, carga del modelo y rutas |
| `schemas.py` | Modelos de entrada y respuesta (Pydantic) |
| `errores.py` | Manejo de errores en español |
| `registro.py` | Logging de peticiones |
| `config.py` | Variables de configuración |
| `ejemplos.py` | Reseñas de demostración |
| `test_main.py` | Pruebas con pytest |
| `run.sh` | Script para levantar el servidor |
