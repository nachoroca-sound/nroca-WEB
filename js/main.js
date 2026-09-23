/* Scroll reveal, hover video play, project cell navigation.
   Grid markup is rendered at build time by build.py — no JS rendering here. */

function initProjectCells() {
  const videoObserver = new IntersectionObserver((entries) => {
    entries.forEach(({ target: video, isIntersecting }) => {
      if (isIntersecting) {
        video.preload = "auto";
        video.play().catch(() => {});
      } else {
        video.pause();
        video.preload = "none";
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll(".project-cell").forEach((cell) => {
    const video = cell.querySelector("video");
    if (video) {
      videoObserver.observe(video);
      cell.addEventListener("mouseenter", () => video.play().catch(() => {}));
    }

    cell.addEventListener("click", (e) => {
      if (e.target.closest("a")) return;
      const link = cell.querySelector("a.project-title");
      if (link) window.location.href = link.href;
    });
    cell.addEventListener("keydown", (e) => {
      if ((e.key === "Enter" || e.key === " ") && !e.target.closest("a")) {
        e.preventDefault();
        const link = cell.querySelector("a.project-title");
        if (link) window.location.href = link.href;
      }
    });
  });
}

/* ---------- Scroll reveal ---------- */
function initScrollReveal() {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduceMotion) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08, rootMargin: "0px 0px -40px 0px" });

  document.querySelectorAll(".reveal").forEach((el) => observer.observe(el));

  /* Stagger individual project cells */
  document.querySelectorAll(".projects-grid .project-cell").forEach((cell, i) => {
    cell.classList.add("reveal");
    cell.style.setProperty("--reveal-i", i % 3);
    observer.observe(cell);
  });
}

/* ---------- Mobile nav: hamburger + full-screen panel ---------- */
function initMobileNav() {
  const toggle = document.querySelector(".nav-toggle");
  const panel = document.getElementById("mobile-nav");
  if (!toggle || !panel) return;

  const closeBtn = panel.querySelector(".mobile-nav-close");
  const links = panel.querySelectorAll(".mobile-nav-link");
  const focusable = [closeBtn, ...links];

  function open() {
    panel.classList.add("is-open");
    panel.setAttribute("aria-hidden", "false");
    toggle.setAttribute("aria-expanded", "true");
    document.body.classList.add("nav-open");
    closeBtn.focus();
    document.addEventListener("keydown", onKeydown);
  }

  function close() {
    panel.classList.remove("is-open");
    panel.setAttribute("aria-hidden", "true");
    toggle.setAttribute("aria-expanded", "false");
    document.body.classList.remove("nav-open");
    document.removeEventListener("keydown", onKeydown);
    toggle.focus();
  }

  function onKeydown(e) {
    if (e.key === "Escape") {
      e.preventDefault();
      close();
      return;
    }
    if (e.key !== "Tab") return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }

  toggle.addEventListener("click", () => {
    if (panel.classList.contains("is-open")) close();
    else open();
  });
  closeBtn.addEventListener("click", close);
  links.forEach((link) => link.addEventListener("click", close));
}

/* ---------- Footer year ---------- */
const footerYear = document.getElementById("footer-year");
if (footerYear) footerYear.textContent = new Date().getFullYear();

/* ---------- Init ---------- */
initProjectCells();
initScrollReveal();
initMobileNav();
