document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('search-input');
  const searchResults = document.getElementById('search-results');
  
  if (!searchInput || !searchResults) return;

  let searchIndex = Array.isArray(window.SEARCH_INDEX) ? window.SEARCH_INDEX : [];

  if (searchIndex.length === 0) {
    const fetchIndex = (url) => {
      return fetch(url).then(res => {
        if (!res.ok) throw new Error('HTTP error ' + res.status);
        return res.json();
      });
    };

    fetchIndex('/search.json')
      .catch(() => fetchIndex('search.json'))
      .catch(() => fetchIndex('../search.json'))
      .then(data => {
        if (Array.isArray(data)) {
          searchIndex = data;
        }
      })
      .catch(err => {
        console.warn('Search index could not be loaded:', err);
      });
  }

  function doSearch(query) {
    query = (query || '').trim().toLowerCase();

    if (!query || query.length < 1) {
      searchResults.innerHTML = '';
      searchResults.style.display = 'none';
      return;
    }

    const currentIndex = (Array.isArray(window.SEARCH_INDEX) && window.SEARCH_INDEX.length > 0) 
      ? window.SEARCH_INDEX 
      : searchIndex;

    const results = currentIndex.filter(item => {
      if (!item) return false;
      const titleStr = String(item.title || '').toLowerCase();
      const descStr = String(item.description || '').toLowerCase();
      const contentStr = String(item.content || '').toLowerCase();
      const catStr = String(item.category || '').toLowerCase();
      const typeStr = String(item.type || '').toLowerCase();
      
      let tagsStr = '';
      if (Array.isArray(item.tags)) {
        tagsStr = item.tags.map(t => String(t)).join(' ').toLowerCase();
      } else if (typeof item.tags === 'string') {
        tagsStr = item.tags.toLowerCase();
      }

      return titleStr.includes(query) || 
             descStr.includes(query) || 
             contentStr.includes(query) || 
             catStr.includes(query) || 
             typeStr.includes(query) || 
             tagsStr.includes(query);
    });

    renderResults(results, query);
  }

  searchInput.addEventListener('input', (e) => {
    doSearch(e.target.value);
  });

  searchInput.addEventListener('focus', (e) => {
    if (e.target.value.trim().length > 0) {
      doSearch(e.target.value);
    }
  });

  document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
      searchResults.style.display = 'none';
    }
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
          <span class="search-type" style="font-size:0.75rem; font-weight:600; text-transform:uppercase; color:var(--c-1-electric-violet); margin-right: 0.5rem;">${escapeHtml(item.type || 'Article')}</span>
          ${item.date ? `<span class="search-date">${escapeHtml(String(item.date))}</span>` : ''}
        </div>
        <h4 class="search-result-title">${escapeHtml(item.title || '')}</h4>
        <p class="search-result-desc">${escapeHtml(item.description || '')}</p>
      </a>
    `).join('');

    searchResults.innerHTML = html;
    searchResults.style.display = 'block';
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/[&<>"']/g, function(m) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m];
    });
  }
});
