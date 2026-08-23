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
      backdrop.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;width:100%;height:100%;background:rgba(28,27,24,0.5);backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px);opacity:0;pointer-events:none;transition:opacity 0.25s ease;z-index:1040;';
      document.body.appendChild(backdrop);
    }

    const toggleNav = (open) => {
      const isOpen = typeof open === 'boolean' ? open : !primaryNav.classList.contains('is-open');
      navToggle.setAttribute('aria-expanded', isOpen);
      if (isOpen) {
        primaryNav.classList.add('is-open');
        navToggle.classList.add('is-active');
        backdrop.style.opacity = '1';
        backdrop.style.pointerEvents = 'auto';
        document.documentElement.style.overflow = 'hidden';
        document.body.style.overflow = 'hidden';
      } else {
        primaryNav.classList.remove('is-open');
        navToggle.classList.remove('is-active');
        backdrop.style.opacity = '0';
        backdrop.style.pointerEvents = 'none';
        document.documentElement.style.overflow = '';
        document.body.style.overflow = '';
      }
    };

    navToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleNav();
    });

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
});
