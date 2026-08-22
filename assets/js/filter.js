document.addEventListener('DOMContentLoaded', () => {
  const filterTabs = document.querySelectorAll('.filter-tab');
  const cards = document.querySelectorAll('[data-category]');

  if (filterTabs.length === 0 || cards.length === 0) return;

  filterTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      filterTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      const targetCategory = tab.getAttribute('data-filter');

      cards.forEach(card => {
        const cardCategory = card.getAttribute('data-category');
        
        if (targetCategory === 'all' || cardCategory === targetCategory) {
          card.style.display = 'flex';
          card.style.animation = 'fadeIn 0.3s ease forwards';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });
});
