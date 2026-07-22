/* /authors directory: free-text search over author cards (name, affiliations,
   keywords), paginated. No tag pills — TagFilter runs in search-only mode. */
document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('authors-grid');
    if (!grid) return;
    const cards = Array.from(grid.querySelectorAll('.card'));
    if (cards.length === 0) return;

    const paginator = new Paginator({
        articles: cards,
        topEl:    document.getElementById('authors-pagination-top'),
        bottomEl: document.getElementById('authors-pagination-bottom'),
        perPage:  8,
        label:    'author'
    });

    new TagFilter({
        items:        cards,
        paginator,
        searchInput:  document.getElementById('authorSearch'),
        searchFields: ['name', 'affiliations', 'keywords']
    });
});
