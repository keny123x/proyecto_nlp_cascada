import {normalizationScene, tokenizationScene} from './text-transform.js';
const $ = (selector) => document.querySelector(selector);
const titles = ['01 / NORMALIZACIÓN', '02 / TOKENIZACIÓN', '03 / STOP WORDS', '04 / STEMMING'];
let prediction = null;
let current = 0;
let timer = null;
let sequenceTimer = null;
let sequence = [];
let cursor = 0;
let paused = false;
let speed = 1;
let generation = 0;
let scene = null;
const reducedMotion = () => matchMedia('(prefers-reduced-motion: reduce)').matches || document.body.classList.contains('motion-paused');
function cancelSequence() {
  generation++; clearTimeout(sequenceTimer); sequenceTimer = null;
  $('#step-body')?.getAnimations({subtree:true}).forEach((animation) => animation.cancel());
  $('#step-body')?.querySelectorAll('.word-focus').forEach((item) => item.classList.remove('word-focus'));
}
function animateNext() {
  if (paused || !prediction) return;
  const token = generation;
  const previous = sequence[cursor - 1];
  if (previous) previous.classList.remove('word-focus');
  if (cursor >= sequence.length) {
    $('#word-status').textContent = sequence.length ? 'Transformación completa · explora las palabras' : 'Sin palabras para animar en esta etapa';
    $('#word-progress').style.width = '100%';
    $('#pause-words').textContent = 'Pausar palabras'; $('#pause-words').disabled = true;
    if (timer) timer = setTimeout(() => { if (token === generation) { if (current < 3) show(current + 1); else stop(); } }, 1100);
    return;
  }
  const item = sequence[cursor++];
  item.classList.add('word-focus', 'word-visited');
  $('#word-status').textContent = `${current === 0 ? 'Fase' : 'Palabra'} ${cursor} de ${sequence.length} · ${item.dataset.action || 'observa su transformación'}`;
  $('#word-progress').style.width = `${cursor / sequence.length * 100}%`;
  let visualDelay = null;
  if (item.runVisual && !reducedMotion()) visualDelay = item.runVisual(speed);
  else if (!reducedMotion()) {
    item.animate([{transform:'translateY(3px) scale(.94)',opacity:.55},{transform:'translateY(-3px) scale(1.09)',opacity:1},{transform:'translateY(0) scale(1)',opacity:1}],{duration:420 / speed,easing:'ease-out'});
    if (item.classList.contains('root-pair')) item.querySelector('strong').animate([{opacity:.2,filter:'blur(3px)'},{opacity:1,filter:'blur(0)'}],{duration:450 / speed});
  }
  const delay = Math.max(70, Math.min(480, 8500 / Math.max(1, sequence.length))) / speed;
  sequenceTimer = setTimeout(() => { if (token === generation) animateNext(); }, visualDelay ?? delay);
}
function startSequence() {
  cancelSequence(); cursor = 0; paused = false;
  scene = null;
  if (prediction && current < 2) {
    const body = $('#step-body'); body.replaceChildren();
    scene = current === 0 ? normalizationScene(body,prediction.pasos) : tokenizationScene(body,prediction.pasos);
  }
  sequence = scene ? scene.items : [...$('#step-body').querySelectorAll('[data-animate-word]')];
  sequence.forEach((item) => item.classList.remove('word-visited'));
  $('#pause-words').disabled = !prediction || !sequence.length;
  $('#repeat-words').disabled = !prediction;
  $('#pause-words').textContent = 'Pausar palabras';
  $('#word-progress').style.width = '0%';
  if (!prediction) { $('#word-status').textContent = 'El recorrido se iluminará palabra por palabra'; return; }
  if (reducedMotion()) {
    scene?.finish();
    sequence.forEach((item) => item.classList.add('word-visited'));
    cursor = sequence.length;
    $('#pause-words').disabled = true;
    $('#word-status').textContent = 'Vista completa · movimiento reducido'; $('#word-progress').style.width = '100%';
    if (timer) timer = setTimeout(() => { if (current < 3) show(current + 1); else stop(); }, 3000);
    return;
  }
  animateNext();
}

