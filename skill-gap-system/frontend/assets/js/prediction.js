/**
 * Powers prediction.html: shows the latest score as a ring, lets the
 * graduate re-run the model, and lists prediction history in a table.
 */
(function () {
  function riskBadgeClass(risk) {
    if (risk === 'low') return 'badge-low';
    if (risk === 'medium') return 'badge-medium';
    return 'badge-high';
  }

  function updateScoreDisplay(prediction) {
    document.getElementById('score-value').textContent = `${prediction.employability_score}%`;
    document.getElementById('score-ring').style.background =
      `conic-gradient(var(--color-primary) ${prediction.employability_score}%, var(--color-border) 0)`;
    const badge = document.getElementById('risk-badge');
    badge.hidden = false;
    badge.textContent = `${prediction.risk_level} risk`;
    badge.className = `badge ${riskBadgeClass(prediction.risk_level)}`;
    document.getElementById('score-explainer').textContent =
      `Employment probability: ${(prediction.employment_probability * 100).toFixed(1)}%. ` +
      `Update your profile and skills, then re-run to see how your score changes.`;
  }

  function renderHistoryTable(history) {
    const body = document.getElementById('history-table-body');
    if (!history.length) {
      body.innerHTML = `<tr><td colspan="4" style="padding:16px 8px; color:var(--color-muted);">No predictions yet — run your first one above.</td></tr>`;
      return;
    }
    body.innerHTML = history
      .map(
        (p) => `
        <tr style="border-bottom:1px solid var(--color-border);">
          <td style="padding:10px 8px;">${new Date(p.created_at || Date.now()).toLocaleDateString()}</td>
          <td style="padding:10px 8px;">${p.employability_score}%</td>
          <td style="padding:10px 8px;">${(p.employment_probability * 100).toFixed(1)}%</td>
          <td style="padding:10px 8px;"><span class="badge ${riskBadgeClass(p.risk_level)}">${p.risk_level}</span></td>
        </tr>`
      )
      .join('');
  }

  async function loadHistory() {
    try {
      const history = await API.predictionHistory();
      renderHistoryTable(history);
      if (history.length) updateScoreDisplay(history[0]);
    } catch (err) {
      window.showToast(err.message || 'Could not load prediction history.', 'danger');
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

    loadHistory();

    document.getElementById('run-prediction-btn').addEventListener('click', async (e) => {
      const btn = e.currentTarget;
      btn.disabled = true;
      btn.textContent = 'Running…';
      try {
        const result = await API.runPrediction();
        updateScoreDisplay(result);
        window.showToast('Prediction complete.', 'success');
        loadHistory();
      } catch (err) {
        window.showToast(err.message || 'Could not run prediction.', 'danger');
      } finally {
        btn.disabled = false;
        btn.textContent = 'Run new prediction';
      }
    });
  });
})();
