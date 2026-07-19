/**
 * Powers dashboard.html: requires auth, loads the graduate's profile,
 * prediction history, and recommendations, and renders the Chart.js graph.
 */
(function () {
  function requireAuth() {
    if (!API.isAuthenticated()) {
      window.location.href = 'login.html';
      return false;
    }
    return true;
  }

  function riskBadgeClass(risk) {
    if (risk === 'low') return 'badge-low';
    if (risk === 'medium') return 'badge-medium';
    return 'badge-high';
  }

  async function loadOverview() {
    const user = API.getUser();
    if (user) {
      document.getElementById('welcome-heading').textContent = `Welcome back, ${user.full_name.split(' ')[0]}`;
    }

    try {
      const [profile, history, recs] = await Promise.all([
        API.getMyGraduateProfile(),
        API.predictionHistory().catch(() => []),
        API.myRecommendations().catch(() => []),
      ]);

      document.getElementById('stat-cgpa').textContent = profile.cgpa != null ? profile.cgpa.toFixed(2) : '—';
      document.getElementById('stat-recs').textContent = recs.length;

      if (history.length) {
        const latest = history[0];
        document.getElementById('stat-score').textContent = `${latest.employability_score}%`;
        const badge = document.getElementById('stat-risk-badge');
        badge.hidden = false;
        badge.textContent = `${latest.risk_level} risk`;
        badge.className = `badge ${riskBadgeClass(latest.risk_level)}`;
      } else {
        document.getElementById('stat-score').textContent = '—';
      }

      renderHistoryChart(history);
      renderRecommendations(recs);
    } catch (err) {
      window.showToast(err.message || 'Could not load your dashboard.', 'danger');
    }
  }

  function renderHistoryChart(history) {
    const canvas = document.getElementById('history-chart');
    if (!canvas || typeof Chart === 'undefined') return;

    const ordered = [...history].reverse();
    const labels = ordered.map((_, i) => `Attempt ${i + 1}`);
    const scores = ordered.map((p) => p.employability_score);

    new Chart(canvas, {
      type: 'line',
      data: {
        labels: labels.length ? labels : ['No predictions yet'],
        datasets: [
          {
            label: 'Employability score',
            data: scores.length ? scores : [0],
            borderColor: '#2563EB',
            backgroundColor: 'rgba(37, 99, 235, 0.12)',
            tension: 0.35,
            fill: true,
            pointRadius: 4,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { min: 0, max: 100 } },
      },
    });
  }

  function renderRecommendations(recs) {
    const container = document.getElementById('recommendations-list');
    if (!recs.length) {
      container.innerHTML = `
        <div class="empty-state">
          <h3>No recommendations yet</h3>
          <p>Generate personalized suggestions based on your current profile.</p>
        </div>`;
      return;
    }
    container.innerHTML = recs
      .slice(0, 6)
      .map(
        (rec) => `
        <div class="card" style="margin-bottom:var(--space-2); padding:var(--space-3);">
          <div style="display:flex; justify-content:space-between; gap:var(--space-3);">
            <div>
              <strong>${escapeHtml(rec.title)}</strong>
              <p style="margin:4px 0 0; font-size:0.875rem;">${escapeHtml(rec.detail || '')}</p>
            </div>
            <span class="badge badge-low" style="white-space:nowrap;">${escapeHtml(rec.category.replace('_', ' '))}</span>
          </div>
        </div>`
      )
      .join('');
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  document.addEventListener('DOMContentLoaded', () => {
    if (!requireAuth()) return;
    loadOverview();

    document.getElementById('logout-btn').addEventListener('click', () => {
      API.clearSession();
      window.location.href = 'index.html';
    });

    document.getElementById('run-prediction-btn').addEventListener('click', async (e) => {
      const btn = e.currentTarget;
      btn.disabled = true;
      btn.textContent = 'Running…';
      try {
        const result = await API.runPrediction();
        const resultBox = document.getElementById('prediction-result');
        resultBox.hidden = false;
        document.getElementById('prediction-score-label').textContent = `${result.employability_score}%`;
        document.getElementById('prediction-progress').style.width = `${result.employability_score}%`;
        window.showToast('Prediction updated.', 'success');
        loadOverview();
      } catch (err) {
        window.showToast(err.message || 'Could not run prediction.', 'danger');
      } finally {
        btn.disabled = false;
        btn.textContent = 'Run prediction';
      }
    });

    document.getElementById('generate-recs-btn').addEventListener('click', async (e) => {
      const btn = e.currentTarget;
      btn.disabled = true;
      btn.textContent = 'Generating…';
      try {
        await API.generateRecommendations();
        window.showToast('New recommendations generated.', 'success');
        loadOverview();
      } catch (err) {
        window.showToast(err.message || 'Could not generate recommendations.', 'danger');
      } finally {
        btn.disabled = false;
        btn.textContent = 'Generate new';
      }
    });
  });
})();