function element(tag, text, className = '') {
  const node = document.createElement(tag);
  node.textContent = text;
  node.className = className;
  return node;
}
function words(items, {removed = false, negations = [], animate = true} = {}) {
  const group = element('div', '', 'chips');
  if (!items.length) return element('p', 'Ninguna en esta reseña.', 'empty-words');
  items.forEach((word) => {
    const chip = element('span', word, `chip${removed ? ' removed' : negations.includes(word) ? ' negation' : ''}`);
    if (animate) { chip.dataset.animateWord = ''; chip.dataset.action = removed ? 'palabra eliminada' : negations.includes(word) ? 'negación conservada' : 'palabra conservada'; }
    if (negations.includes(word)) chip.title = 'Negación conservada';
    group.append(chip);
  });
  return group;
}
function stop() {
  clearTimeout(timer); timer = null;
  $('#play-steps').textContent = 'Reproducir recorrido';
  $('#play-steps').setAttribute('aria-pressed', 'false');
}
function show(index) {
  clearTimeout(timer); if (timer) timer = -1;
  cancelSequence();
  current = index;
  $('#step-label').textContent = titles[index];
  document.querySelectorAll('[data-step]').forEach((button) => {
    const selected = Number(button.dataset.step) === index;
    button.id = `stage-${button.dataset.step}`;
    button.classList.toggle('active', selected);
    button.setAttribute('aria-selected', String(selected));
    button.tabIndex = selected ? 0 : -1;
  });
  $('#step-content').setAttribute('aria-labelledby', `stage-${index}`);
  $('#previous-step').disabled = !prediction || index === 0;
  $('#next-step').disabled = !prediction || index === 3;
  $('#play-steps').disabled = !prediction;
  const body = $('#step-body'); body.replaceChildren();
  if (!prediction) {
    body.append(element('p', 'Cada palabra tiene un recorrido.', 'normalized'),
      element('p', 'Analiza una reseña para ver sus transformaciones reales, calculadas por el backend.'));
    startSequence(); return;
  }
  const steps = prediction.pasos;
  const negations = steps.paso3_negaciones_conservadas;
  if (index < 2) {
    // La escena se construye al iniciar/repetir para volver al estado original.
  } else if (index === 2) {
    body.append(element('h3', `Conservadas · ${steps.paso3_sin_stopwords.length}`, 'lab-caption'), words(steps.paso3_sin_stopwords, {negations}),
      element('h3', `Eliminadas · ${steps.paso3_stopwords_eliminadas.length}`, 'lab-caption'), words(steps.paso3_stopwords_eliminadas, {removed:true}),
      element('h3', 'Negaciones conservadas', 'lab-caption'), words(negations, {negations, animate:false}),
      element('p', 'El borde coral identifica las negaciones que el pipeline conserva. Las palabras tachadas son las stop words eliminadas.'));
  } else {
    body.append(element('h3', 'Palabra → raíz', 'lab-caption'));
    const mappings = element('div', '', 'root-mappings');
    steps.paso4_stemming.forEach((root, i) => {
      const row = element('div', '', 'root-pair');
      row.dataset.animateWord = ''; row.dataset.action = `${steps.paso3_sin_stopwords[i]} → ${root}`;
      row.append(element('span', steps.paso3_sin_stopwords[i]), element('span', '→'), element('strong', root));
      mappings.append(row);
    });
    body.append(mappings.childElementCount ? mappings : element('p', 'No quedaron palabras para reducir.'),
      element('p', 'El modelo utiliza stemming. Las raíces no son lemas ni necesariamente palabras completas.'));
  }
  // Hover y foco permiten inspeccionar una palabra sin alterar los datos.
  body.querySelectorAll('[data-animate-word]').forEach((item) => {
    item.tabIndex = 0;
    item.setAttribute('aria-label', `${item.textContent}: ${item.dataset.action}`);
  });
  startSequence();
}
export function resetLaboratory() {
  stop(); prediction = null;
  $('#lab-mode').textContent = 'ESPERANDO RESEÑA';
  $('#lab-source').textContent = 'Sin análisis activo.';
  $('#lab-stale').textContent = '';
  show(0);
}
export function setLaboratory(data) {
  stop(); prediction = data;
  $('#lab-mode').textContent = data.modo === 'real' ? 'NLP DE LA RESEÑA ENVIADA' : 'NLP REAL · PREDICCIÓN SIMULADA';
  $('#lab-source').textContent = `Reseña enviada: «${data.pasos.texto_original}»`;
  $('#lab-stale').textContent = '';
  show(0);
}
export function markLaboratoryEdited(text) {
  $('#lab-stale').textContent = prediction && text.trim() !== prediction.pasos.texto_original
    ? 'El formulario cambió. Este recorrido corresponde al último texto enviado; analiza de nuevo para actualizarlo.' : '';
}
export function initLaboratory() {
  const controls = element('div', '', 'lab-buttons');
  const previous = element('button', '←'); previous.id = 'previous-step'; previous.setAttribute('aria-label', 'Etapa anterior');
  const play = element('button', 'Reproducir recorrido'); play.id = 'play-steps'; play.setAttribute('aria-pressed', 'false');
  const next = $('#next-step');
  $('.lab-controls').firstElementChild.id = 'lab-source';
  $('.lab-controls').append(controls); controls.append(previous, play, next);
  $('.step-panel .card-top span:last-child').id = 'lab-mode';
  const note = element('p', '', 'lab-stale'); note.id = 'lab-stale'; note.setAttribute('role', 'status');
  $('.lab-layout').before(note);
  document.querySelectorAll('[data-step]').forEach((button) => button.addEventListener('click', () => { stop(); show(Number(button.dataset.step)); }));
  previous.addEventListener('click', () => { stop(); show(Math.max(0, current - 1)); });
  next.addEventListener('click', () => { stop(); show(Math.min(3, current + 1)); });
  play.addEventListener('click', () => {
    if (timer) {
      stop(); paused = true; clearTimeout(sequenceTimer);
      $('#step-body').getAnimations({subtree:true}).forEach((animation) => animation.pause());
      $('#pause-words').textContent = 'Continuar palabras'; return;
    }
    if (!prediction) return;
    timer = -1;
    play.textContent = 'Pausar recorrido'; play.setAttribute('aria-pressed', 'true');
    if (current === 3 || cursor >= sequence.length) show(current === 3 ? 0 : current);
    else {
      clearTimeout(sequenceTimer);
      if (paused && scene) { cancelSequence(); cursor = Math.max(0, cursor - 1); }
      paused = false;
      $('#pause-words').textContent = 'Pausar palabras';
      $('#step-body').getAnimations({subtree:true}).forEach((animation) => animation.play());
      animateNext();
    }
  });
  const toolbar = element('div', '', 'word-toolbar');
  const status = element('span', '', 'word-status'); status.id = 'word-status';
  const actions = element('div', '', 'word-actions');
  const pause = element('button', 'Pausar palabras'); pause.id = 'pause-words';
  const repeat = element('button', 'Repetir paso'); repeat.id = 'repeat-words';
  const label = element('label', 'Velocidad'); label.htmlFor = 'word-speed';
  const select = element('select'); select.id = 'word-speed';
  [['0.6','Lenta'],['1','Normal'],['1.8','Rápida']].forEach(([value,text]) => { const option = element('option',text); option.value = value; option.selected = value === '1'; select.append(option); });
  actions.append(pause,repeat,label,select); toolbar.append(status,actions);
  const track = element('div','','word-progress-track'); const progress = element('span'); progress.id = 'word-progress'; track.append(progress);
  $('#step-body').before(toolbar,track);
  pause.addEventListener('click', () => {
    paused = !paused;
    pause.textContent = paused ? 'Continuar palabras' : 'Pausar palabras';
    if (paused) {
      clearTimeout(sequenceTimer); clearTimeout(timer); if (timer) timer = -1;
      $('#step-body').getAnimations({subtree:true}).forEach((animation) => animation.pause());
    } else {
      if (scene) { cancelSequence(); cursor = Math.max(0, cursor - 1); }
      $('#step-body').getAnimations({subtree:true}).forEach((animation) => animation.play());
      animateNext();
    }
  });
  repeat.addEventListener('click', () => { stop(); startSequence(); });
  select.addEventListener('change', () => { speed = Number(select.value); });
  const pauseAll = () => { stop(); paused = true; clearTimeout(sequenceTimer); if (prediction && cursor < sequence.length) pause.textContent = 'Continuar palabras'; };
  document.addEventListener('visibilitychange', () => { if (document.hidden) pauseAll(); });
  document.addEventListener('opinometro:motion', (event) => { if (event.detail.paused) { pauseAll(); show(current); } });
  matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', () => { stop(); show(current); });
  resetLaboratory();
}
