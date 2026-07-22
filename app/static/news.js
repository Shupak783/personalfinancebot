const carouselEl = document.getElementById("news-carousel");
const summaryEl = document.getElementById("news-trend-summary");

let headlines = [];
let activeIndex = 0;
let rotateTimer = null;
const ROTATE_MS = 8000;

function renderHeadline() {
  if (!headlines.length) {
    carouselEl.textContent = "No headlines available right now.";
    return;
  }
  const h = headlines[activeIndex];
  carouselEl.innerHTML = "";

  const link = document.createElement("a");
  link.className = "news-headline";
  link.href = h.link;
  link.target = "_blank";
  link.rel = "noopener noreferrer"; // never let the linked page control this tab
  link.textContent = h.title; // textContent, never innerHTML, for anything sourced from a feed
  const source = document.createElement("span");
  source.className = "news-source";
  source.textContent = h.source;
  link.appendChild(source);
  carouselEl.appendChild(link);

  const dots = document.createElement("div");
  dots.className = "news-dots";
  headlines.forEach((_, i) => {
    const dot = document.createElement("span");
    dot.className = "news-dot" + (i === activeIndex ? " active" : "");
    dots.appendChild(dot);
  });
  carouselEl.appendChild(dots);
}

function advance() {
  activeIndex = (activeIndex + 1) % headlines.length;
  renderHeadline();
}

function startRotation() {
  if (rotateTimer) clearInterval(rotateTimer);
  if (headlines.length > 1) {
    rotateTimer = setInterval(advance, ROTATE_MS);
  }
}

carouselEl.addEventListener("mouseenter", () => rotateTimer && clearInterval(rotateTimer));
carouselEl.addEventListener("mouseleave", startRotation);

async function loadNews() {
  try {
    const res = await fetch("/news");
    const data = await res.json();
    headlines = data.headlines || [];
    activeIndex = 0;
    renderHeadline();
    startRotation();
    summaryEl.textContent = data.trend_summary || "No overview available right now.";
  } catch (err) {
    carouselEl.textContent = "Couldn't load news right now.";
    summaryEl.textContent = "";
  }
}

loadNews();
