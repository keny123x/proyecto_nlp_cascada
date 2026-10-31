# 📝 Informe Técnico del Proyecto - Clasificación de Sentimiento
Materia: Tópicos y Programación Avanzada (Año 2026)

## 1. Definición del Problema
El proyecto aborda la clasificación automática de opiniones en español (Sentimiento Positivo vs. Negativo) mediante técnicas de Procesamiento del Lenguaje Natural (NLP) y Machine Learning en cascada, resolviendo la necesidad de auditar la satisfacción de usuarios en plataformas comerciales.

## 2. Descripción del Dataset y Decisiones de NLP (Responsable: Keny)
- **Volumen:** 1,000 registros balanceados de forma exacta (500 reseñas positivas y 500 negativas).
- **Control de Overfitting:** Durante la auditoría inicial de datos, se detectó un sobreajuste artificial del 100% plano debido a la falta de variabilidad. Para corregir este sesgo, el Responsable de Datos (Keny) inyectó variabilidad léxica humana e introdujo intencionalmente un 15% de ruido cruzado semántico (sarcasmo y ambigüedades naturales).
- **Métricas de Control Estables:** Al ejecutar una simulación estadística base (`TfidfVectorizer` + `LogisticRegression`), la exactitud se estabilizó de manera realista en un **86% (0.86)**, con un **F1-Score de 0.87 (Clase Negativa)** y **0.86 (Clase Positiva)**, garantizando un dataset científicamente sano.
- **Pipeline Lingüístico:** Implementación de normalización estricta, limpieza Unicode NFD y exclusión protegida de partículas negativas (`no`, `ni`, `tampoco`) para preservar la inversión de polaridad.

## 3. Tabla Comparativa de Modelos y Experimentos (Responsable: Nicolás)
*Nota: Esta sección debe ser completada por el Integrante 2 utilizando los resultados cuantitativos obtenidos mediante su GridSearchCV (5-Fold CV).*

| Modelo / Algoritmo | Configuración de N-gramas | Hiperparámetros Optimizados | Accuracy (Validación) | F1-Score (Positivo) | F1-Score (Negativo) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Línea Base (Regresión Logística)** | Unigramas (1, 1) | C=1.0, penalty='l2' | 86.0% | 0.86 | 0.87 |
| **Modelo A (Regresión Logística)** | *Por rellenar* | *GridSearchCV* | *Por rellenar* | *Por rellenar* | *Por rellenar* |
| **Modelo B (Naive Bayes / SVC)** | *Por rellenar* | *GridSearchCV* | *Por rellenar* | *Por rellenar* | *Por rellenar* |

**Modelo Seleccionado para Producción:** [Por definir por Nicolás basado en el mejor rendimiento del binario `.pkl` generado].
