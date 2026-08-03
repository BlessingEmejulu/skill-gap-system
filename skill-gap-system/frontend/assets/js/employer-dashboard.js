(function () {
  
  async function loadDashboard() {
    try {
      // 1. Fetch Employer Profile
      const response = await fetch(`${window.API_BASE_URL || 'http://localhost:8001'}/api/employers/me`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('sgs_token')}` }
      });
      
      if (!response.ok) {
        throw new Error('Failed to load employer profile.');
      }
      const employer = await response.json();
      
      document.getElementById('company-name').textContent = employer.company_name || 'Your Company';
      document.getElementById('company-details').textContent = `${employer.industry || 'N/A'} • ${employer.company_size || 'N/A'} employees`;

      // 2. Fetch Jobs (List all active jobs and filter by this employer, or just show all jobs since the mock has 1 employer)
      // We will just fetch all jobs and filter manually for simplicity
      const jobsData = await API.listJobs();
      const jobs = (jobsData.items || []).filter(j => j.employer_id === employer.id);
      
      const jobsList = document.getElementById('jobs-list');
      
      if (!jobs.length) {
        jobsList.innerHTML = `
          <div class="empty-state">
            <h3>No job postings</h3>
            <p>You haven't posted any jobs yet.</p>
          </div>
        `;
        return;
      }

      jobsList.innerHTML = jobs.map(job => `
        <div class="card">
          <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:var(--space-2);">
            <div>
              <h3 style="margin:0;">${job.title}</h3>
              <p style="margin:0; font-size:0.875rem; color:var(--color-muted);">${job.location || 'Remote'} • ${job.industry}</p>
            </div>
            <span class="badge badge-success" style="font-size:1rem; padding:var(--space-1) var(--space-2);">${job.is_active === 'active' ? 'Active' : 'Closed'}</span>
          </div>
          <p style="margin-top:var(--space-2);">${job.description}</p>
          <div style="margin-top:var(--space-3); padding-top:var(--space-3); border-top:1px solid var(--color-border); font-size:0.875rem; display:flex; justify-content:space-between;">
            <span><strong>Min Experience:</strong> ${job.min_experience_years} yrs</span>
            <a href="employer-job-matches.html?id=${job.id}" style="color:var(--color-primary); font-weight:600;">View Matches &rarr;</a>
          </div>
        </div>
      `).join('');

    } catch (err) {
      console.error(err);
      alert(err.message || 'Error loading dashboard');
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

    loadDashboard();
  });
})();
