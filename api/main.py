import os
import re
import sys
import json
import unicodedata
from datetime import datetime

import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

# El .pkl guarda referencias a NLPPreprocessor (Keny), así que src/ debe ser importable
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(BASE_DIR)
from src.nlp.preprocess import NLPPreprocessor

# Rutas por defecto a los archivos que exporta el Integrante 2 (Nicolás)
RUTA_MODELO = os.getenv('RUTA_MODELO', os.path.join(BASE_DIR, 'src', 'models', 'pipeline_modelo.pkl'))
RUTA_METRICAS = os.getenv('RUTA_METRICAS', os.path.join(BASE_DIR, 'src', 'models', 'metricas.json'))

ETIQUETAS = {0: 'Negativo', 1: 'Positivo'}
MAX_CARACTERES = 2000

app = FastAPI(
    title="API de Sentimiento de Reseñas",
    description="Clasifica reseñas de productos, hoteles o restaurantes en Positivo o Negativo.",
    version="1.0.0"
)

# Permite que el Frontend (Integrante 4) llame a la API desde el navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

preprocesador = NLPPreprocessor()
HORA_INICIO = datetime.now()


def cargar_modelo(ruta: str):
    """Carga el pipeline entrenado. Si todavía no existe, la API trabaja en modo simulado."""
    if not os.path.exists(ruta):
        print(f"⚠️ No se encontró el modelo en '{ruta}'. La API responde en modo simulado.")
        return None
    modelo = joblib.load(ruta)
    print(f"✅ Modelo cargado desde '{ruta}'")
    return modelo


modelo = cargar_modelo(RUTA_MODELO)


class ResenaEntrada(BaseModel):
    texto: str = Field(..., max_length=MAX_CARACTERES, examples=["El hotel estaba sucio y NO lo recomiendo para nada"])

    @field_validator('texto')
    @classmethod
    def validar_texto(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("La reseña no puede estar vacía.")
        if not re.search(r'[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]', valor):
            raise ValueError("La reseña debe contener al menos una palabra.")
        return valor


def pasos_nlp(texto: str) -> dict:
    """Reproduce paso a paso la limpieza de Keny para que el Frontend la muestre en pantalla."""
    # Paso 1: minúsculas, sin URLs, sin tildes, sin signos ni números
    normalizado = texto.lower()
    normalizado = re.sub(r'https?://\S+|www\.\S+', '', normalizado)
    normalizado = "".join(c for c in unicodedata.normalize('NFD', normalizado) if unicodedata.category(c) != 'Mn')
    normalizado = re.sub(r'[^a-z\s]', '', normalizado)
    normalizado = " ".join(normalizado.split())

    # Paso 2: tokens
    tokens = normalizado.split()

    # Paso 3: stop words eliminadas (las negaciones se conservan)
    sin_stopwords = [w for w in tokens if w not in preprocesador.stop_words]
    eliminadas = [w for w in tokens if w in preprocesador.stop_words]
    negaciones = [w for w in sin_stopwords if w in {'no', 'ni', 'tampoco', 'nunca', 'jamas', 'nada'}]

    # Paso 4: stemming (la técnica que ganó en el GridSearchCV)
    raices = [preprocesador.stemmer.stem(w) for w in sin_stopwords]

    return {
        "texto_original": texto,
        "paso1_normalizado": normalizado,
        "paso2_tokens": tokens,
        "paso3_sin_stopwords": sin_stopwords,
        "paso3_stopwords_eliminadas": eliminadas,
        "paso3_negaciones_conservadas": negaciones,
        "paso4_stemming": raices,
    }


@app.get("/status")
def status():
    """Indica si el servidor está vivo y si el modelo real está cargado."""
    return {
        "estado": "ok",
        "modelo_cargado": modelo is not None,
        "modo": "real" if modelo is not None else "simulado",
        "activo_desde": HORA_INICIO.isoformat(timespec='seconds'),
    }


@app.get("/metrics")
def metrics():
    """Devuelve la precisión del modelo calculada por el Integrante 2 en el conjunto de prueba."""
    if not os.path.exists(RUTA_METRICAS):
        return {
            "modo": "simulado",
            "modelo": "Regresión Logística + TF-IDF",
            "accuracy": 0.90,
            "mensaje": "Métricas de prueba: todavía no existe metricas.json."
        }
    with open(RUTA_METRICAS, encoding='utf-8') as f:
        metricas = json.load(f)
    metricas["modo"] = "real"
    return metricas


@app.post("/predict")
def predict(resena: ResenaEntrada):
    """Recibe la reseña, calcula la probabilidad de cada clase y devuelve el veredicto."""
    pasos = pasos_nlp(resena.texto)

    if modelo is None:
        # Respuesta fija mientras no exista pipeline_modelo.pkl
        probabilidades = {"Negativo": 0.10, "Positivo": 0.90}
    else:
        # El pipeline recibe el texto crudo: él mismo aplica la limpieza y el TF-IDF
        proba = modelo.predict_proba([resena.texto])[0]
        clases = modelo.classes_
        probabilidades = {ETIQUETAS[int(c)]: round(float(p), 4) for c, p in zip(clases, proba)}

    sentimiento = max(probabilidades, key=probabilidades.get)
    probabilidad = probabilidades[sentimiento]

    return {
        "sentimiento": sentimiento,
        "probabilidad": probabilidad,
        "porcentaje": f"{probabilidad * 100:.1f}%",
        "probabilidades": probabilidades,
        "modo": "real" if modelo is not None else "simulado",
        "pasos": {**pasos, "paso5_resultado": f"{sentimiento} - {probabilidad * 100:.1f}% de probabilidad"},
    }
