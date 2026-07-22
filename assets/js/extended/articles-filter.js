/* /articles list: tag pills (multi-select AND) + free-text search, paginated,
   with the current query/tags mirrored into the URL. All the logic lives in
   the shared TagFilter class. */
document.addEventListener('DOMContentLoaded', () => {
    const articles = Array.from(document.querySelectorAll('article[data-title]'));
    if (articles.length === 0) return;

    const paginator = new Paginator({
        articles,
        topEl:    document.getElementById('articles-pagination-top'),
        bottomEl: document.getElementById('articles-pagination-bottom'),
        perPage:  10
    });

    new TagFilter({
        items:        articles,
        cloud:        document.getElementById('articles-tag-cloud'),
        paginator,
        searchInput:  document.querySelector('.article-list-search input'),
        searchFields: ['title', 'abstract'],
        syncURL:      true
    });
});
