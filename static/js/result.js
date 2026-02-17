/**
 * Result JS – AI Resume Analyzer
 * Score counter animation, confetti effect.
 */

document.addEventListener("DOMContentLoaded", () => {
  const score = window.RESUME_SCORE || 0;

  // ── Animate Score Number ───────────────────────────────────────────────────
  const scoreEl = document.getElementById("scoreNumber");
  if (scoreEl) {
    let current = 0;
    const duration = 1800;
    const step = score / (duration / 16);
    const interval = setInterval(() => {
      current = Math.min(current + step, score);
      scoreEl.textContent = Math.round(current);
      if (current >= score) clearInterval(interval);
    }, 16);
  }

  // ── Color the score fill based on value ───────────────────────────────────
  const fill = document.getElementById("scoreFill");
  if (fill) {
    const color = score >= 80 ? "#22C55E" : score >= 50 ? "#F59E0B" : "#EF4444";
    fill.setAttribute("stroke", color);
    // Also update circle text color
    if (scoreEl) scoreEl.style.color = color;
  }

  // ── Confetti (simple CSS confetti) ────────────────────────────────────────
  if (score >= 70) {
    spawnConfetti();
  }

  function spawnConfetti() {
    const container = document.getElementById("confetti");
    if (!container) return;
    const colors = ["#00F5D4", "#F72585", "#22C55E", "#F59E0B", "#3B82F6", "#8B5CF6"];
    for (let i = 0; i < 60; i++) {
      const el = document.createElement("div");
      el.style.cssText = `
        position: fixed;
        top: -10px;
        left: ${Math.random() * 100}vw;
        width: ${Math.random() * 8 + 4}px;
        height: ${Math.random() * 8 + 4}px;
        border-radius: ${Math.random() > 0.5 ? "50%" : "2px"};
        background: ${colors[Math.floor(Math.random() * colors.length)]};
        opacity: ${Math.random() * 0.8 + 0.2};
        transform: rotate(${Math.random() * 360}deg);
        animation: confettiFall ${Math.random() * 2 + 2}s ease-in forwards;
        animation-delay: ${Math.random() * 1.5}s;
        pointer-events: none;
        z-index: 9999;
      `;
      container.appendChild(el);
      setTimeout(() => el.remove(), 4000);
    }

    // Inject keyframes if not present
    if (!document.getElementById("confetti-keyframes")) {
      const style = document.createElement("style");
      style.id = "confetti-keyframes";
      style.textContent = `
        @keyframes confettiFall {
          to {
            transform: translateY(110vh) rotate(${Math.random() * 720}deg);
            opacity: 0;
          }
        }
      `;
      document.head.appendChild(style);
    }
  }

  // ── Animate mini bars ──────────────────────────────────────────────────────
  document.querySelectorAll(".mini-fill").forEach(bar => {
    const width = bar.style.width;
    bar.style.width = "0";
    setTimeout(() => {
      bar.style.transition = "width 1.2s cubic-bezier(0.4,0,0.2,1) 0.3s";
      bar.style.width = width;
    }, 200);
  });
});
