/**
 * Powers assessment.html: lists every skill in the taxonomy as a slider
 * the graduate can self-rate, filtered by category, and saves each rating
 * via the graduates/me/skills endpoint (debounced on slider release).
 */
(function () {
  let allSkills = [];
  let userSkillsMap = {};

  function categoryLabel(category) {
    return category.replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  }

  function renderSkills(filter) {
    const container = document.getElementById('skills-container');
    const filtered = filter === 'all' ? allSkills : allSkills.filter((s) => s.category === filter);

    if (!filtered.length) {
      container.innerHTML = `
        <div class="empty-state">
          <h3>No skills in this category yet</h3>
          <p>An administrator can add skills to the taxonomy from the admin panel.</p>
        </div>`;
      return;
    }

    container.innerHTML = filtered
      .map(
        (skill) => {
          const val = userSkillsMap[skill.id] || 0;
          return `
        <div class="card" style="margin-bottom:var(--space-3); padding:var(--space-3);">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:var(--space-2);">
            <div>
              <strong>${escapeHtml(skill.name)}</strong>
              <div style="font-size:0.75rem; color:var(--color-muted);">${categoryLabel(skill.category)}</div>
            </div>
            <span id="value-${skill.id}" style="font-weight:600; color:var(--color-primary);">${val}%</span>
          </div>
          <input
            type="range" min="0" max="100" value="${val}"
            id="slider-${skill.id}"
            data-skill-id="${skill.id}"
            aria-label="Proficiency in ${escapeHtml(skill.name)}"
            style="width:100%;"
          />
        </div>`;
        }
      )
      .join('');

    filtered.forEach((skill) => {
      const slider = document.getElementById(`slider-${skill.id}`);
      const valueLabel = document.getElementById(`value-${skill.id}`);
      slider.addEventListener('input', () => {
        valueLabel.textContent = `${slider.value}%`;
      });
      slider.addEventListener('change', () => saveSkill(skill.id, Number(slider.value)));
    });
  }

  async function saveSkill(skillId, proficiency) {
    try {
      await API.addMySkill(skillId, proficiency);
      window.showToast('Skill rating saved.', 'success');
    } catch (err) {
      window.showToast(err.message || 'Could not save that rating.', 'danger');
    }
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  document.addEventListener('DOMContentLoaded', async () => {
    if (!API.isAuthenticated()) {
      window.location.href = 'login.html';
      return;
    }

    document.getElementById('logout-btn').addEventListener('click', () => {
      API.clearSession();
      window.location.href = 'index.html';
    });

    document.getElementById('category-filter').addEventListener('change', (e) => {
      renderSkills(e.target.value);
    });

    try {
      const [skillsResponse, profileResponse] = await Promise.all([
        API.listSkills(),
        API.getMyGraduateProfile()
      ]);
      
      allSkills = skillsResponse;
      
      if (profileResponse.skills) {
        profileResponse.skills.forEach(s => {
          userSkillsMap[s.skill_id] = s.proficiency;
        });
      }

      if (!allSkills.length) {
        document.getElementById('skills-container').innerHTML = `
          <div class="empty-state">
            <h3>No skills in the taxonomy yet</h3>
            <p>Ask an administrator to add skills, or check back once the platform is seeded.</p>
          </div>`;
        return;
      }
      renderSkills('all');
    } catch (err) {
      window.showToast(err.message || 'Could not load skills.', 'danger');
    }
  });
})();
