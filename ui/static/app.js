/*
  Configuration: Backend endpoints integrated with Flask app.
*/
const BACKEND_BASE_URL = ""; // Same server
const POST_ENDPOINT = "/job";
const STATUS_ENDPOINT_TEMPLATE = "/job/{id}";

const POLL_INTERVAL_MS = 20000; // 20 seconds

// Validation regexes (match backend)
const nameRe = /^[A-Za-z\s]+$/;
const cellNumberRe = /^[0-9]{10,15}$/; // 10-15 digits only
const linkedinRe = /^https?:\/\/(www\.)?linkedin\.com\/in\/[\w\-]+\/?$/i;

const frm = document.getElementById('frm');
const submitBtn = document.getElementById('submitBtn');
const cancelBtn = document.getElementById('cancelBtn');
const statusText = document.getElementById('statusText');
const log = document.getElementById('log');

let pollTimer = null;
let currentJobId = null;

function appendLog(msg) {
  const p = document.createElement('div');
  p.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
  log.prepend(p);
}

function setStatus(s) {
  statusText.textContent = s;
}

frm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const name = document.getElementById('name').value.trim();
  const cell_number = document.getElementById('cell_number').value.trim();
  const linkedin_account = document.getElementById('linkedin_account').value.trim();

  // Client-side validation
  if (!nameRe.test(name)) {
    alert("Invalid name. Only letters and spaces allowed.");
    return;
  }
  if (!cellNumberRe.test(cell_number)) {
    alert("Invalid cell number. Must be 10-15 digits only (e.g. 9127638825).");
    return;
  }
  if (!linkedinRe.test(linkedin_account)) {
    alert("Invalid LinkedIn URL. Must be https://linkedin.com/in/your-profile");
    return;
  }

  // Disable submit while pending
  submitBtn.disabled = true;
  cancelBtn.disabled = false;
  setStatus("Posting to backend...");
  appendLog("Sending POST to backend...");

  try {
    const resp = await fetch(BACKEND_BASE_URL + POST_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, cell_number, linkedin_account })
    });

    if (!resp.ok) {
      // treat as failed
      setStatus("POST failed (HTTP " + resp.status + ")");
      appendLog("POST returned HTTP " + resp.status);
      submitBtn.disabled = false;
      cancelBtn.disabled = true;
      return;
    }

    const data = await resp.json();
    // attempt to extract job id (many APIs return id or job_id)
    const jobId = data.job_id || data.id || data.request_id || data.jobId;
    if (!jobId) {
      // If no job id returned, you might instead get final status in response.
      // We'll check if response contains status:
      if (data.status && (data.status === "completed" || data.status === "failed")) {
        setStatus("Completed (received final status in POST response)");
        appendLog("Final state: " + data.status);
      } else {
        setStatus("POST succeeded but no job id returned");
        appendLog("Response JSON: " + JSON.stringify(data));
      }
      submitBtn.disabled = false;
      cancelBtn.disabled = true;
      return;
    }

    currentJobId = jobId;
    appendLog("Received job id: " + currentJobId);
    setStatus("Polling for status... (job " + currentJobId + ")");

    // start polling
    pollStatus();
    pollTimer = setInterval(pollStatus, POLL_INTERVAL_MS);

  } catch (err) {
    console.error(err);
    setStatus("Network or JS error during POST");
    appendLog("Error: " + err.message);
    submitBtn.disabled = false;
    cancelBtn.disabled = true;
  }
});

cancelBtn.addEventListener('click', () => {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
  currentJobId = null;
  setStatus("Polling cancelled by user");
  appendLog("Polling cancelled");
  submitBtn.disabled = false;
  cancelBtn.disabled = true;
});

async function pollStatus() {
  if (!currentJobId) return;
  setStatus("Checking backend for job " + currentJobId + " ...");
  appendLog("GET status for job " + currentJobId);

  try {
    const url = BACKEND_BASE_URL + STATUS_ENDPOINT_TEMPLATE.replace("{id}", encodeURIComponent(currentJobId));
    const resp = await fetch(url, { method: "GET" });
    if (!resp.ok) {
      // treat non-2xx as failure
      setStatus("Failed (HTTP " + resp.status + ")");
      appendLog("GET returned HTTP " + resp.status);
      stopPollingBecause("failed (HTTP " + resp.status + ")");
      return;
    }
    const data = await resp.json();
    const status = data.status || data.state || null;
    appendLog("Status response: " + JSON.stringify(data));
    if (!status) {
      // cannot find status field — treat as pending for now
      setStatus("Waiting (no status field found)");
      return;
    }
    if (status.toLowerCase() === "pending" || status.toLowerCase() === "in_progress" || status.toLowerCase() === "inprogress") {
      setStatus("Pending... (job " + currentJobId + ")");
      return;
    }
    if (status.toLowerCase() === "completed" || status.toLowerCase() === "complete" || status.toLowerCase() === "success" ) {
      setStatus("Completed 🎉");
      appendLog("Job completed");
      stopPollingBecause("completed");
      return;
    }
    if (status.toLowerCase() === "failed" || status.toLowerCase() === "error") {
      setStatus("Failed ❌");
      appendLog("Job failed");
      stopPollingBecause("failed");
      return;
    }
    // any other status string — log and keep polling
    setStatus("Status: " + status);
  } catch (err) {
    console.error(err);
    setStatus("Network / fetch error during poll");
    appendLog("Error: " + err.message);
    // treat fetch errors as failure (you can change behavior)
    stopPollingBecause("failed (network error)");
  }
}

function stopPollingBecause(reason) {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
  currentJobId = null;
  submitBtn.disabled = false;
  cancelBtn.disabled = true;
  appendLog("Stopped polling: " + reason);
}
