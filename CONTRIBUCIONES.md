# 📝 Registro de Contribuciones del Equipo

De acuerdo con el historial de commits y las asignaciones del proyecto:

| Integrante | Rol / Responsabilidad | Estado |
| :--- | :--- | :--- |
| **Keny** | Integrante 1: Responsable de Datos y NLP (Preprocesamiento, EDA) | Completado |
| **Nicolás** | Integrante 2: Responsable de Modelado y Pipeline (GridSearchCV) | Completado |
| **KAO** | Integrante 3: Responsable de Backend (FastAPI API REST) | Integrado en la rama local de trabajo |
| **Angela** | Integrante 4: Responsable de Frontend (Interfaz Web / Opinómetro) | Implementado localmente con asistencia de IA; pendiente de revisión y commits |

## Resumen de entregables de Nicolás (Integrante 2)
- Script `src/models/train.py` con el flujo de entrenamiento reproducible (`random_state=42`).
- Comparación cuantitativa: Unigramas vs. Bigramas y Regresión Logística vs. Naive Bayes.
- Pipeline completo (limpieza NLP + TF-IDF + Regresión Logística) optimizado con `GridSearchCV` (5-Fold CV).
- Artefactos para la API: `src/models/pipeline_modelo.pkl` y `src/models/metricas.json`.
- `requirements.txt` con las versiones de las bibliotecas.
- Corrección del dataset (`data/resenas.csv` y `descargar_datos.py`): reseñas reales de hoteles (Rest-Mex 2025) en lugar de datos sintéticos.

## Frontend preparado para revisión de Angela

- Interfaz original de Opinómetro con portada animada y adaptación móvil.
- Conexión a predicción individual, lotes, estado y métricas mediante Fetch API.
- Laboratorio de etapas NLP con reproducción, stop words, negaciones y raíces.
- Matriz de confusión, experimentos y configuración del modelo.
- Validaciones, errores de red, modo simulado y controles de accesibilidad.
- Documentación de inicio y guía para la demostración.

Estos cambios se prepararon con asistencia de Codex. La asignación del rol no
sustituye la autoría registrada en Git: Angela debe revisar y comprender el código
antes de registrar sus contribuciones. No se ha creado un commit que atribuya
estos archivos a un integrante ni se ha publicado el frontend en la rama principal.

## Ajuste de integración NLP pendiente de registrar

Se evita descargar `stopwords` al importar si el corpus ya está instalado.
Este ajuste no cambia la limpieza; se verificó la coincidencia API/modelo en
las 200 reseñas de prueba. Debe revisarse y explicarse como cualquier aporte NLP.
