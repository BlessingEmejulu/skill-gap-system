/**
 * Light/dark theme toggle. Persists the choice and respects the user's
 * OS-level preference on first visit.
 */
(function () {
  const STORAGE_KEY = 'sgs_theme';

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    const toggle = document.querySelector('[data-theme-toggle]');
    if (toggle) {
      toggle.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
      toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
  }

  function initTheme() {
    const saved = localStorage.getItem(STORAGE_KEY);
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    applyTheme(saved || (prefersDark ? 'dark' : 'light'));
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    localStorage.setItem(STORAGE_KEY, next);
    applyTheme(next);
  }

  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    const toggle = document.querySelector('[data-theme-toggle]');
    if (toggle) toggle.addEventListener('click', toggleTheme);
  });
})();
