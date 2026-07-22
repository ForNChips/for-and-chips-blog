/* /bags index: tag pills (multi-select AND) + free-text search over bag cards,
   with the current query/tags mirrored into the URL. No pagination — bags are
   few — so TagFilter falls back to inline show/hide. */
document.addEventListener('DOMContentLoaded', () => {
  const results = document.getElementById('bags-results');
  if (!results) return;

  new TagFilter({
    items:        Array.from(results.querySelectorAll('.bag-card')),
    cloud:        document.getElementById('bags-tag-cloud'),
    searchInput:  document.querySelector('.bags-page .article-list-search input'),
    searchFields: ['title', 'description'],
    syncURL:      true
  });
});
