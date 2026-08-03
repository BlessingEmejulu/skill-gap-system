/**
 * Shared UI behavior used across every page: mobile nav toggle,
 * scroll-reveal for .reveal elements, and a small toast helper.
 */
(function () {
  document.addEventListener('DOMContentLoaded', () => {
    // Mobile nav toggle
    const navToggle = document.querySelector('[data-nav-toggle]');
    const navLinks = document.querySelector('.nav-links');
    if (navToggle && navLinks) {
      navToggle.addEventListener('click', () => {
        const isOpen = navLinks.classList.toggle('open');
        navToggle.setAttribute('aria-expanded', String(isOpen));
      });
    }

    // Sidebar toggle (dashboard layout, mobile)
    const sidebarToggle = document.querySelector('[data-sidebar-toggle]');
    const sidebar = document.querySelector('.sidebar');
    if (sidebarToggle && sidebar) {
      // Create and inject overlay
      const overlay = document.createElement('div');
      overlay.className = 'sidebar-overlay';
      document.body.appendChild(overlay);

      function toggleSidebar() {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('open');
      }

      sidebarToggle.addEventListener('click', toggleSidebar);
      overlay.addEventListener('click', toggleSidebar);

      // Close button inside sidebar
      const sidebarClose = sidebar.querySelector('.sidebar-close');
      if (sidebarClose) {
        sidebarClose.addEventListener('click', toggleSidebar);
      }
    }

    // Scroll-reveal
    const revealEls = document.querySelectorAll('.reveal');
    if (revealEls.length && 'IntersectionObserver' in window) {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add('in-view');
              observer.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.15 }
      );
      revealEls.forEach((el) => observer.observe(el));
    } else {
      revealEls.forEach((el) => el.classList.add('in-view'));
    }

    // Logged-in nav state
    const authArea = document.querySelector('[data-auth-area]');
    if (authArea && window.API) {
      if (API.isAuthenticated()) {
        const user = API.getUser();
        authArea.innerHTML = `
          <a href="dashboard.html" class="btn btn-secondary btn-sm">Dashboard</a>
          <button class="btn btn-primary btn-sm" data-logout>Log out</button>
        `;
        const logoutBtn = authArea.querySelector('[data-logout]');
        logoutBtn.addEventListener('click', () => {
          API.clearSession();
          window.location.href = 'index.html';
        });
      }
    }
  });

  // Simple toast notifications
  window.showToast = function showToast(message, type = 'default') {
    const toast = document.createElement('div');
    toast.className = `toast ${type === 'danger' ? 'toast-danger' : type === 'success' ? 'toast-success' : ''}`;
    toast.setAttribute('role', 'status');
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
  };
})();
