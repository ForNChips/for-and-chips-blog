/* Adds a "copy" button to every <pre><code> block on the page.
   The button label and confirmation text come from window.__chipsI18n,
   set inline by extend_head.html so the strings stay translatable. */

const i18n = window.__chipsI18n || { codeCopy: 'copy', codeCopied: 'copied!' };

document.querySelectorAll('pre > code').forEach(codeblock => {
    const container = codeblock.parentNode.parentNode;

    const button = document.createElement('button');
    button.className = 'copy-code';
    button.textContent = i18n.codeCopy;

    const copyingDone = () => {
        button.textContent = i18n.codeCopied;
        setTimeout(() => { button.textContent = i18n.codeCopy; }, 2000);
    };

    button.addEventListener('click', () => {
        if ('clipboard' in navigator) {
            navigator.clipboard.writeText(codeblock.textContent);
            copyingDone();
            return;
        }

        const range = document.createRange();
        range.selectNodeContents(codeblock);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        try {
            document.execCommand('copy');
            copyingDone();
        } catch (e) { /* clipboard unavailable */ }
        selection.removeRange(range);
    });

    if (container.classList.contains('highlight')) {
        container.appendChild(button);
    } else if (container.parentNode.firstChild === container) {
        /* code-block is the very first child — leave it alone */
    } else {
        const tableAncestor = codeblock.closest('table');
        if (tableAncestor) tableAncestor.appendChild(button);
        else               codeblock.parentNode.appendChild(button);
    }
});
