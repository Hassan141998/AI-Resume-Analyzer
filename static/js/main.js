/**
 * Main JS – AI Resume Analyzer
 * Global utilities: mobile nav, toast auto-dismiss, smooth scroll.
 */

document.addEventListener("DOMContentLoaded", () => {

  // ── Mobile Nav Toggle ──────────────────────────────────────────────────────
  const toggle   = document.getElementById("navToggle");
  const navLinks = document.querySelector(".nav-links");
  if (toggle && navLinks) {
    toggle.addEventListener("click", () => {
      navLinks.classList.toggle("nav-open");
      toggle.classList.toggle("open");
    });
  }

  // ── Auto-dismiss Toasts ────────────────────────────────────────────────────
  document.querySelectorAll(".toast").forEach(toast => {
    setTimeout(() => {
      toast.style.opacity    = "0";
      toast.style.transform  = "translateX(100%)";
      toast.style.transition = "all 0.4s ease";
      setTimeout(() => toast.remove(), 400);
    }, 5000);
  });

  // ── Smooth scroll for anchors ──────────────────────────────────────────────
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener("click", e => {
      const target = document.querySelector(a.getAttribute("href"));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });

});
