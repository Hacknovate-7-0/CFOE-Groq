const statusEl = document.getElementById("status");
const logPanel = document.getElementById("log-panel");
const logOutput = document.getElementById("log-output");
const latestEl = document.getElementById("latest-result");
const historyBody = document.getElementById("history-body");
const metricsEl = document.getElementById("metrics");
const filterEl = document.getElementById("risk-filter");
const searchEl = document.getElementById("search");
const compareBox = document.getElementById("compare-box");
const downloadDialog = document.getElementById("download-dialog");
const downloadAuditSelect = document.getElementById("download-audit-select");
const downloadFormatSelect = document.getElementById("download-format-select");
const downloadOpenBtn = document.getElementById("download-open-btn");
const downloadCancelBtn = document.getElementById("download-cancel-btn");
const infoDialog = document.getElementById("info-dialog");
const infoContent = document.getElementById("info-content");
const infoCloseBtn = document.getElementById("info-close-btn");
const supplierInput = document.getElementById("supplier_name");
const emissionsInput = document.getElementById("emissions");
const violationsInput = document.getElementById("violations");
const notesInput = document.getElementById("notes");

let audits = [];
let selectedForCompare = [];
let visibleAudits = [];
let logSocket = null;

const downloadableFormats = ["pdf", "docx"];

function connectLogSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws/logs`;
  
  logSocket = new WebSocket(wsUrl);
  
  logSocket.onmessage = (event) => {
    const logMsg = JSON.parse(event.data);
    addLogMessage(logMsg);
  };
  
  logSocket.onerror = () => {
    console.warn('WebSocket connection error');
  };
  
  logSocket.onclose = () => {
    // Reconnect after 2 seconds
    setTimeout(connectLogSocket, 2000);
  };
}

function addLogMessage(logMsg) {
  const logLine = document.createElement('div');
  logLine.className = `log-line log-${logMsg.type}`;
  logLine.textContent = logMsg.message;
  logOutput.appendChild(logLine);
  logOutput.scrollTop = logOutput.scrollHeight;
}

function clearLogs() {
  logOutput.innerHTML = '';
}

function showLogPanel() {
  clearLogs();
  logPanel.style.display = 'block';
}

function hideLogPanel() {
  logPanel.style.display = 'none';
}

const setStatus = (msg, isError = false) => {
  statusEl.textContent = msg;
  statusEl.style.color = isError ? "#9f2f2f" : "#1f5a46";
};

const classToBadge = (classification) => {
  const cls = classification.toLowerCase().includes("critical")
    ? "critical"
    : classification.toLowerCase().includes("moderate")
      ? "moderate"
      : "low";
  return `<span class="badge ${cls}">${classification}</span>`;
};

const fmtDate = (iso) => {
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleString();
};

function refreshInputsFromAudit(item) {
  supplierInput.value = item.supplier_name ?? "";
  emissionsInput.value = item.emissions ?? "";
  violationsInput.value = item.violations ?? "";
  notesInput.value = item.notes ?? "";
}

async function fetchMetrics() {
  const res = await fetch("/api/metrics");
  const data = await res.json();

  const cards = [
    ["Total Audits", data.total_audits],
    ["Average Risk Score", data.avg_risk_score],
    ["Critical Rate", `${data.critical_rate}%`],
    ["Critical Count", data.classifications["Critical Risk"] ?? 0],
  ];

  metricsEl.innerHTML = cards
    .map(
      ([label, value]) =>
        `<article class="metric-card"><p class="metric-label">${label}</p><p class="metric-value">${value}</p></article>`
    )
    .join("");
}

async function fetchHistory() {
  const res = await fetch("/api/audits?limit=200");
  const data = await res.json();
  audits = data.items || [];
  renderHistory();
  renderCompare();

  if (audits.length > 0) {
    renderLatest(audits[0]);
  }
}

function renderLatest(item) {
  latestEl.innerHTML = `
    <div class="latest-block">
      <div class="badges">
        ${classToBadge(item.classification)}
        <span class="badge low">Score ${item.risk_score}</span>
        <span class="badge low">${item.report_source}</span>
      </div>
      <div><strong>${item.supplier_name}</strong> | Emissions ${item.emissions} | Violations ${item.violations}</div>
      <div><strong>Decision:</strong> ${item.policy_decision}</div>
      <div><strong>Reason:</strong> ${item.policy_reason}</div>
      <div><strong>Action:</strong> ${item.recommended_action}</div>
      <div class="report">${item.report_text || "No report generated."}</div>
    </div>
  `;
}

function renderHistory() {
  const filter = filterEl.value;
  const q = searchEl.value.trim().toLowerCase();

  const rows = audits.filter((a) => {
    const riskMatch = filter === "ALL" || a.classification === filter;
    const searchMatch = !q || a.supplier_name.toLowerCase().includes(q);
    return riskMatch && searchMatch;
  });

  visibleAudits = rows;

  historyBody.innerHTML = rows
    .map((item) => {
      const checked = selectedForCompare.includes(item.audit_id) ? "checked" : "";

      return `
        <tr data-audit-id="${item.audit_id}">
          <td><input type="checkbox" data-audit-id="${item.audit_id}" ${checked} /></td>
          <td>${item.supplier_name}</td>
          <td>${classToBadge(item.classification)}</td>
          <td>${item.risk_score}</td>
          <td>${item.policy_decision}</td>
          <td><button type="button" class="row-info-btn" data-audit-id="${item.audit_id}">Info</button></td>
          <td>${fmtDate(item.timestamp)}</td>
        </tr>
      `;
    })
    .join("");

  historyBody.querySelectorAll("input[type='checkbox']").forEach((cb) => {
    cb.addEventListener("change", (event) => {
      event.stopPropagation();
      const id = event.target.dataset.auditId;
      if (event.target.checked) {
        if (!selectedForCompare.includes(id)) {
          selectedForCompare.push(id);
        }
      } else {
        selectedForCompare = selectedForCompare.filter((x) => x !== id);
      }

      if (selectedForCompare.length > 2) {
        selectedForCompare = selectedForCompare.slice(selectedForCompare.length - 2);
      }

      renderHistory();
      renderCompare();
    });
  });

  historyBody.querySelectorAll(".row-info-btn").forEach((btn) => {
    btn.addEventListener("click", (event) => {
      event.stopPropagation();
      const id = event.currentTarget.dataset.auditId;
      const item = audits.find((x) => x.audit_id === id);
      if (item) {
        openInfoDialog(item);
      }
    });
  });

  historyBody.querySelectorAll("tr[data-audit-id]").forEach((row) => {
    row.addEventListener("click", () => {
      const id = row.dataset.auditId;
      const item = audits.find((x) => x.audit_id === id);
      if (item) {
        renderLatest(item);
        refreshInputsFromAudit(item);
        setStatus(`Showing details for ${item.supplier_name}.`);
      }
    });
  });
}

function refreshDownloadFormatOptions() {
  const selectedAuditId = downloadAuditSelect.value;
  const selectedAudit = audits.find((a) => a.audit_id === selectedAuditId);
  const links = selectedAudit?.download_links || {};

  const availableFormats = downloadableFormats.filter((fmt) => links[fmt]);
  downloadFormatSelect.innerHTML = availableFormats
    .map((fmt) => `<option value="${fmt}">${fmt.toUpperCase()}</option>`)
    .join("");
}

function openDownloadDialog(auditId = null) {
  const source = auditId
    ? audits.filter((a) => a.audit_id === auditId)
    : (visibleAudits.length ? visibleAudits : audits);
  if (!source.length) {
    setStatus("No audits available to download.", true);
    return;
  }

  downloadAuditSelect.innerHTML = source
    .map((a) => `<option value="${a.audit_id}">${a.supplier_name} | ${a.audit_id}</option>`)
    .join("");

  refreshDownloadFormatOptions();
  downloadAuditSelect.disabled = Boolean(auditId);
  downloadDialog.showModal();
}

function openSelectedDownload() {
  const selectedAuditId = downloadAuditSelect.value;
  const selectedFormat = downloadFormatSelect.value;
  const selectedAudit = audits.find((a) => a.audit_id === selectedAuditId);
  const href = selectedAudit?.download_links?.[selectedFormat];

  if (!href) {
    setStatus("Selected format is not available for this audit.", true);
    return;
  }

  const a = document.createElement("a");
  a.href = href;
  a.setAttribute("download", "");
  a.style.display = "none";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);

  downloadDialog.close();
  setStatus(`Download started: ${selectedFormat.toUpperCase()} for ${selectedAudit.supplier_name}.`);
}

function openInfoDialog(item) {
  const downloadAction = `<button type="button" id="info-download-btn">Download Files</button>`;

  infoContent.innerHTML = `
    <p><strong>Job ID:</strong> ${item.job_id || "-"}</p>
    <p><strong>Audit ID:</strong> ${item.audit_id}</p>
    <p><strong>Timestamp:</strong> ${fmtDate(item.timestamp)}</p>
    <p><strong>Supplier:</strong> ${item.supplier_name}</p>
    <p><strong>Emissions:</strong> ${item.emissions}</p>
    <p><strong>Violations:</strong> ${item.violations}</p>
    <p><strong>Risk:</strong> ${item.risk_score} (${item.classification})</p>
    <p><strong>Policy Decision:</strong> ${item.policy_decision}</p>
    <p><strong>Human Approval Required:</strong> ${item.human_approval_required}</p>
    <p><strong>Policy Reason:</strong> ${item.policy_reason}</p>
    <p><strong>Recommended Action:</strong> ${item.recommended_action}</p>
    <p><strong>Report Source:</strong> ${item.report_source}</p>
    ${downloadAction}
    <div class="info-report"><strong>Executive Report</strong>\n${item.report_text || "No report generated."}</div>
  `;

  const infoDownloadBtn = document.getElementById("info-download-btn");
  if (infoDownloadBtn) {
    infoDownloadBtn.addEventListener("click", () => {
      infoDialog.close();
      openDownloadDialog(item.audit_id);
    });
  }

  infoDialog.showModal();
}

function renderCompare() {
  const picks = audits.filter((a) => selectedForCompare.includes(a.audit_id));
  if (picks.length !== 2) {
    compareBox.textContent = "No pair selected.";
    return;
  }

  const [a, b] = picks;
  const delta = (b.risk_score - a.risk_score).toFixed(2);

  compareBox.innerHTML = `
    <div class="compare-grid">
      <article class="compare-card">
        <h3>${a.supplier_name}</h3>
        <p>${classToBadge(a.classification)} Score: ${a.risk_score}</p>
        <p>Decision: ${a.policy_decision}</p>
        <p>Action: ${a.recommended_action}</p>
      </article>
      <article class="compare-card">
        <h3>${b.supplier_name}</h3>
        <p>${classToBadge(b.classification)} Score: ${b.risk_score}</p>
        <p>Decision: ${b.policy_decision}</p>
        <p>Action: ${b.recommended_action}</p>
      </article>
    </div>
    <p><strong>Risk Delta:</strong> ${delta} (second - first)</p>
  `;
}

async function submitAudit(event) {
  event.preventDefault();

  const payload = {
    supplier_name: document.getElementById("supplier_name").value.trim(),
    emissions: Number(document.getElementById("emissions").value),
    violations: Number(document.getElementById("violations").value),
    notes: document.getElementById("notes").value.trim(),
  };

  setStatus("Running audit...");
  showLogPanel();

  try {
    const res = await fetch("/api/audit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Audit failed");
    }

    const result = await res.json();
    setStatus(`Audit complete for ${result.supplier_name}.`);
    renderLatest(result);
    await fetchMetrics();
    await fetchHistory();
    
    // Hide log panel after 3 seconds
    setTimeout(hideLogPanel, 3000);
  } catch (err) {
    setStatus(err.message, true);
    addLogMessage({type: 'error', message: `Error: ${err.message}`});
  }
}

async function clearHistory() {
  if (!window.confirm("Delete all saved audits?")) return;
  await fetch("/api/audits", { method: "DELETE" });
  selectedForCompare = [];
  await fetchMetrics();
  await fetchHistory();
  latestEl.textContent = "No audit executed yet.";
  setStatus("Audit history cleared.");
}

document.getElementById("audit-form").addEventListener("submit", submitAudit);
filterEl.addEventListener("change", renderHistory);
searchEl.addEventListener("input", renderHistory);
downloadAuditSelect.addEventListener("change", refreshDownloadFormatOptions);
downloadOpenBtn.addEventListener("click", openSelectedDownload);
downloadCancelBtn.addEventListener("click", () => downloadDialog.close());
infoCloseBtn.addEventListener("click", () => infoDialog.close());
document.getElementById("refresh-btn").addEventListener("click", async () => {
  await fetchMetrics();
  await fetchHistory();
  setStatus("Data refreshed.");
});
document.getElementById("clear-btn").addEventListener("click", clearHistory);

(async function init() {
  connectLogSocket();
  await fetchMetrics();
  await fetchHistory();
  setStatus("Dashboard ready.");
})();
