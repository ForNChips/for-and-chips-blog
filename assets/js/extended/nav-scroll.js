/* Persists the horizontal scroll position of the main menu across pages,
   and intercepts in-page anchor clicks to honor prefers-reduced-motion
   and update the URL fragment cleanly. */

const menu = document.getElementById('menu');
if (menu) {
    const stored = localStorage.getItem('menu-scroll-position');
    if (stored) menu.scrollLeft = parseInt(stored, 10);
    menu.addEventListener('scroll', () => {
        localStorage.setItem('menu-scroll-position', menu.scrollLeft);
    });
}

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const id = this.getAttribute('href').slice(1);
        const target = document.querySelector(`[id='${decodeURIComponent(id)}']`);
        if (!target) return;

        e.preventDefault();
        target.scrollIntoView(reduceMotion.matches ? undefined : { behavior: 'smooth' });

        if (id === 'top') history.replaceState(null, null, ' ');
        else              history.pushState(null, null, `#${id}`);
    });
});
