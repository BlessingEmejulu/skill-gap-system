(function () {
  let allSkills = {};

  async function loadData() {
    const urlParams = new URLSearchParams(window.location.search);
    const jobId = urlParams.get('id');

    if (!jobId) {
      alert("No Job ID specified.");
      window.location.href = 'employer-dashboard.html';
      return;
    }

    try {
      // Load skills mapping for displaying missing skills nicely
      const skillsResponse = await API.listSkills();
      skillsResponse.forEach(s => {
        allSkills[s.id] = s.name;
      });

      // Load Job Details
      const job = await API.getJob(jobId);
      document.getElementById('job-title').textContent = job.title;
      document.getElementById('job-details').textContent = `${job.industry || 'N/A'} • ${job.location || 'Remote'} • Min Exp: ${job.min_experience_years} yrs`;

      // Load Matches
      const matchesData = await API.getEmployerJobMatches(jobId);
      const matches = matchesData.matches || [];
      
      const matchesList = document.getElementById('matches-list');

      if (!matches.length) {
        matchesList.innerHTML = `
          <div class="empty-state" style="text-align:center; padding: 40px 0;">
            <p>No graduates match this job yet.</p>
          </div>
        `;
        return;
      }

      matchesList.innerHTML = matches.map((match, index) => {
        const badgeClass = match.match_percentage >= 80 ? 'badge-success' : match.match_percentage >= 50 ? 'badge-warning' : 'badge-danger';
        
        let missingSkillsHtml = '';
        if (match.missing_skill_ids && match.missing_skill_ids.length > 0) {
          const missingNames = match.missing_skill_ids.map(id => allSkills[id] || `Skill #${id}`).join(', ');
          missingSkillsHtml = `<p style="font-size:0.875rem; color:var(--color-danger); margin-top:var(--space-2);"><strong>Missing:</strong> ${missingNames}</p>`;
        } else {
          missingSkillsHtml = `<p style="font-size:0.875rem; color:var(--color-success); margin-top:var(--space-2);">Matches all required skills!</p>`;
        }

        return `
          <div class="match-row">
            <div>
              <div style="display:flex; align-items:center; gap:var(--space-2); margin-bottom:var(--space-1);">
                <strong style="font-size:1.1rem;">#${index + 1} - ${match.full_name}</strong>
                <a href="mailto:${match.email}" style="font-size:0.85rem; color:var(--color-primary);">${match.email}</a>
              </div>
              ${missingSkillsHtml}
            </div>
            <div style="text-align:right;">
              <div class="badge ${badgeClass}" style="font-size:1.1rem; padding:var(--space-1) var(--space-2);">
                ${match.match_percentage}% Match
              </div>
            </div>
          </div>
        `;
      }).join('');

    } catch (err) {
      console.error(err);
      alert(err.message || 'Error loading matches');
    }
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

    loadData();
  });
})();
