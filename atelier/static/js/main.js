(() => {
  if (location.hash === '#demo-result') {
    const heading = document.querySelector('#result-title');
    if (heading) { heading.tabIndex = -1; heading.focus({preventScroll:true}); }
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
  try { const saved = localStorage.getItem('atelier-3d-effects'); effects = saved === null ? !motion.matches : saved === 'on'; }
  catch { effects = !motion.matches; }
  const syncEffects = () => {
    document.documentElement.classList.toggle('effects-on', effects && !motion.matches);
    if (motionToggle) {
      motionToggle.setAttribute('aria-pressed', String(effects));
      motionToggle.textContent = `3D effects: ${effects ? (motion.matches ? 'On (motion paused)' : 'On') : 'Off'}`;
      motionToggle.title = motion.matches ? 'Automatic movement is paused by your reduced-motion preference.' : 'Toggle automatic 3D effects';
    }
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
  syncEffects();

  const viewer = document.querySelector('.art-viewer');
  if (viewer && typeof viewer.showModal === 'function') {
    const image = viewer.querySelector('[data-viewer-image]');
    const title = viewer.querySelector('#viewer-title');
    const frame = viewer.querySelector('[data-viewer-frame]');
    const close = viewer.querySelector('[data-viewer-close]');
    let opener = null, x = 0, y = 0, dragging = null;
    const render = () => {
      frame.style.setProperty('--view-x', `${x}deg`);
      frame.style.setProperty('--view-y', `${y}deg`);
    };
    document.querySelectorAll('[data-inspect]').forEach(button => {
      button.hidden = false;
      button.addEventListener('click', () => {
        opener = button;
        title.textContent = button.dataset.title;
        image.alt = button.dataset.title;
        image.hidden = false;
        image.src = button.dataset.image;
        x = 0; y = 0; render();
        viewer.showModal();
        close.focus();
      });
    });
    image.addEventListener('error', () => { image.hidden = true; });
    close.addEventListener('click', () => viewer.close());
    viewer.addEventListener('close', () => { if (opener && opener.isConnected) opener.focus(); });
    viewer.querySelectorAll('[data-view]').forEach(button => button.addEventListener('click', () => {
      const action = button.dataset.view;
      if (action === 'left') y = Math.max(-35, y - 10);
      if (action === 'right') y = Math.min(35, y + 10);
      if (action === 'up') x = Math.max(-25, x - 10);
      if (action === 'down') x = Math.min(25, x + 10);
      if (action === 'reset') { x = 0; y = 0; }
      render();
    }));
    frame.addEventListener('pointerdown', event => {
      dragging = {startX: event.clientX, startY: event.clientY, x, y};
      frame.setPointerCapture(event.pointerId);
      frame.classList.add('dragging');
    });
    frame.addEventListener('pointermove', event => {
      if (!dragging) return;
      y = Math.max(-35, Math.min(35, dragging.y + (event.clientX - dragging.startX) / 4));
      x = Math.max(-25, Math.min(25, dragging.x - (event.clientY - dragging.startY) / 4));
      render();
    });
    const stopDrag = () => { dragging = null; frame.classList.remove('dragging'); };
    frame.addEventListener('pointerup', stopDrag);
    frame.addEventListener('pointercancel', stopDrag);
  }

  const hero = document.querySelector('.hero');
  const scene = document.querySelector('[data-parallax]');
  if (hero && scene && finePointer.matches) {
    hero.addEventListener('pointermove', event => {
      if (event.pointerType === 'touch' || motion.matches || !effects) return;
      const box = hero.getBoundingClientRect();
      scene.style.setProperty('--px', `${((event.clientX - box.left) / box.width - .5) * 12}px`);
      scene.style.setProperty('--py', `${((event.clientY - box.top) / box.height - .5) * 8}px`);
    });
    hero.addEventListener('pointerleave', () => {
      scene.style.setProperty('--px', '0px');
      scene.style.setProperty('--py', '0px');
    });
  }
  document.querySelectorAll('[data-tilt]').forEach(frame => {
    frame.addEventListener('pointermove', event => {
      if (event.pointerType === 'touch' || !finePointer.matches || motion.matches || !effects) return;
      const box = frame.getBoundingClientRect();
      frame.style.setProperty('--tilt-x', `${(0.5 - (event.clientY - box.top) / box.height) * 8}deg`);
      frame.style.setProperty('--tilt-y', `${((event.clientX - box.left) / box.width - 0.5) * 8}deg`);
    });
    frame.addEventListener('pointerleave', () => {
      frame.style.setProperty('--tilt-x', '0deg');
      frame.style.setProperty('--tilt-y', '0deg');
    });
  });
})();
