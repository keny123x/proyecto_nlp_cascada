import {initBatch, batchTexts, validateBatch, resetBatch, renderBatch} from './components/batch.js';
import {initMetrics} from './components/metrics.js';
import {initExperience} from './animations/experience.js';
import {getStatus, predict, predictBatch} from './services/api.js';
import {resetResult, renderResult} from './components/result.js';
import {initLaboratory, resetLaboratory, setLaboratory, markLaboratoryEdited} from './components/laboratory.js';
const $ = (selector) => document.querySelector(selector);
let busy = false;
let mode = 'single';
let requestVersion = 0;
let lastText = '';
const review = $('#review');
const examples = {
  positive: 'La habitación estaba impecable y el personal fue muy amable. Nos encantó la estancia.',
  negative: 'La habitación estaba sucia y había mucho ruido. No recomiendo este hotel.',
  mixed: 'La ubicación era excelente, pero la habitación era pequeña y el desayuno no estaba incluido.',
};
const updateCounter = () => { $('#counter').textContent = `${review.value.length} / 2000`; };
function changed() {
  updateCounter();
  markLaboratoryEdited(review.value);
  review.removeAttribute('aria-invalid');
  if (lastText && review.value.trim() !== lastText) {
    $('#form-message').textContent = 'Has cambiado el texto. Analízalo de nuevo para actualizar el resultado.';
  }
}
review.addEventListener('input', changed);
document.querySelectorAll('[data-example]').forEach((button) => button.addEventListener('click', () => {
  review.value = examples[button.dataset.example]; changed(); review.focus();
}));
$('#clear').addEventListener('click', () => {
  requestVersion++; lastText = ''; review.value = ''; $('#batch').value = ''; updateCounter();
  resetResult(); resetLaboratory(); resetBatch(); $('#form-message').textContent = 'Texto borrado. Puedes comenzar un nuevo análisis.'; (mode === 'batch' ? $('#batch') : review).focus();
});
for (const tabMode of ['single', 'batch']) {
  $(`#${tabMode}-tab`).addEventListener('click', () => {
    mode = tabMode;
    for (const other of ['single', 'batch']) {
      const selected = mode === other;
      $(`#${other}-tab`).setAttribute('aria-selected', String(selected));
      $(`#${other}-tab`).tabIndex = selected ? 0 : -1;
      $(`#${other}-tab`).classList.toggle('active', selected);
      $(`#${other}-panel`).hidden = !selected;
    }
    $('#preview').disabled = busy;
    $('#preview').textContent = busy ? 'Analizando…' : mode === 'batch' ? 'Analizar lote ↗' : 'Analizar reseña ↗';
    $('#batch-results').hidden = mode !== 'batch';
    $('#form-message').textContent = mode === 'batch'
      ? 'Una reseña por línea. Selecciona un resultado del lote para explorar sus pasos NLP.'
      : 'Tu texto se envía al backend local para obtener la predicción.';
  });
}
$('#preview').addEventListener('click', async () => {
  if (busy) return;
  const submittedMode = mode;
  const texts = batchTexts();
  if (submittedMode === 'batch') {
    const error = validateBatch(texts);
    if (error) { $('#form-message').textContent = error; $('#batch').setAttribute('aria-invalid','true'); $('#batch').focus(); return; }
  }
  const texto = review.value.trim();
  if (submittedMode === 'single' && (!texto || !/[a-záéíóúñü]/i.test(texto) || review.value.length > 2000)) {
    $('#form-message').textContent = !texto ? 'Escribe una reseña antes de analizar.' : review.value.length > 2000 ? 'La reseña no puede superar los 2000 caracteres.' : 'La reseña debe contener al menos una palabra.';
    review.setAttribute('aria-invalid', 'true'); review.focus(); return;
  }
  review.removeAttribute('aria-invalid');
  busy = true; const version = ++requestVersion;
  $('#preview').disabled = true; $('#preview').textContent = 'Analizando…';
  resetResult(); resetLaboratory();
  $('#batch-results').replaceChildren();
  $('.result-card').setAttribute('aria-busy', 'true');
  $('#form-message').textContent = submittedMode === 'batch' ? 'Procesando las reseñas del lote…' : 'Procesando tu reseña con el pipeline del servidor…';
  try {
    const response = submittedMode === 'batch' ? await predictBatch(texts) : await predict(texto);
    if (version !== requestVersion) return;
    if (submittedMode === 'batch') {
      renderBatch(response, (result) => {
        renderResult(result); setLaboratory(result);
        document.querySelector('#laboratorio').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'});
      });
      $('#batch-results').hidden = mode !== 'batch';
      $('.result-description').textContent = 'Selecciona Explorar en una fila del lote para ver su resultado y recorrido NLP.';
      $('#form-message').textContent = JSON.stringify(batchTexts()) !== JSON.stringify(texts)
        ? 'El lote cambió. Los resultados corresponden al último lote enviado.'
        : `Lote completado: ${response.total} reseñas. Selecciona Explorar para ver el detalle de una reseña.`;
      $('#service-state').textContent = response.resultados.every((result) => result.modo === 'real') ? 'MODELO REAL · API CONECTADA' : 'ATENCIÓN · MODO SIMULADO';
      return;
    }
    const data = response;
    renderResult(data); setLaboratory(data); markLaboratoryEdited(review.value); lastText = texto;
    $('#form-message').textContent = review.value.trim() !== texto
      ? 'Resultado del texto enviado. Has editado la reseña; vuelve a analizar para actualizarlo.'
      : data.modo === 'real' ? 'Análisis completado con el modelo real. Explora el recorrido de tus palabras en el laboratorio inferior.'
      : 'Modo simulado: respuesta fija de prueba. El modelo entrenado no está cargado.';
    $('#service-state').textContent = data.modo === 'real' ? 'MODELO REAL · API CONECTADA' : 'ATENCIÓN · MODO SIMULADO';
  } catch (error) {
    if (version === requestVersion) {
      $('#form-message').textContent = error.message;
      $('#service-state').textContent = 'ANÁLISIS NO DISPONIBLE · REINTENTA';
    }
  } finally {
    busy = false; $('.result-card').setAttribute('aria-busy', 'false');
    $('#preview').disabled = false; $('#preview').textContent = mode === 'batch' ? 'Analizar lote ↗' : 'Analizar reseña ↗';
  }
});
// Navegación por teclado de ambos grupos de pestañas.
document.querySelectorAll('[role="tablist"]').forEach((list) => list.addEventListener('keydown', (event) => {
  const tabs = [...list.querySelectorAll('[role="tab"]')];
  const index = tabs.indexOf(document.activeElement);
  if (index < 0) return;
  let next;
  if (['ArrowRight', 'ArrowDown'].includes(event.key)) next = (index + 1) % tabs.length;
  if (['ArrowLeft', 'ArrowUp'].includes(event.key)) next = (index + tabs.length - 1) % tabs.length;
  if (event.key === 'Home') next = 0;
  if (event.key === 'End') next = tabs.length - 1;
  if (next !== undefined) { event.preventDefault(); tabs[next].focus(); tabs[next].click(); }
}));
initLaboratory();
initBatch();
initMetrics();
initExperience();
resetResult();
$('#preview').textContent = 'Analizar reseña ↗';
$('.prototype-label').id = 'service-state';
$('#service-state').setAttribute('role', 'status');
$('#service-state').textContent = 'COMPROBANDO CONEXIÓN CON LA API…';
$('#form-message').textContent = 'Tu texto se envía al backend local para obtener la predicción.';
review.setAttribute('aria-describedby', 'form-message');
$('#batch').setAttribute('aria-describedby', 'batch-count form-message');
for (const input of [review, $('#batch')]) input.addEventListener('keydown', (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
    event.preventDefault(); $('#preview').click();
  }
});
getStatus().then((data) => {
  $('#service-state').textContent = data.modo === 'real' ? 'MODELO REAL · API CONECTADA' : 'ATENCIÓN · MODO SIMULADO';
}).catch(() => { $('#service-state').textContent = 'API DESCONECTADA · INICIA FASTAPI EN :8000'; });
