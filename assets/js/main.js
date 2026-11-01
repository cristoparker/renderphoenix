/* RenderPhoenix — site behaviour. Loaded with `defer`; every feature is optional
   and no-ops when its markup is absent. */
(() => {
  'use strict';

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const escapeHtml = (str) => String(str ?? '').replace(/[&<>"']/g, (c) => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));

  /* ------------------------------------------------------------ Mobile menu */
  const menuBtn = $('.menu-toggle');
  const nav = $('#site-nav');
  if (menuBtn && nav) {
    const setOpen = (open) => {
      nav.classList.toggle('is-open', open);
      menuBtn.setAttribute('aria-expanded', String(open));
      menuBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    };
    menuBtn.addEventListener('click', () => setOpen(!nav.classList.contains('is-open')));
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) { setOpen(false); menuBtn.focus(); }
    });
    document.addEventListener('click', (e) => {
      if (nav.classList.contains('is-open') && !nav.contains(e.target) && !menuBtn.contains(e.target)) setOpen(false);
    });
    matchMedia('(min-width: 901px)').addEventListener('change', (e) => { if (e.matches) setOpen(false); });
  }

  /* ----------------------------------------------------------------- Search */
  const dialog = $('#search-dialog');
  const input = $('#search-input');
  const results = $('#search-results');
  let index = null;
  let indexPromise = null;
  let active = -1;

  const loadIndex = () => {
    indexPromise = indexPromise || fetch('/search.json')
      .then((r) => (r.ok ? r.json() : []))
      .then((data) => { index = Array.isArray(data) ? data : []; })
      .catch(() => { index = []; });
    return indexPromise;
  };

  const score = (item, terms) => {
    const title = String(item.title || '').toLowerCase();
    const hay = [item.description, item.content, item.type, (item.tags || []).join(' ')].join(' ').toLowerCase();
    let total = 0;
    for (const t of terms) {
      if (title.includes(t)) total += title.startsWith(t) ? 6 : 4;
      else if (hay.includes(t)) total += 1;
      else return 0; // every term must match somewhere
    }
    return total;
  };

  const highlight = (i) => {
    const links = $$('a', results);
    active = Math.max(-1, Math.min(i, links.length - 1));
    links.forEach((a, n) => a.setAttribute('aria-selected', String(n === active)));
    if (links[active]) links[active].scrollIntoView({ block: 'nearest' });
  };

  const runSearch = () => {
    const q = input.value.trim().toLowerCase();
    active = -1;
    if (!q) { results.innerHTML = ''; return; }
    if (!index) { loadIndex().then(runSearch); return; }
    const terms = q.split(/\s+/);
    const hits = index
      .map((item) => [score(item, terms), item])
      .filter(([s]) => s > 0)
      .sort((a, b) => b[0] - a[0])
      .slice(0, 12);
    results.innerHTML = hits.length
      ? hits.map(([, it]) => `<li><a href="${escapeHtml(it.url)}"><small>${escapeHtml(it.type || 'Page')}${it.date ? ' · ' + escapeHtml(it.date) : ''}</small><strong>${escapeHtml(it.title)}</strong><span>${escapeHtml(it.description || '')}</span></a></li>`).join('')
      : `<li class="search-empty">No results for “${escapeHtml(input.value.trim())}”.</li>`;
  };

  const openSearch = () => {
    if (!dialog || dialog.open) return;
    loadIndex();
    if (typeof dialog.showModal === 'function') dialog.showModal();
    else dialog.setAttribute('open', '');
    input.select();
  };

  if (dialog && input && results) {
    $$('[data-search-open]').forEach((btn) => btn.addEventListener('click', openSearch));
    $$('[data-search-open]').forEach((btn) => btn.addEventListener('pointerenter', loadIndex, { once: true }));

    document.addEventListener('keydown', (e) => {
      const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName || '');
      if ((e.key === 'k' && (e.ctrlKey || e.metaKey)) || (e.key === '/' && !typing)) {
        e.preventDefault();
        openSearch();
      }
    });

    let timer;
    input.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(runSearch, 80); });
    input.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowDown') { e.preventDefault(); highlight(active + 1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); highlight(active - 1); }
      else if (e.key === 'Enter') {
        const target = $$('a', results)[Math.max(active, 0)];
        if (target) { e.preventDefault(); location.href = target.href; }
      }
    });
    dialog.addEventListener('click', (e) => { if (e.target === dialog) dialog.close(); });
  }

  /* -------------------------------------------------------- Work filtering */
  const chips = $$('.chip[data-filter]');
  const cards = $$('[data-filter-grid] .card');
  const count = $('[data-result-count]');
  if (chips.length && cards.length) {
    const apply = (filter) => {
      let shown = 0;
      cards.forEach((card) => {
        const match = filter === 'all' || card.dataset.category === filter;
        card.hidden = !match;
        card.classList.toggle('is-entering', match);
        if (match) shown += 1;
      });
      chips.forEach((c) => c.setAttribute('aria-pressed', String(c.dataset.filter === filter)));
      if (count) count.textContent = `${shown} project${shown === 1 ? '' : 's'}`;
    };
    chips.forEach((chip) => chip.addEventListener('click', () => {
      apply(chip.dataset.filter);
      history.replaceState(null, '', chip.dataset.filter === 'all' ? location.pathname : `#${chip.dataset.filter}`);
    }));
    const initial = location.hash.slice(1);
    if (initial && chips.some((c) => c.dataset.filter === initial)) apply(initial);
  }

  /* --------------------------------------------------------- Showcase rail */
  const rail = $('[data-rail]');
  const railNav = $('[data-rail-nav]');
  if (rail && railNav) {
    const prev = $('[data-rail-prev]', railNav);
    const next = $('[data-rail-next]', railNav);
    const step = () => (rail.firstElementChild?.getBoundingClientRect().width || 400) + 24;
    const update = () => {
      prev.disabled = rail.scrollLeft <= 4;
      next.disabled = rail.scrollLeft + rail.clientWidth >= rail.scrollWidth - 4;
    };
    prev.addEventListener('click', () => rail.scrollBy({ left: -step(), behavior: 'smooth' }));
    next.addEventListener('click', () => rail.scrollBy({ left: step(), behavior: 'smooth' }));
    rail.addEventListener('scroll', update, { passive: true });
    railNav.hidden = false;
    update();
  }

  /* ------------------------------------------------------------ Code copy */
  $$('.code-copy-btn').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const code = btn.closest('.code-block-wrapper')?.querySelector('pre code');
      if (!code) return;
      try {
        await navigator.clipboard.writeText(code.innerText);
        const label = btn.querySelector('span');
        const original = label ? label.textContent : '';
        if (label) label.textContent = 'Copied';
        setTimeout(() => { if (label) label.textContent = original; }, 1800);
      } catch (_) { /* clipboard unavailable */ }
    });
  });

  /* ------------------------------------------------------- YouTube facade */
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.yt-facade');
    if (!btn) return;
    const iframe = document.createElement('iframe');
    iframe.src = `https://www.youtube-nocookie.com/embed/${encodeURIComponent(btn.dataset.yt)}?autoplay=1`;
    iframe.title = btn.getAttribute('aria-label')?.replace(/^Play video: /, '') || 'YouTube video';
    iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    iframe.allowFullscreen = true;
    btn.replaceWith(iframe);
  });

  /* --------------------------------------------------------- Contact form */
  const form = $('[data-mailto-form]');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const data = new FormData(form);
      const subject = `${data.get('subject') || 'Inquiry'} — ${data.get('name') || ''}`.trim();
      const body = `${data.get('message') || ''}\n\n— ${data.get('name') || ''}\n${data.get('email') || ''}`;
      location.href = `mailto:${form.dataset.mailtoForm}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    });
  }

  /* ---------------------------------------------------- Broken image fallback */
  document.addEventListener('error', (e) => {
    const img = e.target;
    if (img.tagName === 'IMG' && !img.dataset.fallback) {
      img.dataset.fallback = '1';
      img.src = '/assets/images/image-not-found.svg';
    }
  }, true);
})();
