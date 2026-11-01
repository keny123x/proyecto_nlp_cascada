import {node, percent, table} from './dom.js';
let host;
export function initBatch() {
  host = node('section', '', 'batch-results'); host.id = 'batch-results'; host.hidden = true;
  host.setAttribute('aria-label', 'Resultados de varias reseñas');
  document.querySelector('.analysis-grid').after(host);
  const count = node('p', '0 / 50 reseñas', 'batch-help'); count.id = 'batch-count';
  document.querySelector('#batch').after(count);
  document.querySelector('.batch-help:last-child').textContent = 'Hasta 50 reseñas, una por línea y hasta 2000 caracteres cada una. Se omiten las líneas en blanco.';
  document.querySelector('#batch').addEventListener('input', () => {
    const total = batchTexts().length;
    count.textContent = `${total} / 50 reseñas`;
    document.querySelector('#batch').removeAttribute('aria-invalid');
    if (host.childElementCount) {
      document.querySelector('#form-message').textContent = 'El lote cambió. Los resultados corresponden al último lote enviado.';
    }
  });
}
export function batchTexts() { return document.querySelector('#batch').value.split(/\r?\n/).map((text) => text.trim()).filter(Boolean); }
export function validateBatch(texts) {
  if (!texts.length) return 'Escribe al menos una reseña, una por línea.';
  if (texts.length > 50) return 'Puedes analizar como máximo 50 reseñas por lote.';
  const index = texts.findIndex((text) => text.length > 2000 || !/[a-záéíóúñü]/i.test(text));
  if (index >= 0) return `Reseña ${index + 1}: debe contener al menos una palabra y no superar los 2000 caracteres.`;
  return '';
}
export function resetBatch() { host.replaceChildren(); document.querySelector('#batch-count').textContent = '0 / 50 reseñas'; }
export function renderBatch(data, onSelect) {
  host.replaceChildren(); host.hidden = false;
  host.append(node('h3', 'Un vistazo a todas las opiniones.'), node('p', `Total: ${data.total} · Positivas: ${data.positivos} · Negativas: ${data.negativos}`, 'batch-summary'));
  if (data.resultados.some((result) => result.modo !== 'real')) host.append(node('p', 'Modo simulado: las clasificaciones de prueba no provienen del modelo entrenado.', 'lab-stale'));
  const status = node('p', 'Selecciona una reseña para explorar su resultado y sus pasos NLP.', 'batch-selection'); status.setAttribute('role','status');
  host.append(status);
  const rows = data.resultados.map((result, index) => {
    const button = node('button', 'Explorar ↗', 'row-detail'); button.setAttribute('aria-label', `Explorar reseña ${index + 1}`); button.setAttribute('aria-pressed','false');
    button.addEventListener('click', () => {
      host.querySelectorAll('button').forEach((other) => other.setAttribute('aria-pressed', String(other === button)));
      status.textContent = `Mostrando reseña ${index + 1}: «${result.pasos.texto_original}»`;
      onSelect(result);
    });
    const sentiment = node('span', result.sentimiento, result.sentimiento === 'Positivo' ? 'positive-text' : 'negative-text');
    return [index + 1, result.pasos.texto_original, sentiment, percent(result.probabilidad), button];
  });
  host.append(table(['N.º','Reseña','Sentimiento','Probabilidad','Detalle'], rows, 'Resultados del último lote enviado'));
}
