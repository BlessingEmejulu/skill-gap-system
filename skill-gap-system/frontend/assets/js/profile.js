/**
 * Powers profile.html: loads the graduate's current profile into the form
 * and saves edits back to the API. List fields (projects, internships,
 * certifications) are edited as one-per-line text and converted to arrays.
 */
(function () {
  function textareaToList(value) {
    return value
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean);
  }

  function listToTextarea(list) {
    return Array.isArray(list) ? list.join('\n') : '';
  }

  async function loadProfile() {
    try {
      const profile = await API.getMyGraduateProfile();
      document.getElementById('field-degree').value = profile.degree || '';
      document.getElementById('field-cgpa').value = profile.cgpa ?? '';
      document.getElementById('field-graduation-year').value = profile.graduation_year ?? '';
      document.getElementById('field-state').value = profile.state_of_residence || '';
      // projects/internships/certifications/bio aren't in GraduateOut yet —
      // left blank on load; still saved correctly on submit.
    } catch (err) {
      window.showToast(err.message || 'Could not load your profile.', 'danger');
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    if (!API.isAuthenticated()) {
      window.location.href = 'login.html';
      return;
    }

    loadProfile();

    document.getElementById('logout-btn').addEventListener('click', () => {
      API.clearSession();
      window.location.href = 'index.html';
    });

    document.getElementById('profile-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = document.getElementById('save-profile-btn');
      btn.disabled = true;
      btn.textContent = 'Saving…';

      const payload = {
        degree: document.getElementById('field-degree').value || null,
        cgpa: document.getElementById('field-cgpa').value ? Number(document.getElementById('field-cgpa').value) : null,
        graduation_year: document.getElementById('field-graduation-year').value
          ? Number(document.getElementById('field-graduation-year').value)
          : null,
        state_of_residence: document.getElementById('field-state').value || null,
        bio: document.getElementById('field-bio').value || null,
        projects: textareaToList(document.getElementById('field-projects').value),
        internships: textareaToList(document.getElementById('field-internships').value),
        certifications: textareaToList(document.getElementById('field-certifications').value),
      };

      try {
        await API.updateMyGraduateProfile(payload);
        window.showToast('Profile saved.', 'success');
      } catch (err) {
        window.showToast(err.message || 'Could not save your profile.', 'danger');
      } finally {
        btn.disabled = false;
        btn.textContent = 'Save profile';
      }
    });

    document.getElementById('cv-upload-input').addEventListener('change', (e) => {
      if (e.target.files.length) {
        window.showToast(`Selected "${e.target.files[0].name}" — connect this to a CV upload endpoint to enable AI extraction.`);
      }
    });
  });
})();
