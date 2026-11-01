// Animaciones de presentación. Los textos de cada fase llegan de Python.
import {node} from './dom.js';

export function normalizationScene(body, steps) {
  const root = node('div','','normalization-scene');
  const original = node('p',steps.texto_original,'original');
  const line = node('div',steps.texto_original,'normalization-line');
  line.setAttribute('aria-label','Texto durante la normalización');
  const legend = node('p','Los elementos coral desaparecerán; la frase permanece como texto continuo.','transform-help');
  const phases = node('div','','normalization-phases');
  const snapshots = steps.normalizacion_etapas?.length ? steps.normalizacion_etapas : [{nombre:'Texto normalizado',texto:steps.paso1_normalizado}];
  const final = node('p','','normalization-final');
  final.hidden = true;
  root.append(node('h3','Texto original','lab-caption'),original,node('h3','Limpiando la misma frase','lab-caption'),line,phases,legend,final);
  body.append(root);
  let active = 0;
  const items = snapshots.map((phase,index) => {
    const pill = node('span',phase.nombre,'normalization-phase');
    pill.dataset.action = phase.nombre; phases.append(pill);
    const before = index ? snapshots[index - 1].texto : steps.texto_original;
    pill.runVisual = (speed) => {
      active = index;
      line.replaceChildren();
      const duration = 1000 / speed;
      if (phase.nombre.startsWith('Retirar') || phase.nombre === 'Ordenar espacios') {
        // Estas fases eliminan caracteres: el texto siguiente es subsecuencia
        // del anterior. Solo marcamos la diferencia entre snapshots del servidor.
        const after = [...phase.texto]; let target = 0;
        let run = ''; let deleting = null;
        function flush() {
          if (!run) return;
          line.append(node('span',run,deleting ? 'normalization-removal' : 'normalization-kept'));
          run = '';
        }
        for (const char of before) {
          const removed = char !== after[target];
          if (!removed) target++;
          if (removed !== deleting) { flush(); deleting = removed; }
          run += char;
        }
        flush();
        const removals = [...line.querySelectorAll('.normalization-removal')];
        removals.forEach((span) => span.animate([
          {opacity:1,filter:'blur(0)',backgroundColor:'#ff967f44'},
          {opacity:1,offset:.3,filter:'blur(0)',backgroundColor:'#ff967f55'},
          {opacity:0,filter:'blur(5px)',transform:'translateY(-12px) scale(.7)'},
        ],{duration,fill:'forwards'}));
      } else {
        line.textContent = before || ' ';
        line.animate([{opacity:1},{opacity:.3,offset:.5},{opacity:1}],{duration});
      }
      // Un reloj de animación cancelable comparte pausa con el resto del panel.
      const clock = root.animate([{opacity:1},{opacity:1}],{duration});
      clock.finished.then(() => {
        if (!root.isConnected || active !== index) return;
        line.textContent = phase.texto || '(Texto vacío tras normalizar)';
        if (index === snapshots.length - 1) {
          final.textContent = 'Texto limpio. Todavía no lo hemos separado en tokens.'; final.hidden = false;
        }
      }).catch(() => {});
      return duration + 180 / speed;
    };
    return pill;
  });
  return {items,finish() {
    line.textContent = steps.paso1_normalizado || '(Texto vacío tras normalizar)';
    final.textContent = 'Texto limpio. Todavía no lo hemos separado en tokens.'; final.hidden = false;
  }};
}

export function tokenizationScene(body, steps) {
  const root = node('div','','tokenization-scene');
  const source = node('div','','token-source');
  const destination = node('div','','token-destination');
  source.setAttribute('aria-label','Frase normalizada antes de separar');
  const sourceWords = [];
  steps.paso2_tokens.forEach((word,index) => {
    const span = node('span',word,'token-source-word'); sourceWords.push(span);
    source.append(span); if (index < steps.paso2_tokens.length - 1) source.append(document.createTextNode(' '));
  });
  if (!steps.paso2_tokens.length) source.textContent = 'No hay palabras para separar.';
  const counter = node('p',`0 de ${steps.paso2_tokens.length} palabras en sus casillas`,'token-counter');
  root.append(node('h3','Una frase completa','lab-caption'),source,node('div','↓ Separar por palabras','token-flow-label'),node('h3','Casillas de tokens','lab-caption'),destination,counter,node('p','Cada palabra sale de la frase y ocupa su propia casilla, conservando el orden y las repeticiones.','transform-help'));
  body.append(root);
  const items = steps.paso2_tokens.map((word,index) => {
    const slot = node('span','','token-slot');
    const target = node('span',word,'token-target');
    target.dataset.action = `«${word}» viaja a la casilla ${index + 1}`;
    slot.append(target); destination.append(slot);
    target.runVisual = (speed) => {
      const from = sourceWords[index].getBoundingClientRect();
      const to = target.getBoundingClientRect();
      target.classList.add('token-arrived');
      sourceWords[index].classList.add('token-departed');
      slot.classList.add('token-filled');
      const duration = Math.max(140, Math.min(800, 9000 / Math.max(1, items.length))) / speed;
      target.animate([
        {transform:`translate(${from.left - to.left}px,${from.top - to.top}px) scale(1.05)`,opacity:1,backgroundColor:'#80e5cf33'},
        {transform:'translate(0,0) scale(1)',opacity:1,backgroundColor:'#80e5cf08'},
      ],{duration,easing:'cubic-bezier(.25,.6,.3,1)'});
      counter.textContent = `${index + 1} de ${steps.paso2_tokens.length} palabras en sus casillas`;
      return duration + 120 / speed;
    };
    return target;
  });
  return {items,finish() {
    items.forEach((item,index) => {
      item.classList.add('token-arrived'); item.parentElement.classList.add('token-filled');
      sourceWords[index].classList.add('token-departed');
    });
    counter.textContent = `${items.length} de ${items.length} palabras en sus casillas`;
  }};
}
