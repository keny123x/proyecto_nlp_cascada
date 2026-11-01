const $ = (selector) => document.querySelector(selector);
const percent = (value) => (value * 100).toLocaleString('es', {minimumFractionDigits: 1, maximumFractionDigits: 1});
export function resetResult() {
  $('.result-card').classList.remove('negative');
  $('.result-card').setAttribute('aria-busy', 'false');
  $('.sample-badge').textContent = 'Sin analizar';
  $('#result-title').textContent = 'Tu opinión empieza aquí.';
  $('.result-description').textContent = 'Escribe una reseña y pulsa Analizar reseña para conocer el resultado.';
  $('.result-symbol').textContent = '✧';
  $('.result-value > span').textContent = 'Esperando una reseña';
  $('.result-value strong').replaceChildren(document.createTextNode('—'));
  $('.probability-track > span').style.width = '0%';
  $('.probability-legend span:first-child').textContent = 'Positivo —';
  $('.probability-legend span:last-child').textContent = 'Negativo —';
  $('.result-footnote').textContent = 'La probabilidad estima una clase; no mide la intensidad de la emoción.';
}
export function renderResult(data) {
  const positive = data.sentimiento === 'Positivo';
  $('.result-card').classList.toggle('negative', !positive);
  $('.sample-badge').textContent = data.modo === 'real' ? 'Modelo real' : 'SIMULADO';
  $('#result-title').textContent = positive ? 'Una buena señal.' : 'Algo no salió bien.';
  $('.result-symbol').textContent = positive ? '↗' : '↘';
  $('.result-description').textContent = data.modo === 'real'
    ? 'Clasificación del modelo para la reseña enviada.'
    : 'Respuesta de prueba: el modelo real no está cargado. No es una predicción real.';
  $('.result-value > span').textContent = positive ? 'Positiva' : 'Negativa';
  const symbol = document.createElement('span'); symbol.textContent = '%';
  $('.result-value strong').replaceChildren(document.createTextNode(percent(data.probabilidad)), symbol);
  $('.probability-track > span').style.width = `${data.probabilidades.Positivo * 100}%`;
  $('.probability-legend span:first-child').textContent = `Positivo ${percent(data.probabilidades.Positivo)} %`;
  $('.probability-legend span:last-child').textContent = `Negativo ${percent(data.probabilidades.Negativo)} %`;
  $('.result-footnote').textContent = data.modo === 'real'
    ? `Texto analizado: «${data.pasos.texto_original}». Probabilidad estimada, no garantía de acierto.`
    : `Texto enviado: «${data.pasos.texto_original}». Porcentajes fijos de demostración, sin inferencia del modelo.`;
}
