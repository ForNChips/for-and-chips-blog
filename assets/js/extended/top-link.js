const SCROLL_THRESHOLD = 800;

const button = document.getElementById('top-link');
if (button) {
    let ticking = false;
    const update = () => {
        const scrolled = document.body.scrollTop || document.documentElement.scrollTop;
        const visible = scrolled > SCROLL_THRESHOLD;
        button.style.visibility = visible ? 'visible' : 'hidden';
        button.style.opacity    = visible ? '1' : '0';
        ticking = false;
    };

    window.addEventListener('scroll', () => {
        if (!ticking) {
            requestAnimationFrame(update);
            ticking = true;
        }
    }, { passive: true });
}
