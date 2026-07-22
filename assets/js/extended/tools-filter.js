/* /tools index: tag pills (multi-select AND) + free-text search over tool
   cards, with the current query/tags mirrored into the URL. No pagination —
   tools are few — so TagFilter falls back to inline show/hide.
   Used by layouts/tools/list.html; loaded from extend_head.html; depends on
   the shared TagFilter class (tag-filter.js). */
document.addEventListener('DOMContentLoaded', () => {
  const grid = document.getElementById('tools-grid');
  if (!grid) return;

  new TagFilter({
    items:        Array.from(grid.querySelectorAll('.article-card')),
    cloud:        document.getElementById('tools-tag-cloud'),
    searchInput:  document.querySelector('.tools-page .article-list-search input'),
    searchFields: ['title', 'description'],
    syncURL:      true
  });
});
