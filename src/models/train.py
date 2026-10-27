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

def preparar_datasets(path_csv: str, test_size: float = 0.2, random_state: int = 42):
    """Carga datos y realiza el train/test split estratificado."""
    X, y = cargar_datos(path_csv)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )
    print(f"📊 Datos cargados: {len(X)} muestras totales.")
    print(f"   - Entrenamiento: {len(X_train)} | Prueba: {len(X_test)}")
    return X_train, X_test, y_train, y_test

def evaluar_comparaciones_experimentos(X_train, X_test, y_train, y_test, preprocesador):
    """
    Compara de forma transparente:
    - Unigramas vs. Bigramas
    - Regresión Logística vs. Naive Bayes
    """
    print("\n" + "="*65)
    print("📊 COMPARACIÓN DE EXPERIMENTOS (N-GRAMAS Y MODELOS)")
    print("="*65)

    # Limpieza previa con el lematizador de Keny
    X_train_clean = [preprocesador.aplicar_lematizacion(texto) for texto in X_train]
    X_test_clean = [preprocesador.aplicar_lematizacion(texto) for texto in X_test]

    experimentos = [
        {"nombre": "Regresión Logística (Unigramas)", "ngram": (1, 1), "model": LogisticRegression(random_state=42)},
        {"nombre": "Regresión Logística (Unigramas + Bigramas)", "ngram": (1, 2), "model": LogisticRegression(random_state=42)},
        {"nombre": "Naive Bayes (Unigramas)", "ngram": (1, 1), "model": MultinomialNB()},
        {"nombre": "Naive Bayes (Unigramas + Bigramas)", "ngram": (1, 2), "model": MultinomialNB()}
    ]

    resultados = []

    for exp in experimentos:
        vec = TfidfVectorizer(ngram_range=exp["ngram"], min_df=2)
        X_tr_tfidf = vec.fit_transform(X_train_clean)
        X_te_tfidf = vec.transform(X_test_clean)

        clf = exp["model"]
        clf.fit(X_tr_tfidf, y_train)
        y_pred = clf.predict(X_te_tfidf)

        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')

        resultados.append({
            "Modelo": exp["nombre"],
            "Dim. Vocabulario": X_tr_tfidf.shape[1],
            "Accuracy": round(acc, 4),
            "F1-Score (Weighted)": round(f1, 4)
        })

    df_res = pd.DataFrame(resultados)
    print(df_res.to_string(index=False))
    print("="*65 + "\n")
    return df_res

if __name__ == "__main__":
    print("🚀 Módulo de modelado e integración inicializado correctamente.")
