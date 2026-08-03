(function () {
  let allSkills = [];

  async function loadSkills() {
    try {
      allSkills = await API.listSkills();
      // Add one empty row by default
      addSkillRow();
    } catch (err) {
      console.error('Failed to load skills:', err);
      alert('Could not load skills list from the server.');
    }
  }

  function createSkillOptions() {
    return allSkills.map(s => `<option value="${s.id}">${s.name} (${s.category})</option>`).join('');
  }

  function addSkillRow() {
    const container = document.getElementById('skills-container');
    const row = document.createElement('div');
    row.className = 'skill-row';
    
    row.innerHTML = `
      <div>
        <label style="font-size: 0.85rem; font-weight:600; display:block; margin-bottom: 4px;">Skill</label>
        <select class="input skill-select" required>
          <option value="" disabled selected>Select a skill...</option>
          ${createSkillOptions()}
        </select>
      </div>
      <div>
        <label style="font-size: 0.85rem; font-weight:600; display:block; margin-bottom: 4px;">Importance (1-5)</label>
        <div style="display:flex; align-items:center; gap: 8px;">
          <input type="range" class="skill-importance input" min="1" max="5" value="3" style="flex:1;" />
          <span class="importance-val" style="font-weight:bold; width:20px; text-align:center;">3</span>
        </div>
      </div>
      <div>
        <label style="font-size: 0.85rem; font-weight:600; display:block; margin-bottom: 4px;">Type</label>
        <select class="input skill-required" required>
          <option value="required" selected>Required</option>
          <option value="preferred">Preferred</option>
        </select>
      </div>
      <div style="flex: 0 0 auto; margin-top:20px;">
        <button type="button" class="btn btn-secondary btn-sm remove-skill-btn" aria-label="Remove skill" style="color:var(--color-danger); border-color:var(--color-danger);">
          &times; Remove
        </button>
      </div>
    `;

    // Update range value display
    const range = row.querySelector('.skill-importance');
    const valDisplay = row.querySelector('.importance-val');
    range.addEventListener('input', (e) => {
      valDisplay.textContent = e.target.value;
    });

    // Remove button
    row.querySelector('.remove-skill-btn').addEventListener('click', () => {
      container.removeChild(row);
    });

    container.appendChild(row);
  }

  document.addEventListener('DOMContentLoaded', () => {
    if (!API.isAuthenticated()) {
      window.location.href = 'login.html';
      return;
    }

    const user = API.getUser();
    if (user && user.role !== 'employer') {
      window.location.href = 'dashboard.html';
      return;
    }

    document.getElementById('logout-btn').addEventListener('click', () => {
      API.clearSession();
      window.location.href = 'index.html';
    });

    document.getElementById('add-skill-btn').addEventListener('click', addSkillRow);

    document.getElementById('job-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = document.getElementById('submit-job-btn');
      
      const payload = {
        title: document.getElementById('job-title').value.trim(),
        industry: document.getElementById('job-industry').value.trim(),
        location: document.getElementById('job-location').value.trim(),
        min_experience_years: parseFloat(document.getElementById('job-experience').value),
        description: document.getElementById('job-description').value.trim(),
        required_skills: []
      };

      const rows = document.querySelectorAll('.skill-row');
      rows.forEach(row => {
        const skillId = row.querySelector('.skill-select').value;
        const importance = parseFloat(row.querySelector('.skill-importance').value);
        const isRequired = row.querySelector('.skill-required').value;
        
        if (skillId) {
          payload.required_skills.push({
            skill_id: parseInt(skillId, 10),
            importance: importance,
            is_required: isRequired
          });
        }
      });

      if (payload.required_skills.length === 0) {
        alert("Please add at least one required skill.");
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = 'Posting...';

      try {
        await API.createJob(payload);
        alert("Job posted successfully!");
        window.location.href = 'employer-dashboard.html';
      } catch (err) {
        alert(err.message || 'Error posting job.');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Post Job';
      }
    });

    loadSkills();
  });
})();
