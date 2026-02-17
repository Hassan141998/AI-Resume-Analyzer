/**
 * Upload JS – AI Resume Analyzer
 * Handles: drag-and-drop upload, file validation, char counter, loading animation.
 */

document.addEventListener("DOMContentLoaded", () => {

  const dropZone    = document.getElementById("dropZone");
  const browseBtn   = document.getElementById("browseBtn");
  const resumeInput = document.getElementById("resumeInput");
  const filePreview = document.getElementById("filePreview");
  const fileName    = document.getElementById("fileName");
  const fileSize    = document.getElementById("fileSize");
  const removeFile  = document.getElementById("removeFile");
  const uploadProg  = document.getElementById("uploadProgress");
  const jdTextarea  = document.getElementById("job_description");
  const charCount   = document.getElementById("charCount");
  const form        = document.getElementById("analysisForm");
  const analyzeBtn  = document.getElementById("analyzeBtn");
  const btnText     = analyzeBtn?.querySelector(".btn-text");
  const btnLoading  = analyzeBtn?.querySelector(".btn-loading");
  const overlay     = document.getElementById("loadingOverlay");

  // ── Drag & Drop ────────────────────────────────────────────────────────────
  if (dropZone) {
    ["dragenter", "dragover"].forEach(evt =>
      dropZone.addEventListener(evt, e => {
        e.preventDefault();
        dropZone.classList.add("drag-over");
      })
    );
    ["dragleave", "drop"].forEach(evt =>
      dropZone.addEventListener(evt, () => dropZone.classList.remove("drag-over"))
    );
    dropZone.addEventListener("drop", e => {
      e.preventDefault();
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    });
    dropZone.addEventListener("click", () => resumeInput.click());
  }

  if (browseBtn) browseBtn.addEventListener("click", e => { e.stopPropagation(); resumeInput.click(); });
  if (resumeInput) resumeInput.addEventListener("change", () => {
    if (resumeInput.files[0]) handleFile(resumeInput.files[0]);
  });

  // ── File Handler ───────────────────────────────────────────────────────────
  const ALLOWED_TYPES = ["application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword"];
  const MAX_SIZE = 10 * 1024 * 1024; // 10 MB

  function handleFile(file) {
    if (!ALLOWED_TYPES.includes(file.type) && !file.name.match(/\.(pdf|docx|doc)$/i)) {
      showToast("Only PDF and DOCX files are supported.", "error");
      return;
    }
    if (file.size > MAX_SIZE) {
      showToast("File exceeds 10 MB limit.", "error");
      return;
    }

    // Update UI
    dropZone.classList.add("hidden");
    filePreview.classList.remove("hidden");
    fileName.textContent = file.name;
    fileSize.textContent = formatBytes(file.size);

    // Fake progress bar
    let w = 0;
    const interval = setInterval(() => {
      w = Math.min(w + Math.random() * 15, 95);
      uploadProg.style.width = w + "%";
    }, 80);
    setTimeout(() => {
      clearInterval(interval);
      uploadProg.style.width = "100%";
    }, 700);
  }

  // ── Remove File ────────────────────────────────────────────────────────────
  if (removeFile) {
    removeFile.addEventListener("click", () => {
      resumeInput.value = "";
      filePreview.classList.add("hidden");
      dropZone.classList.remove("hidden");
      uploadProg.style.width = "0";
    });
  }

  // ── Char Counter ───────────────────────────────────────────────────────────
  if (jdTextarea && charCount) {
    const update = () => {
      const n = jdTextarea.value.length;
      charCount.textContent = n.toLocaleString() + " character" + (n !== 1 ? "s" : "");
      charCount.style.color = n > 100 ? "var(--green)" : "var(--text-muted)";
    };
    jdTextarea.addEventListener("input", update);
  }

  // ── Form Submit + Loading Animation ───────────────────────────────────────
  if (form) {
    form.addEventListener("submit", e => {
      if (!resumeInput.files.length) {
        e.preventDefault();
        showToast("Please upload a resume first.", "error");
        return;
      }
      if (!jdTextarea.value.trim()) {
        e.preventDefault();
        showToast("Please paste a job description.", "error");
        return;
      }

      // Show loading overlay
      if (overlay) overlay.classList.remove("hidden");
      if (btnText)    btnText.classList.add("hidden");
      if (btnLoading) btnLoading.classList.remove("hidden");
      analyzeBtn.disabled = true;

      // Animate steps
      const steps = ["step1","step2","step3","step4"];
      steps.forEach((id, i) => {
        setTimeout(() => {
          const el = document.getElementById(id);
          if (el) { el.classList.add("active"); }
          // Mark previous step done
          if (i > 0) {
            const prev = document.getElementById(steps[i - 1]);
            if (prev) { prev.classList.remove("active"); prev.classList.add("done"); }
          }
        }, i * 900);
      });
    });
  }

  // ── Helpers ────────────────────────────────────────────────────────────────
  function formatBytes(bytes) {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / 1048576).toFixed(1) + " MB";
  }

  function showToast(message, type = "info") {
    const container = document.querySelector(".toast-container") || (() => {
      const c = document.createElement("div");
      c.className = "toast-container";
      document.body.appendChild(c);
      return c;
    })();

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    const icon = type === "error" ? "fa-exclamation-circle" : "fa-check-circle";
    toast.innerHTML = `<i class="fas ${icon}"></i><span>${message}</span>
      <button class="toast-close" onclick="this.parentElement.remove()">✕</button>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity   = "0";
      toast.style.transform = "translateX(100%)";
      toast.style.transition = "all 0.4s ease";
      setTimeout(() => toast.remove(), 400);
    }, 4000);
  }
});
