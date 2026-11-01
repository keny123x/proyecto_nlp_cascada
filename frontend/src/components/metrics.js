import {getMetrics} from '../services/api.js';
import {node, percent, table} from './dom.js';
export function initMetrics() {
  const grid = document.querySelector('.metric-grid');
  const note = document.querySelector('.metrics-note');
  note.setAttribute('role', 'status');
  grid.before(note);
  const details = node('div', '', 'metrics-details'); grid.after(details);
  const retry = node('button', 'Actualizar métricas ↻', 'row-detail'); note.after(retry);
  async function load() {
    retry.disabled = true; grid.replaceChildren(); details.replaceChildren(); note.textContent = 'Consultando métricas de la API…';
    try {
      const data = await getMetrics();
      document.querySelector('#metricas .section-heading > p').textContent = `${data.modelo}. Entrenado con reseñas de hoteles en español.`;
      const cards = [
        ['EXACTITUD EN PRUEBA',percent(data.accuracy),'Proporción de predicciones correctas.'],
        ['F1 PONDERADO',Number.isFinite(data.f1_weighted) ? data.f1_weighted.toLocaleString('es', {maximumFractionDigits:3}) : 'No disponible','Combina precisión y recall, ponderando cada clase.'],
        ['RESEÑAS DE PRUEBA',Number.isFinite(data.muestras_test) ? data.muestras_test.toLocaleString('es') : 'No disponible','Conjunto reservado para la evaluación final.'],
      ];
      cards.forEach(([label,value,description]) => { const card = node('article'); card.append(node('span',label,'metric-label'),node('strong',value),node('p',description)); grid.append(card); });
      note.textContent = data.modo === 'real' ? 'Métricas del artefacto de evaluación, consultadas en /metrics. No se recalculan con las reseñas que ingresas.' : `MÉTRICAS SIMULADAS. ${data.mensaje || 'No hay un artefacto de evaluación disponible.'}`;
      note.classList.toggle('negative-text',data.modo !== 'real');
      const matrix = data.matriz_confusion;
      const matrixCard = node('article', '', 'metric-detail-card'); matrixCard.append(node('h3','¿Dónde acierta y dónde se equivoca?'));
      if (Array.isArray(matrix) && matrix.length === 2 && matrix.every((row) => Array.isArray(row) && row.length === 2 && row.every(Number.isFinite))) {
        matrixCard.append(table(['Clase real ↓ / Predicha →','Negativo','Positivo'],[
          ['Negativo',matrix[0][0],matrix[0][1]],['Positivo',matrix[1][0],matrix[1][1]],
        ],'Matriz de confusión · conteos de reseñas'));
        matrixCard.append(node('p',`Aciertos: ${matrix[0][0] + matrix[1][1]}. Errores: ${matrix[0][1] + matrix[1][0]}. Filas = clase real; columnas = clase predicha.`));
      } else matrixCard.append(node('p','La API no proporciona una matriz de confusión.'));
      details.append(matrixCard);
      const comparison = node('article','','metric-detail-card'); comparison.append(node('h3','Cuatro formas de leer una reseña.'));
      if (Array.isArray(data.comparacion_experimentos) && data.comparacion_experimentos.length) {
        comparison.append(table(['Experimento','Vocabulario','Exactitud','F1 ponderado'], data.comparacion_experimentos.map((row) => [row.Modelo,row['Dim. Vocabulario'] ?? 'No disponible',percent(row.Accuracy),Number.isFinite(row['F1-Score (Weighted)']) ? row['F1-Score (Weighted)'].toLocaleString('es',{maximumFractionDigits:3}) : 'No disponible']), 'Comparación de experimentos con lematización'));
        comparison.append(node('p','Estos experimentos usan lematización. El modelo final se optimizó por separado mediante validación cruzada; sus resultados no son una fila equivalente de esta tabla.'));
      } else comparison.append(node('p','La API no proporciona comparación de experimentos.'));
      details.append(comparison);
      if (data.mejores_hiperparametros) {
        const params = node('details','','model-params'); params.append(node('summary','Explorar configuración del modelo final'));
        params.append(table(['Parámetro','Valor'],Object.entries(data.mejores_hiperparametros),'Hiperparámetros seleccionados'));
        params.append(node('p',`F1 ponderado en validación cruzada: ${Number.isFinite(data.f1_cv) ? data.f1_cv.toLocaleString('es',{maximumFractionDigits:4}) : 'No disponible'}.`)); details.append(params);
      }
    } catch (error) { note.textContent = `No se pudieron cargar las métricas. ${error.message}`; }
    finally { retry.disabled = false; }
  }
  retry.addEventListener('click',load); load();
}
