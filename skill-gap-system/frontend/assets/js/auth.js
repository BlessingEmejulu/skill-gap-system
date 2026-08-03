/**
 * Handles the login.html page: tab switching between login/register,
 * client-side validation, and wiring both forms to the API.
 */
(function () {
  function switchTab(tab) {
    const isLogin = tab === 'login';
    document.getElementById('tab-login').setAttribute('aria-selected', String(isLogin));
    document.getElementById('tab-register').setAttribute('aria-selected', String(!isLogin));
    document.getElementById('tab-login').style.background = isLogin ? 'var(--color-primary)' : 'transparent';
    document.getElementById('tab-login').style.color = isLogin ? '#fff' : 'var(--color-text)';
    document.getElementById('tab-register').style.background = !isLogin ? 'var(--color-primary)' : 'transparent';
    document.getElementById('tab-register').style.color = !isLogin ? '#fff' : 'var(--color-text)';
    document.getElementById('panel-login').hidden = !isLogin;
    document.getElementById('panel-register').hidden = isLogin;
  }

  function setFieldError(inputId, message) {
    const errorEl = document.getElementById(`${inputId}-error`);
    const input = document.getElementById(inputId);
    if (!errorEl || !input) return;
    if (message) {
      errorEl.textContent = message;
      errorEl.hidden = false;
      input.closest('.field').classList.add('has-error');
    } else {
      errorEl.hidden = true;
      input.closest('.field').classList.remove('has-error');
    }
  }

  function setLoading(buttonId, isLoading, label) {
    const btn = document.getElementById(buttonId);
    if (!btn) return;
    btn.disabled = isLoading;
    btn.textContent = isLoading ? 'Please wait…' : label;
  }

  document.addEventListener('DOMContentLoaded', () => {
    // Redirect already-logged-in users based on their role
    if (API.isAuthenticated()) {
      const user = API.getUser();
      if (user && user.role === 'employer') {
        window.location.href = 'employer-dashboard.html';
      } else if (user && (user.role === 'admin' || user.role === 'researcher')) {
        window.location.href = 'analytics.html';
      } else {
        window.location.href = 'dashboard.html';
      }
      return;
    }

    const params = new URLSearchParams(window.location.search);
    switchTab(params.get('tab') === 'register' ? 'register' : 'login');

    document.getElementById('tab-login').addEventListener('click', () => switchTab('login'));
    document.getElementById('tab-register').addEventListener('click', () => switchTab('register'));

    // --- Login form ---
    document.getElementById('panel-login').addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('login-email').value.trim();
      const password = document.getElementById('login-password').value;

      setFieldError('login-email', !email ? 'Enter your email address.' : '');
      setFieldError('login-password', !password ? 'Enter your password.' : '');
      if (!email || !password) return;

      setLoading('login-submit', true, 'Log in');
      try {
        const result = await API.login({ email, password });
        API.setSession(result.access_token);
        const user = await API.me();
        API.setSession(result.access_token, user);
        alert('Welcome back!');
        if (user.role === 'employer') {
          window.location.href = 'employer-dashboard.html';
        } else if (user.role === 'admin' || user.role === 'researcher') {
          window.location.href = 'analytics.html';
        } else {
          window.location.href = 'dashboard.html';
        }
      } catch (err) {
        alert(err.message || 'Could not log in.');
      } finally {
        setLoading('login-submit', false, 'Log in');
      }
    });

    // --- Register form ---
    document.getElementById('panel-register').addEventListener('submit', async (e) => {
      e.preventDefault();
      const full_name = document.getElementById('register-name').value.trim();
      const email = document.getElementById('register-email').value.trim();
      const password = document.getElementById('register-password').value;
      const role = document.getElementById('register-role').value;

      setFieldError('register-name', full_name.length < 2 ? 'Enter your full name.' : '');
      setFieldError('register-email', !email ? 'Enter a valid email address.' : '');
      setFieldError('register-password', password.length < 8 ? 'Use at least 8 characters.' : '');
      if (full_name.length < 2 || !email || password.length < 8) return;

      setLoading('register-submit', true, 'Create account');
      try {
        await API.register({ full_name, email, password, role });
        const result = await API.login({ email, password });
        API.setSession(result.access_token);
        const user = await API.me();
        API.setSession(result.access_token, user);
        alert('Account created — welcome!');
        if (user.role === 'employer') {
          window.location.href = 'employer-dashboard.html';
        } else if (user.role === 'admin' || user.role === 'researcher') {
          window.location.href = 'analytics.html';
        } else {
          window.location.href = 'dashboard.html';
        }
      } catch (err) {
        // The login page doesn't have the toast component, so we use a simple alert.
        alert(err.message || 'Could not create your account.');
      } finally {
        setLoading('register-submit', false, 'Create account');
      }
    });

    // --- Forgot password ---
    document.getElementById('forgot-password-link').addEventListener('click', async (e) => {
      e.preventDefault();
      const email = document.getElementById('login-email').value.trim();
      if (!email) {
        setFieldError('login-email', 'Enter your email address first.');
        return;
      }
      try {
        await API.forgotPassword(email);
        alert('If that email is registered, a reset link has been sent.');
      } catch (err) {
        alert(err.message || 'Something went wrong.');
      }
    });
  });
})();
