(() => {
  const bar = document.getElementById('reading-progress');
  if (!bar) return;

  let ticking = false;
  const update = () => {
    const el = document.documentElement;
    const scrolled = el.scrollTop || document.body.scrollTop;
    const total = el.scrollHeight - el.clientHeight;
    bar.style.width = (total > 0 ? (scrolled / total) * 100 : 0) + '%';
    ticking = false;
  };

  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(update);
      ticking = true;
    }
  }, { passive: true });

  update();
})();
