document.addEventListener('DOMContentLoaded', function () {
    const navBar    = document.querySelector('.nav-bar');
    const hamburger = document.querySelector('.nav-hamburger');
    const dropdown  = document.querySelector('.nav-dropdown');

    if (!navBar || !hamburger || !dropdown) return;

    function pinHamburger() {
        // Capture the hamburger's current viewport position before we switch
        // it to position:fixed, so it stays exactly where the user clicked.
        const rect = hamburger.getBoundingClientRect();
        hamburger.style.top    = rect.top + 'px';
        hamburger.style.right  = (window.innerWidth - rect.right) + 'px';
        hamburger.classList.add('is-pinned');
    }

    function unpinHamburger() {
        hamburger.classList.remove('is-pinned');
        hamburger.style.top   = '';
        hamburger.style.right = '';
    }

    function openDropdown() {
        pinHamburger();
        dropdown.classList.add('is-open');
        document.body.classList.add('nav-dropdown-open');
        hamburger.setAttribute('aria-expanded', 'true');
        dropdown.setAttribute('aria-hidden', 'false');
    }

    function closeDropdown() {
        dropdown.classList.remove('is-open');
        document.body.classList.remove('nav-dropdown-open');
        hamburger.setAttribute('aria-expanded', 'false');
        dropdown.setAttribute('aria-hidden', 'true');
        unpinHamburger();
    }

    hamburger.addEventListener('click', function (e) {
        e.stopPropagation();
        if (dropdown.classList.contains('is-open')) {
            closeDropdown();
        } else {
            openDropdown();
        }
    });

    document.addEventListener('click', function (e) {
        if (!hamburger.contains(e.target) && !dropdown.contains(e.target)) {
            closeDropdown();
        }
    });

    dropdown.querySelectorAll('a').forEach(function (link) {
        link.addEventListener('click', closeDropdown);
    });
});
