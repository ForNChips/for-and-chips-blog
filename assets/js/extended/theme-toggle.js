const toggle = document.getElementById('theme-toggle');
if (toggle) {
    toggle.addEventListener('click', () => {
        const html = document.documentElement;
        const next = html.dataset.theme === 'dark' ? 'light' : 'dark';
        html.dataset.theme = next;
        localStorage.setItem('pref-theme', next);
    });
}
