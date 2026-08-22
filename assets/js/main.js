document.addEventListener('DOMContentLoaded', () => {
  // Mobile Navigation Toggle
  const navToggle = document.getElementById('nav-toggle');
  const primaryNav = document.getElementById('primary-nav');

  if (navToggle && primaryNav) {
    navToggle.addEventListener('click', () => {
      const isExpanded = navToggle.getAttribute('aria-expanded') === 'true';
      navToggle.setAttribute('aria-expanded', !isExpanded);
      primaryNav.classList.toggle('is-open');
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
      if (primaryNav.classList.contains('is-open') && !primaryNav.contains(e.target) && !navToggle.contains(e.target)) {
        navToggle.setAttribute('aria-expanded', 'false');
        primaryNav.classList.remove('is-open');
      }
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
