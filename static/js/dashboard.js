/**
 * Dashboard JS – AI Resume Analyzer
 * Initialises charts, stat counter animations, search, and delete.
 */

document.addEventListener("DOMContentLoaded", () => {

  // ── Animated Stat Counters ─────────────────────────────────────────────────
  document.querySelectorAll(".stat-value[data-target]").forEach(el => {
    const target = parseInt(el.dataset.target, 10);
    if (isNaN(target)) return;
    let current = 0;
    const step = Math.max(1, Math.floor(target / 40));
    const interval = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = current;
      if (current >= target) clearInterval(interval);
    }, 30);
  });

  // ── Pie Chart – Score Distribution ────────────────────────────────────────
  const pieCtx = document.getElementById("pieChart");
  if (pieCtx && window.SCORE_DIST) {
    const { high, mid, low } = window.SCORE_DIST;
    new Chart(pieCtx, {
      type: "doughnut",
      data: {
        labels: ["High (≥80)", "Medium (50–79)", "Low (<50)"],
        datasets: [{
          data: [high, mid, low],
          backgroundColor: ["#22C55E", "#F59E0B", "#EF4444"],
          borderColor: "transparent",
          borderWidth: 0,
          hoverOffset: 6,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "65%",
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              color: "#94A3B8",
              font: { family: "Inter", size: 11 },
              padding: 14,
              usePointStyle: true,
              pointStyleWidth: 8,
            },
          },
          tooltip: {
            backgroundColor: "#1E293B",
            borderColor: "rgba(255,255,255,0.1)",
            borderWidth: 1,
            titleColor: "#E2E8F0",
            bodyColor: "#94A3B8",
            padding: 12,
          },
        },
      },
    });
  }

  // ── Bar Chart – Recent Scores ──────────────────────────────────────────────
  const barCtx = document.getElementById("barChart");
  if (barCtx && window.RECENT_SCORES && window.RECENT_SCORES.length) {
    const labels = window.RECENT_SCORES.map(r => r.filename);
    const scores = window.RECENT_SCORES.map(r => r.score);

    new Chart(barCtx, {
      type: "bar",
      data: {
        labels,
        datasets: [{
          label: "Score",
          data: scores,
          backgroundColor: scores.map(s =>
            s >= 80 ? "rgba(34,197,94,0.65)"
            : s >= 50 ? "rgba(245,158,11,0.65)"
            : "rgba(239,68,68,0.65)"
          ),
          borderRadius: 8,
          borderSkipped: false,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "#1E293B",
            borderColor: "rgba(255,255,255,0.1)",
            borderWidth: 1,
            titleColor: "#E2E8F0",
            bodyColor: "#94A3B8",
            padding: 10,
          },
        },
        scales: {
          x: {
            ticks: { color: "#94A3B8", font: { size: 10 }, maxRotation: 30 },
            grid: { display: false },
          },
          y: {
            min: 0,
            max: 100,
            ticks: { color: "#94A3B8", font: { size: 10 }, stepSize: 20 },
            grid: { color: "rgba(255,255,255,0.04)" },
          },
        },
      },
    });
  }

  // ── Table Search ──────────────────────────────────────────────────────────
  const searchInput = document.getElementById("tableSearch");
  const table       = document.getElementById("analysisTable");

  if (searchInput && table) {
    searchInput.addEventListener("input", () => {
      const query = searchInput.value.toLowerCase().trim();
      table.querySelectorAll("tbody tr").forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(query) ? "" : "none";
      });
    });
  }

  // ── Delete Rows ────────────────────────────────────────────────────────────
  document.querySelectorAll(".delete-btn").forEach(btn => {
    btn.addEventListener("click", async () => {
      const id  = btn.dataset.id;
      const row = btn.closest("tr");
      if (!confirm("Delete this analysis permanently?")) return;

      try {
        const res = await fetch(`/api/delete/${id}`, { method: "DELETE" });
        if (res.ok) {
          row.style.transition = "opacity 0.3s, transform 0.3s";
          row.style.opacity    = "0";
          row.style.transform  = "translateX(30px)";
          setTimeout(() => row.remove(), 300);
        } else {
          alert("Delete failed. Please try again.");
        }
      } catch {
        alert("Network error. Please try again.");
      }
    });
  });

});
