(() => {
  if (location.hash === '#demo-result' || location.hash === '#latest-result') {
    const heading = document.querySelector('#result-title');
    if (heading) { heading.tabIndex = -1; heading.focus(); }
  }
  const menu = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#main-nav');
  if (menu && nav) menu.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(open));
    nav.classList.toggle('open', open);
  });

  const demos = {
    admin: ['admin@atelier.example', 'AdminDemo!2026'],
    maya: ['maya@atelier.example', 'BidderDemo!2026'],
    arjun: ['arjun@atelier.example', 'BidderDemo!2026'],
    sara: ['sara@atelier.example', 'BidderDemo!2026']
  };
  document.querySelectorAll('[data-demo]').forEach(button => {
    button.addEventListener('click', () => {
      const credentials = demos[button.dataset.demo];
      if (!credentials) return;
      const form = document.querySelector('.form-stack');
      form.elements.email.value = credentials[0];
      form.elements.password.value = credentials[1];
      form.elements.email.focus();
    });
  });

  document.querySelectorAll('form[data-confirm]').forEach(form => {
    form.addEventListener('submit', event => {
      if (!window.confirm(form.dataset.confirm)) event.preventDefault();
    });
  });

  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const finePointer = window.matchMedia('(pointer: fine)');
  const motionToggle = document.querySelector('[data-motion-toggle]');
  let effects;
  try {
    const saved = localStorage.getItem('atelier-3d-effects');
    effects = saved === null ? !motion.matches : saved === 'on';
  } catch { effects = !motion.matches; }

  const surfaces = [...document.querySelectorAll('[data-tilt], .art-detail-image')];
  const resets = [];
  const enabled = () => effects && !motion.matches;
  const syncEffects = () => {
    document.documentElement.classList.toggle('effects-on', enabled());
    if (motionToggle) {
      motionToggle.setAttribute('aria-pressed', String(effects));
      motionToggle.textContent = `3D effects: ${effects ? (motion.matches ? 'Paused' : 'On') : 'Off'}`;
    }
    if (!enabled()) resets.forEach(reset => reset());
  };
  if (motionToggle) {
    motionToggle.hidden = false;
    motionToggle.addEventListener('click', () => {
      effects = !effects;
      try { localStorage.setItem('atelier-3d-effects', effects ? 'on' : 'off'); } catch {}
      syncEffects();
    });
  }
  motion.addEventListener('change', syncEffects);
  finePointer.addEventListener('change', () => { if (!finePointer.matches) resets.forEach(reset => reset()); });

  // Decorative images and linked frames never become Chrome drag previews.
  document.querySelectorAll('img').forEach(image => {
    image.draggable = false;
    image.addEventListener('dragstart', event => event.preventDefault());
  });
  document.querySelectorAll('.hero, .art-image, .art-card-image, .exhibition-image, .event-detail-image').forEach(surface => {
    surface.draggable = false;
    surface.addEventListener('dragstart', event => event.preventDefault());
    surface.addEventListener('selectstart', event => event.preventDefault());
  });

  surfaces.forEach(surface => {
    let box, frame = 0, pointer = {x:0,y:0};
    const draw = () => {
      frame = 0;
      if (!enabled()) return;
      surface.style.setProperty('--tilt-x', `${-pointer.y * 3}deg`);
      surface.style.setProperty('--tilt-y', `${pointer.x * 4}deg`);
      surface.style.setProperty('--hover-z', '10px');
      surface.style.setProperty('--pointer-x', `${(pointer.x + 1) * 50}%`);
      surface.style.setProperty('--pointer-y', `${(pointer.y + 1) * 50}%`);
    };
    const reset = () => {
      cancelAnimationFrame(frame); frame = 0;
      surface.classList.remove('is-hovered','is-focused');
      surface.style.setProperty('--tilt-x','0deg');
      surface.style.setProperty('--tilt-y','0deg');
      surface.style.setProperty('--hover-z','0px');
      surface.style.setProperty('--pointer-x','50%');
      surface.style.setProperty('--pointer-y','50%');
    };
    resets.push(reset);
    surface.addEventListener('pointerenter', event => {
      if (event.pointerType === 'touch' || !finePointer.matches || !enabled()) return;
      box = surface.getBoundingClientRect();
      surface.classList.add('is-hovered');
    });
    surface.addEventListener('pointermove', event => {
      if (event.pointerType === 'touch' || !finePointer.matches || !enabled()) return;
      box ||= surface.getBoundingClientRect();
      pointer.x = Math.max(-1,Math.min(1,(event.clientX-box.left)/box.width*2-1));
      pointer.y = Math.max(-1,Math.min(1,(event.clientY-box.top)/box.height*2-1));
      if (!frame) frame = requestAnimationFrame(draw);
    });
    surface.addEventListener('pointerleave', () => { box = null; reset(); });
    surface.addEventListener('focusin', () => {
      if (!enabled()) return;
      surface.classList.add('is-focused');
      pointer = {x:-0.35,y:-0.25};
      if (!frame) frame = requestAnimationFrame(draw);
    });
    surface.addEventListener('focusout', reset);
  });

  const hero = document.querySelector('.hero');
  const scene = document.querySelector('[data-parallax]');
  if (hero && scene) {
    let animation = 0, bounds, target = {x:0,y:0}, camera = {x:0,y:0};
    const render = () => {
      camera.x += (target.x-camera.x)*0.12;
      camera.y += (target.y-camera.y)*0.12;
      scene.style.setProperty('--camera-x',`${camera.x}deg`);
      scene.style.setProperty('--camera-y',`${camera.y}deg`);
      if (Math.abs(target.x-camera.x)+Math.abs(target.y-camera.y)>0.015) animation=requestAnimationFrame(render);
      else animation=0;
    };
    const reset = () => {
      cancelAnimationFrame(animation); animation=0;
      target={x:0,y:0}; camera={x:0,y:0};
      scene.style.setProperty('--camera-x','0deg');
      scene.style.setProperty('--camera-y','0deg');
      hero.style.setProperty('--light-x','50%');
      hero.style.setProperty('--light-y','50%');
    };
    resets.push(reset);
    hero.addEventListener('pointerenter', () => { bounds=hero.getBoundingClientRect(); });
    hero.addEventListener('pointermove', event => {
      if (event.pointerType==='touch' || !finePointer.matches || !enabled() || hero.classList.contains('webgl-ready')) return;
      bounds ||= hero.getBoundingClientRect();
      const x=Math.max(0,Math.min(1,(event.clientX-bounds.left)/bounds.width));
      const y=Math.max(0,Math.min(1,(event.clientY-bounds.top)/bounds.height));
      target={x:(0.5-y)*10,y:(x-0.5)*16};
      hero.style.setProperty('--light-x',`${x*100}%`);
      hero.style.setProperty('--light-y',`${y*100}%`);
      if (!animation) animation=requestAnimationFrame(render);
    });
    hero.addEventListener('pointerleave', () => {
      target={x:0,y:0}; bounds=null;
      if (!animation) animation=requestAnimationFrame(render);
    });
  }
  window.addEventListener('blur', () => resets.forEach(reset => reset()));
  syncEffects();
})();
