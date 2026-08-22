document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('search-input');
  const searchResults = document.getElementById('search-results');
  
  if (!searchInput || !searchResults) return;

  let searchIndex = [];

  // Fetch search JSON index
  fetch('/search.json')
    .then(response => response.json())
    .then(data => {
      searchIndex = data;
    })
    .catch(err => {
      console.warn('Search index could not be loaded:', err);
    });

  let debounceTimer;

  searchInput.addEventListener('input', (e) => {
    clearTimeout(debounceTimer);
    const query = e.target.value.trim().toLowerCase();

    if (query.length < 2) {
      searchResults.innerHTML = '';
      searchResults.style.display = 'none';
      return;
    }

    debounceTimer = setTimeout(() => {
      const results = searchIndex.filter(item => {
        const titleMatch = item.title && item.title.toLowerCase().includes(query);
        const descMatch = item.description && item.description.toLowerCase().includes(query);
        const contentMatch = item.content && item.content.toLowerCase().includes(query);
        const tagsMatch = item.tags && item.tags.some(tag => tag.toLowerCase().includes(query));
        const categoryMatch = item.category && item.category.toLowerCase().includes(query);
        
        return titleMatch || descMatch || contentMatch || tagsMatch || categoryMatch;
      });

      renderResults(results, query);
    }, 200);
  });

  function renderResults(results, query) {
    if (results.length === 0) {
      searchResults.innerHTML = `<div class="search-no-results">No articles or projects found for "${escapeHtml(query)}"</div>`;
      searchResults.style.display = 'block';
      return;
    }

    const html = results.map(item => `
      <a href="${item.url}" class="search-result-item">
        <div class="search-result-meta">
          <span class="badge cat-badge">${escapeHtml(item.category || item.type || 'Article')}</span>
          ${item.date ? `<span class="search-date">${item.date}</span>` : ''}
        </div>
        <h4 class="search-result-title">${escapeHtml(item.title)}</h4>
        <p class="search-result-desc">${escapeHtml(item.description || '')}</p>
      </a>
    `).join('');

    searchResults.innerHTML = html;
    searchResults.style.display = 'block';
  }

  function escapeHtml(str) {
    return str.replace(/[&<>"']/g, function(m) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m];
    });
  }
});
