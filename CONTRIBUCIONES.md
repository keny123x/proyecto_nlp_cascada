# 📝 Registro de Contribuciones del Equipo

De acuerdo con el historial de commits y las asignaciones del proyecto:

| Integrante | Rol / Responsabilidad | Estado |
| :--- | :--- | :--- |
| **Keny** | Integrante 1: Responsable de Datos y NLP (Preprocesamiento, EDA) | Completado |
| **Nicolás** | Integrante 2: Responsable de Modelado y Pipeline (GridSearchCV) | Completado |
| **KAO** | Integrante 3: Responsable de Backend (FastAPI API REST) | Pendiente |
| **Angela** | Integrante 4: Responsable de Frontend (Interfaz Web / Opinómetro) | Pendiente |

## Resumen de entregables de Nicolás (Integrante 2)
- Script `src/models/train.py` con el flujo de entrenamiento reproducible (`random_state=42`).
- Comparación cuantitativa: Unigramas vs. Bigramas y Regresión Logística vs. Naive Bayes.
- Pipeline completo (limpieza NLP + TF-IDF + Regresión Logística) optimizado con `GridSearchCV` (5-Fold CV).
- Artefactos para la API: `src/models/pipeline_modelo.pkl` y `src/models/metricas.json`.
- `requirements.txt` con las versiones de las bibliotecas.
- Corrección del dataset (`data/resenas.csv` y `descargar_datos.py`): reseñas reales de hoteles (Rest-Mex 2025) en lugar de datos sintéticos.
