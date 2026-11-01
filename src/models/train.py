import os
import sys
import json
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

# Rutas absolutas: el script funciona sin importar desde qué carpeta se ejecute
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
RUTA_DATOS = os.path.join(BASE_DIR, 'data', 'resenas.csv')
RUTA_MODELO = os.path.join(BASE_DIR, 'src', 'models', 'pipeline_modelo.pkl')
RUTA_METRICAS = os.path.join(BASE_DIR, 'src', 'models', 'metricas.json')

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

def construir_pipeline(preprocesador):
    """Pipeline completo: limpieza NLP (Keny) -> TF-IDF -> Regresión Logística."""
    return Pipeline([
        ('vectorizer', TfidfVectorizer(preprocessor=preprocesador.aplicar_lematizacion)),
        ('classifier', LogisticRegression(random_state=42, max_iter=1000))
    ])

def optimizar_hiperparametros_pipeline(X_train, y_train, preprocesador):
    """Ajusta hiperparámetros del Pipeline usando GridSearchCV con 5-Fold CV."""
    print("⚙️ Ejecutando GridSearchCV para Regresión Logística...")

    pipeline = construir_pipeline(preprocesador)

    param_grid = {
        'vectorizer__preprocessor': [preprocesador.aplicar_stemming, preprocesador.aplicar_lematizacion],
        'vectorizer__ngram_range': [(1, 1), (1, 2)],
        'vectorizer__min_df': [1, 2],
        'vectorizer__max_df': [0.9, 1.0],
        'classifier__C': [0.1, 1.0, 10.0],
        'classifier__solver': ['lbfgs', 'liblinear']
    }

    grid_search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        cv=5,
        scoring='f1_weighted',
        n_jobs=-1,
        verbose=1
    )

    # Se pasa el texto crudo: el propio Pipeline aplica la limpieza de Keny
    grid_search.fit(X_train, y_train)

    mejores_params = dict(grid_search.best_params_)
    mejores_params['vectorizer__preprocessor'] = mejores_params['vectorizer__preprocessor'].__name__
    print(f"✅ Mejores Hiperparámetros: {mejores_params}")
    print(f"✅ Mejor F1-Score en CV: {grid_search.best_score_:.4f}")
    return grid_search.best_estimator_, mejores_params, grid_search.best_score_

def evaluar_y_exportar(modelo_optimo, mejores_params, mejor_score_cv, df_comparacion, X_test, y_test,
                       ruta_modelo=RUTA_MODELO, ruta_metricas=RUTA_METRICAS):
    """Evalúa en el conjunto de test retenido y exporta el .pkl y las métricas en JSON."""
    y_pred = modelo_optimo.predict(X_test)

    print("\n📈 REPORTE DE EVALUACIÓN EN TEST:")
    print(classification_report(y_test, y_pred, target_names=['Negativo', 'Positivo']))

    matriz = confusion_matrix(y_test, y_pred)
    print("🧮 MATRIZ DE CONFUSIÓN:")
    print(pd.DataFrame(matriz, index=['Real Negativo', 'Real Positivo'],
                       columns=['Pred. Negativo', 'Pred. Positivo']))

    os.makedirs(os.path.dirname(ruta_modelo), exist_ok=True)
    joblib.dump(modelo_optimo, ruta_modelo)
    print(f"\n💾 Modelo exportado exitosamente en: '{ruta_modelo}'")

    metricas = {
        "modelo": "Regresión Logística + TF-IDF",
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "f1_weighted": round(f1_score(y_test, y_pred, average='weighted'), 4),
        "f1_cv": round(mejor_score_cv, 4),
        "mejores_hiperparametros": {k: str(v) for k, v in mejores_params.items()},
        "matriz_confusion": matriz.tolist(),
        "muestras_test": len(y_test),
        "comparacion_experimentos": df_comparacion.to_dict(orient='records')
    }
    with open(ruta_metricas, 'w', encoding='utf-8') as f:
        json.dump(metricas, f, ensure_ascii=False, indent=2)
    print(f"💾 Métricas exportadas en: '{ruta_metricas}'")

def main():
    X_train, X_test, y_train, y_test = preparar_datasets(RUTA_DATOS)

    preprocesador = NLPPreprocessor()

    # 1. Comparación de experimentos
    df_comparacion = evaluar_comparaciones_experimentos(X_train, X_test, y_train, y_test, preprocesador)

    # 2. Búsqueda de hiperparámetros
    modelo_final, mejores_params, mejor_score_cv = optimizar_hiperparametros_pipeline(X_train, y_train, preprocesador)

    # 3. Evaluación final y exportación
    evaluar_y_exportar(modelo_final, mejores_params, mejor_score_cv, df_comparacion, X_test, y_test)

    # 4. Prueba rápida con texto crudo (así lo usará la API del Integrante 3)
    ejemplo = "El hotel estaba sucio y NO lo recomiendo para nada"
    prob = modelo_final.predict_proba([ejemplo])[0]
    print(f"\n🔎 Prueba: '{ejemplo}' -> Negativo {prob[0]:.1%} | Positivo {prob[1]:.1%}")

if __name__ == "__main__":
    main()
