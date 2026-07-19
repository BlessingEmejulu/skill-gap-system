/**
 * Powers analytics.html. Admin/Researcher only — the API returns 403 for
 * other roles, in which case we show an explanatory empty state instead
 * of a broken dashboard.
 */
(function () {
  function barChart(canvasId, labels, data, label, color) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || typeof Chart === 'undefined') return;
    new Chart(canvas, {
      type: 'bar',
      data: {
        labels: labels.length ? labels : ['No data yet'],
        datasets: [
          {
            label,
            data: data.length ? data : [0],
            backgroundColor: color,
            borderRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } },
      },
    });
  }

  function showRestricted() {
    document.getElementById('analytics-content').innerHTML = `
      <div class="empty-state card">
        <h3>Analytics is restricted</h3>
        <p>This dashboard is available to Administrator and Researcher accounts. Log in with one of those roles to view labour market analytics.</p>
      </div>`;
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

    try {
      const overview = await API.analyticsOverview();

      barChart(
        'top-skills-chart',
        overview.top_demanded_skills.map((s) => s.skill),
        overview.top_demanded_skills.map((s) => s.demand),
        'Demand',
        '#2563EB'
      );
      barChart(
        'skill-gaps-chart',
        overview.most_common_gaps.map((s) => s.skill),
        overview.most_common_gaps.map((s) => s.count),
        'Gap count',
        '#EF4444'
      );
      barChart(
        'distribution-chart',
        overview.graduate_distribution_by_university.map((u) => u.university),
        overview.graduate_distribution_by_university.map((u) => u.graduate_count),
        'Graduates',
        '#22C55E'
      );
    } catch (err) {
      if (err.status === 403) {
        showRestricted();
      } else {
        window.showToast(err.message || 'Could not load analytics.', 'danger');
      }
    }
  });
})();
