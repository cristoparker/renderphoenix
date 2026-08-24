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

  // Code Copy Button
  const codeBlocks = document.querySelectorAll('pre code');
  codeBlocks.forEach((codeBlock) => {
    const pre = codeBlock.parentElement;
    if (!pre) return;

    const copyBtn = document.createElement('button');
    copyBtn.className = 'code-copy-btn';
    copyBtn.type = 'button';
    copyBtn.innerText = 'Copy';
    copyBtn.setAttribute('aria-label', 'Copy code to clipboard');

    copyBtn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(codeBlock.innerText);
        copyBtn.innerText = 'Copied!';
        setTimeout(() => { copyBtn.innerText = 'Copy'; }, 2000);
      } catch (err) {
        copyBtn.innerText = 'Error';
      }
    });

    pre.style.position = 'relative';
    pre.appendChild(copyBtn);
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
});
