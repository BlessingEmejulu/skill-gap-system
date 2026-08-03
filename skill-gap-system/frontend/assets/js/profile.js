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
      document.getElementById('field-projects').value = listToTextarea(profile.projects);
      document.getElementById('field-internships').value = listToTextarea(profile.internships);
      document.getElementById('field-bio').value = profile.bio || '';
      
      // Handle Certifications
      if (profile.certifications && Array.isArray(profile.certifications)) {
        const certCheckboxes = document.querySelectorAll('input[name="certifications"]');
        const customCerts = [];
        
        profile.certifications.forEach(cert => {
          let found = false;
          certCheckboxes.forEach(cb => {
            if (cb.value === cert) {
              cb.checked = true;
              found = true;
            }
          });
          if (!found && cert.trim() !== "") {
            customCerts.push(cert);
          }
        });
        
        if (customCerts.length > 0) {
          document.getElementById('field-certifications-other').value = customCerts.join(', ');
        }
      }
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
        certifications: (() => {
          const selected = Array.from(document.querySelectorAll('input[name="certifications"]:checked')).map(cb => cb.value);
          const otherCerts = document.getElementById('field-certifications-other').value;
          if (otherCerts) {
            otherCerts.split(',').forEach(c => {
              if (c.trim()) selected.push(c.trim());
            });
          }
          return selected;
        })(),
      };

      try {
        await API.updateMyGraduateProfile(payload);
        // Automatically run a new prediction in the background so dashboard stays up to date
        API.runPrediction().catch(e => console.error('Auto-prediction failed:', e));
        
        window.showToast('Profile saved.', 'success');
      } catch (err) {
        window.showToast(err.message || 'Could not save your profile.', 'danger');
      } finally {
        btn.disabled = false;
        btn.textContent = 'Save profile';
      }
    });

    document.getElementById('cv-upload-input').addEventListener('change', async (e) => {
      if (e.target.files.length) {
        const file = e.target.files[0];
        window.showToast(`Uploading "${file.name}"...`, 'info');
        try {
          const result = await API.uploadCV(file);
          window.showToast(result.message || 'CV uploaded and processed!', 'success');
          // Optionally reload the profile or show extracted skills
        } catch (err) {
          window.showToast(err.message || 'CV upload failed.', 'danger');
        }
      }
    });
  });
})();
