/**
 * Copy-link button on article pages.
 *
 * Copies the article's canonical URL (passed via data-url, so query strings
 * and fragments in the address bar are ignored). Falls back to a hidden
 * textarea + execCommand when the async Clipboard API is unavailable, which
 * is the case on non-secure origins and older browsers.
 */
(() => {
    const btn = document.querySelector('.copy-link-btn');
    if (!btn) return;

    const label = btn.querySelector('.copy-link-btn__label');
    const original = label.textContent;
    const url = btn.dataset.url || window.location.href;
    let resetTimer = null;

    const flash = (text) => {
        label.textContent = text;
        clearTimeout(resetTimer);
        resetTimer = setTimeout(() => { label.textContent = original; }, 2000);
    };

    const legacyCopy = (value) => {
        const ta = document.createElement('textarea');
        ta.value = value;
        ta.setAttribute('readonly', '');
        ta.style.position = 'fixed';
        ta.style.left = '-9999px';
        document.body.appendChild(ta);
        ta.select();
        let ok = false;
        try { ok = document.execCommand('copy'); } catch { ok = false; }
        document.body.removeChild(ta);
        return ok;
    };

    btn.addEventListener('click', async () => {
        let ok = false;
        if (navigator.clipboard && window.isSecureContext) {
            try {
                await navigator.clipboard.writeText(url);
                ok = true;
            } catch { ok = false; }
        }
        if (!ok) ok = legacyCopy(url);
        flash(ok ? 'Link copied!' : 'Press Ctrl+C to copy');
    });
})();
