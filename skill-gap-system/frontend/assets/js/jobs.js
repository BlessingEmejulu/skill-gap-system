(function () {
  let allSkills = {};

  async function loadJobs() {
    const container = document.getElementById('jobs-container');
    
    try {
      // Fetch skills map first to display skill names
      const skillsResponse = await API.listSkills();
      skillsResponse.forEach(s => {
        allSkills[s.id] = s.name;
      });

      const jobsData = await API.listJobs();
      const jobs = jobsData.items || [];

      if (!jobs.length) {
        container.innerHTML = `
          <div class="empty-state">
            <h3>No jobs found</h3>
            <p>There are no active jobs available at the moment. Please check back later.</p>
          </div>`;
        return;
      }

      container.innerHTML = '';
      
      // Load all match percentages concurrently
      const matchPromises = jobs.map(async (job) => {
        try {
          const matchData = await API.getJobMatch(job.id);
          return { job, matchData };
        } catch (e) {
          console.error("Failed to load match for job", job.id, e);
          return { job, matchData: null };
        }
      });

      const matchedJobs = await Promise.all(matchPromises);

      // Render jobs
      matchedJobs.forEach(({ job, matchData }) => {
        let matchPercent = 0;
        let missingSkillIds = [];
        
        if (matchData) {
          matchPercent = Math.round(matchData.match_percentage);
          if (matchData.missing_skill_ids) {
            try {
              missingSkillIds = JSON.parse(matchData.missing_skill_ids);
            } catch (e) {
              console.error("Failed to parse missing skills", e);
            }
          }
        }

        const badgeClass = matchPercent >= 80 ? 'badge-success' : matchPercent >= 50 ? 'badge-warning' : 'badge-danger';
        
        let missingSkillsHtml = '';
        if (missingSkillIds.length > 0) {
          const missingNames = missingSkillIds.map(id => allSkills[id] || `Skill #${id}`).join(', ');
          missingSkillsHtml = `<p style="font-size:0.875rem; color:var(--color-danger); margin-top:var(--space-2);"><strong>Missing skills:</strong> ${missingNames}</p>`;
        } else {
          missingSkillsHtml = `<p style="font-size:0.875rem; color:var(--color-success); margin-top:var(--space-2);">You have all required skills!</p>`;
        }

        const jobCard = document.createElement('div');
        jobCard.className = 'card';
        jobCard.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:var(--space-2);">
            <div>
              <h3 style="margin:0;">${job.title}</h3>
              <p style="margin:0; font-size:0.875rem; color:var(--color-muted);">${job.industry} &bull; ${job.location || 'Remote'}</p>
            </div>
            <span class="badge ${badgeClass}" style="font-size:1rem; padding:var(--space-1) var(--space-2);">${matchPercent}% Match</span>
          </div>
          <p style="margin-top:var(--space-2);">${job.description}</p>
          <p style="font-size:0.875rem; color:var(--color-muted); margin-top:var(--space-2);">Min. Experience: ${job.min_experience_years} years</p>
          ${missingSkillsHtml}
          <div style="margin-top:var(--space-3);">
            <button class="btn btn-primary btn-sm">Apply Now</button>
          </div>
        `;
        container.appendChild(jobCard);
      });

    } catch (err) {
      container.innerHTML = `
        <div class="empty-state">
          <h3>Error loading jobs</h3>
          <p>${err.message}</p>
        </div>`;
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    if (!API.isAuthenticated()) {
      window.location.href = 'login.html';
      return;
    }

    document.getElementById('logout-btn').addEventListener('click', () => {
      API.clearSession();
      window.location.href = 'index.html';
    });

    loadJobs();
  });
})();
