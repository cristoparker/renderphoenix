// Global Image Error Fallback Handler
document.addEventListener('error', (e) => {
  if (e.target && e.target.tagName === 'IMG') {
    if (!e.target.dataset.fallbackTried) {
      e.target.dataset.fallbackTried = '1';
      e.target.src = '/assets/images/image-not-found.svg';
    } else if (e.target.dataset.fallbackTried === '1') {
      e.target.dataset.fallbackTried = '2';
      e.target.src = '/assets/images/image-not-found.png';
    }
  }
}, true);

document.addEventListener('DOMContentLoaded', () => {

  // Mobile Navigation Toggle
  const navToggle = document.getElementById('nav-toggle');
  const primaryNav = document.getElementById('primary-nav');

  if (navToggle && primaryNav) {
    let backdrop = document.querySelector('.nav-backdrop');
    if (!backdrop) {
      backdrop = document.createElement('div');
      backdrop.className = 'nav-backdrop';
      document.body.appendChild(backdrop);
    }

    const navClose = document.getElementById('nav-close');

    const toggleNav = (open) => {
      const isOpen = typeof open === 'boolean' ? open : !primaryNav.classList.contains('is-open');
      navToggle.setAttribute('aria-expanded', isOpen);
      if (isOpen) {
        primaryNav.classList.add('is-open');
        navToggle.classList.add('is-active');
        backdrop.classList.add('is-visible');
        document.body.classList.add('nav-open');
        document.documentElement.style.overflow = 'hidden';
        document.body.style.overflow = 'hidden';
      } else {
        primaryNav.classList.remove('is-open');
        navToggle.classList.remove('is-active');
        backdrop.classList.remove('is-visible');
        document.body.classList.remove('nav-open');
        document.documentElement.style.overflow = '';
        document.body.style.overflow = '';
      }
    };

    navToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleNav();
    });

    if (navClose) {
      navClose.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleNav(false);
      });
    }

    backdrop.addEventListener('click', () => {
      toggleNav(false);
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && primaryNav.classList.contains('is-open')) {
        toggleNav(false);
      }
    });

    const navLinks = primaryNav.querySelectorAll('.nav-link');
    navLinks.forEach((link) => {
      link.addEventListener('click', () => {
        if (window.innerWidth <= 768) {
          toggleNav(false);
        }
      });
    });
  }

  // Remove any stray legacy buttons inside <pre>
  document.querySelectorAll('pre > button, pre > .code-copy-btn').forEach(el => el.remove());

  // Code Copy Button Interaction
  const copyIconSvg = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
  const checkIconSvg = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>';

  document.querySelectorAll('.code-copy-btn').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const wrapper = btn.closest('.code-block-wrapper') || btn.parentElement;
      const codeEl = wrapper ? wrapper.querySelector('pre code') : null;
      if (!codeEl) return;

      try {
        await navigator.clipboard.writeText(codeEl.innerText);
        btn.classList.add('copied');
        btn.innerHTML = `${checkIconSvg}<span>Copied!</span>`;

        setTimeout(() => {
          btn.classList.remove('copied');
          btn.innerHTML = `${copyIconSvg}<span>Copy</span>`;
        }, 2000);
      } catch (err) {
        console.error('Failed to copy code: ', err);
      }
    });
  });

  // Scroll Header Effect
  const header = document.getElementById('site-header');
  if (header) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 40) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }
    });
  }

  // Clickable Cards Navigation (Project cards, Post cards, Sidebar highlights)
  document.addEventListener('click', (e) => {
    // If clicked on an interactive element, allow default behavior
    if (e.target.closest('a, button, input, textarea, select, label')) {
      return;
    }
    // If user is selecting text, do not navigate
    const selection = window.getSelection();
    if (selection && selection.toString().length > 0) {
      return;
    }
    const card = e.target.closest('.project-card, .post-card, .magazine-sidebar-item');
    if (card) {
      const targetLink = card.querySelector('a.card-link, a.read-more-link, .card-title a, .post-card-title a, .magazine-sidebar-title a, h3 a, h4 a');
      if (targetLink && targetLink.href) {
        if (e.metaKey || e.ctrlKey) {
          window.open(targetLink.href, '_blank');
        } else {
          window.location.href = targetLink.href;
        }
      }
    }
  });

  // Smooth Count-Up Animation for Stats
  const countUpElements = document.querySelectorAll('.stat-count-up, [data-target]');
  if (countUpElements.length > 0) {
    const animateCountUp = (el) => {
      const target = parseFloat(el.getAttribute('data-target'));
      if (isNaN(target)) return;

      const suffix = el.getAttribute('data-suffix') || '';
      const prefix = el.getAttribute('data-prefix') || '';
      const duration = 1800; // 1.8 seconds animation
      let startTime = null;

      const updateNumber = (timestamp) => {
        if (!startTime) startTime = timestamp;
        const elapsed = timestamp - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Cubic ease-out
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const currentVal = Math.round(easeOut * target);

        el.textContent = `${prefix}${currentVal}${suffix}`;

        if (progress < 1) {
          requestAnimationFrame(updateNumber);
        } else {
          el.textContent = `${prefix}${target}${suffix}`;
        }
      };

      requestAnimationFrame(updateNumber);
    };

    if ('IntersectionObserver' in window) {
      const countObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            animateCountUp(entry.target);
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.2 });

      countUpElements.forEach((el) => {
        // Initialize to 0 with suffix before animation triggers
        const suffix = el.getAttribute('data-suffix') || '';
        const prefix = el.getAttribute('data-prefix') || '';
        el.textContent = `${prefix}0${suffix}`;
        countObserver.observe(el);
      });
    } else {
      countUpElements.forEach((el) => animateCountUp(el));
    }
  }
});
