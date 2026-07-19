/**
 * Powers reports.html: triggers PDF/Excel generation and lists past
 * reports. Downloads are authenticated, so we fetch the file as a blob
 * (a plain <a href> can't carry an Authorization header) and save it.
 */
(function () {
  async function downloadReport(reportId, filename) {
    try {
      const response = await fetch(API_BASE_FOR_DOWNLOAD(reportId), {
        headers: { Authorization: `Bearer ${localStorage.getItem('sgs_token')}` },
      });
      if (!response.ok) throw new Error('Download failed.');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename || `report-${reportId}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      window.showToast(err.message || 'Could not download report.', 'danger');
    }
  }

  function API_BASE_FOR_DOWNLOAD(reportId) {
    return API.reportDownloadUrl(reportId);
  }

  function renderReports(reports) {
    const list = document.getElementById('reports-list');
    if (!reports.length) {
      list.innerHTML = `
        <div class="empty-state">
          <h3>No reports yet</h3>
          <p>Generate a PDF or Excel report above to see it here.</p>
        </div>`;
      return;
    }
    list.innerHTML = reports
      .map(
        (r) => `
        <div class="card" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:var(--space-2); padding:var(--space-3);">
          <div>
            <strong>${r.report_type.replace('_', ' ')} report</strong>
            <div style="font-size:0.75rem; color:var(--color-muted);">${r.file_format.toUpperCase()} · ${r.status}</div>
          </div>
          <button class="btn btn-secondary btn-sm" data-download="${r.id}" ${r.status !== 'ready' ? 'disabled' : ''}>Download</button>
        </div>`
      )
      .join('');

    list.querySelectorAll('[data-download]').forEach((btn) => {
      btn.addEventListener('click', () => downloadReport(btn.dataset.download));
    });
  }

  async function loadReports() {
    try {
      const reports = await API.myReports();
      renderReports(reports);
    } catch (err) {
      window.showToast(err.message || 'Could not load reports.', 'danger');
    }
  }

  async function generate(fileFormat, btn) {
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Generating…';
    try {
      await API.generateReport(fileFormat);
      window.showToast('Report generated.', 'success');
      loadReports();
    } catch (err) {
      if (err.status === 403) {
        window.showToast('Reports are available to Administrator and Researcher accounts.', 'danger');
      } else {
        window.showToast(err.message || 'Could not generate report.', 'danger');
      }
    } finally {
      btn.disabled = false;
      btn.textContent = originalText;
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

    loadReports();

    document.getElementById('generate-pdf-btn').addEventListener('click', (e) => generate('pdf', e.currentTarget));
    document.getElementById('generate-xlsx-btn').addEventListener('click', (e) => generate('xlsx', e.currentTarget));
  });
})();
