/**
 * Particle Animation – AI Resume Analyzer
 * Creates a subtle animated particle canvas background.
 */

(function () {
  const canvas  = document.getElementById("particles-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  let W, H, particles = [];

  const CONFIG = {
    count:     60,
    speed:     0.4,
    maxRadius: 2.5,
    minRadius: 0.5,
    colors:    ["#00F5D4", "#F72585", "#3B82F6", "#8B5CF6"],
    connDist:  120,
    connAlpha: 0.08,
  };

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  function random(min, max) { return Math.random() * (max - min) + min; }

  function createParticle() {
    const color = CONFIG.colors[Math.floor(Math.random() * CONFIG.colors.length)];
    return {
      x:    random(0, W),
      y:    random(0, H),
      r:    random(CONFIG.minRadius, CONFIG.maxRadius),
      vx:   random(-CONFIG.speed, CONFIG.speed),
      vy:   random(-CONFIG.speed, CONFIG.speed),
      color,
      alpha: random(0.3, 0.7),
    };
  }

  function init() {
    particles = Array.from({ length: CONFIG.count }, createParticle);
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);

    // Draw connections
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < CONFIG.connDist) {
          const alpha = (1 - dist / CONFIG.connDist) * CONFIG.connAlpha;
          ctx.beginPath();
          ctx.strokeStyle = `rgba(0,245,212,${alpha})`;
          ctx.lineWidth = 0.8;
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.stroke();
        }
      }
    }

    // Draw particles
    particles.forEach(p => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.globalAlpha = p.alpha;
      ctx.fill();
      ctx.globalAlpha = 1;

      // Update position
      p.x += p.vx;
      p.y += p.vy;

      // Wrap around edges
      if (p.x < -10) p.x = W + 10;
      if (p.x > W + 10) p.x = -10;
      if (p.y < -10) p.y = H + 10;
      if (p.y > H + 10) p.y = -10;
    });

    requestAnimationFrame(draw);
  }

  resize();
  init();
  draw();
  window.addEventListener("resize", () => { resize(); init(); });
})();
