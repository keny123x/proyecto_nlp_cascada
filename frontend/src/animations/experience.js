export function initExperience() {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const toggle = document.createElement('button');
  toggle.className = 'motion-toggle';
  toggle.textContent = 'Pausar movimiento';
  toggle.setAttribute('aria-pressed', String(reduced.matches));
  document.querySelector('.hero-footer').prepend(toggle);
  function pause(value) {
    document.body.classList.toggle('motion-paused', value);
    toggle.textContent = value ? 'Activar movimiento' : 'Pausar movimiento';
    toggle.setAttribute('aria-pressed', String(value));
    document.dispatchEvent(new CustomEvent('opinometro:motion', {detail:{paused:value}}));
  }
  pause(reduced.matches);
  toggle.addEventListener('click', () => pause(!document.body.classList.contains('motion-paused')));
  reduced.addEventListener('change', (event) => pause(event.matches));

  // El contenido permanece visible sin JavaScript o con movimiento reducido.
  const observer = new IntersectionObserver((entries) => entries.forEach((entry) => {
    if (!entry.isIntersecting) return;
    if (!reduced.matches && !document.body.classList.contains('motion-paused')) {
      entry.target.animate([{opacity:.35,transform:'translateY(18px)'},{opacity:1,transform:'translateY(0)'}], {duration:550,easing:'ease-out'});
    }
    observer.unobserve(entry.target);
  }), {threshold:.12});
  document.querySelectorAll('.section-heading, .input-card, .result-card, .closing h2').forEach((item) => observer.observe(item));

  // Una sola sección activa en la navegación; no altera el scroll del usuario.
  const nav = [...document.querySelectorAll('.header nav a')];
  const sections = [...document.querySelectorAll('main > section[id]')];
  const active = new IntersectionObserver(() => {
    const section = sections.filter((item) => item.getBoundingClientRect().top <= innerHeight * .45).at(-1);
    nav.forEach((link) => {
      if (section && link.hash === `#${section.id}`) link.setAttribute('aria-current','location');
      else link.removeAttribute('aria-current');
    });
  }, {rootMargin:'-10% 0px -50% 0px',threshold:0});
  sections.forEach((item) => active.observe(item));
}
