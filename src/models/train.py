import os
import sys
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, f1_score, confusion_matrix

# Importar el preprocesador del Integrante 1 (Keny)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.nlp.preprocess import NLPPreprocessor

def cargar_datos(path_data: str):
    """Carga y limpia datos nulos iniciales del CSV de reseñas."""
    if not os.path.exists(path_data):
        raise FileNotFoundError(f"No se encontró el archivo de datos en: {path_data}")
    df = pd.read_csv(path_data)
    df = df.dropna(subset=['texto', 'sentimiento'])
    return df['texto'], df['sentimiento']

if __name__ == "__main__":
    print("🚀 Módulo de modelado e integración inicializado correctamente.")
