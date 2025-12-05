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

function appendLog(msg, jsonData = null) {
  const container = document.createElement('div');
  container.style.marginBottom = '8px';

  const timestamp = document.createElement('div');
  timestamp.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
  timestamp.style.color = 'var(--accent)';
  container.appendChild(timestamp);

  if (jsonData) {
    const pre = document.createElement('pre');
    pre.style.margin = '4px 0 0 0';
    pre.style.padding = '8px';
    pre.style.background = 'rgba(0,0,0,0.4)';
    pre.style.border = '1px solid rgba(255,204,51,0.2)';
    pre.style.borderRadius = '3px';
    pre.style.fontSize = '11px';
    pre.style.overflow = 'auto';
    pre.style.maxHeight = '300px';
    pre.style.color = '#9aa7c7';
    pre.style.lineHeight = '1.4';
    pre.textContent = JSON.stringify(jsonData, null, 2);
    container.appendChild(pre);
  }

  log.prepend(container);
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
    appendLog("POST response:", data);

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
        appendLog("No job_id found in response");
      }
      submitBtn.disabled = false;
      cancelBtn.disabled = true;
      return;
    }

    currentJobId = jobId;
    appendLog("Received job id: " + currentJobId);
    setStatus("Polling for status... (job " + currentJobId + ")");

    // Set loading state (placeholders)
    setLoadingState();
    startLoadingNeedle();

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
  setLoadingState();
});

// Helper functions for gauge and display management
function setLoadingState() {
  const gradeDisplay = document.getElementById('gradeDisplay');
  const scoreDisplay = document.getElementById('scoreDisplay');
  if (gradeDisplay) gradeDisplay.textContent = 'Grade: —';
  if (scoreDisplay) scoreDisplay.textContent = 'Score: —';
  stopLoadingNeedle();
}

function updateGauge(score_0_1000) {
  // Map score from 0-1000 to needle angle -80 to 80 degrees
  const minAngle = -80;
  const maxAngle = 80;
  const angle = minAngle + (score_0_1000 / 1000) * (maxAngle - minAngle);

  const needle = document.getElementById('needle');
  if (needle) {
    needle.style.transition = 'transform 1.5s ease-out';
    needle.style.transform = `translateX(-50%) rotate(${angle}deg)`;
  }
}

function updateResults(grade, score_1000) {
  const gradeDisplay = document.getElementById('gradeDisplay');
  const scoreDisplay = document.getElementById('scoreDisplay');
  if (gradeDisplay) gradeDisplay.textContent = `Grade: ${grade}`;
  if (scoreDisplay) scoreDisplay.textContent = `Score: ${score_1000}`;
}

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
    appendLog("Status response:", data);
    if (!status) {
      // cannot find status field — treat as pending for now
      setStatus("Waiting (no status field found)");
      return;
    }
    if (status.toLowerCase() === "pending" || status.toLowerCase() === "in_progress" || status.toLowerCase() === "inprogress") {
      setStatus("Pending... (job " + currentJobId + ")");
      // Keep showing loading state with placeholders
      return;
    }
    if (status.toLowerCase() === "completed" || status.toLowerCase() === "complete" || status.toLowerCase() === "success" ) {
      setStatus("Completed 🎉");

      // Extract grade and score from result
      const result = data.result || {};
      const grade = result.grade || '—';
      const score_0_1000 = result.score_0_1000 || 0;

      // Log the complete result
      appendLog("Job completed - Result:", result);

      // Update gauge and displays
      stopLoadingNeedle();
      updateGauge(score_0_1000);
      updateResults(grade, score_0_1000);

      stopPollingBecause("completed");
      return;
    }
    if (status.toLowerCase() === "failed" || status.toLowerCase() === "error") {
      setStatus("Failed ❌");
      const errorInfo = data.error || data.message || "No error details provided";
      appendLog("Job failed:", { error: errorInfo, full_response: data });
      setLoadingState();
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


let loadingTimer = null;
let loadingAngle = -80;
let loadingDir = 1;

function startLoadingNeedle() {
    const needle = document.getElementById("needle");
    if (!needle) {
        console.error("NEEDLE NOT FOUND");
        return;
    }

    // اگر از قبل در حال اجرا بود، دوباره ست نکن
    if (loadingTimer !== null) return;

    loadingTimer = setInterval(() => {
        loadingAngle += loadingDir * 4;

        if (loadingAngle > 80 || loadingAngle < -80) {
            loadingDir *= -1;
        }

        needle.style.transform =
            `translateX(-50%) rotate(${loadingAngle}deg)`;

    }, 120);
}

function stopLoadingNeedle() {
    if (loadingTimer !== null) {
        clearInterval(loadingTimer);
        loadingTimer = null;
    }

    // ریست عقربه به موقعیت اولیه
    const needle = document.getElementById("needle");
    if (needle) {
        needle.style.transform = `translateX(-50%) rotate(-80deg)`;
    }

    loadingAngle = -80;
    loadingDir = 1;
}

