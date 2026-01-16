let map = null

async function loadMap() {
  const response = await fetch("/api/map");
  map = await response.json();
}

function neighborsOf(territory) {
  return (map && map[territory] && map[territory].neighbors) ? map[territory].neighbors : [];
}

const layer = document.getElementById("layer4"); // contains the 42 territories
const selectedEl = document.getElementById("selected"); // get selected territory display
const defaultColor = "#eaeaea";

let selectedId = null;  
let lasthighlighted = new Set();

// helper function to convert from id
function idToName(id) {
  return id
    .split("_")
    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

// helper function to convert name into id
function nameToId(name) {
  return name.toLowerCase().replaceAll(" ", "_");
}

// function to clear previous highlights
function clearHighlights() {
  lasthighlighted.forEach(id => {
    const el = document.getElementById(id);
    if (el && id !== selectedId) el.style.fill = defaultColor;
  });
  lasthighlighted.clear();
}

// function to highlight adjacent territories
function highlightAdjacent(neighbors) {
  neighbors.forEach(name => {
    const id = nameToId(name);
    const el = document.getElementById(id);
    if (el && id !== selectedId) {
      el.style.fill = "#f7e3a1";
      lasthighlighted.add(id);
    }
  });
}

async function init() {
  await loadMap(); // fetch map before clicks 
}

// animations and event listeners for each territory
layer.querySelectorAll("path").forEach(p => {
  p.style.cursor = "pointer";
  p.style.fill = defaultColor;
  p.style.transition = "fill 120ms, stroke-width 120ms";
  p.style.stroke = "#111";
  p.style.strokeWidth = "1";
  p.addEventListener("mouseenter", () => {
    p.style.strokeWidth = "2";
    if (p.id !== selectedId && !lasthighlighted.has(p.id)) p.style.fill = "#d6d6d6";
  });
  p.addEventListener("mouseleave", () => {
    p.style.strokeWidth = "1";
    if (p.id === selectedId) {
      p.style.fill = "#bcdcff"; 
    } else if (lasthighlighted.has(p.id)) {
      p.style.fill = "#f7e3a1";
    } else {
      p.style.fill = defaultColor;
    }
  });
  // highlight selected territory and adjacent territories
  p.addEventListener("click",() => {
    // unselect old territory
    clearHighlights();
    if (selectedId) {
      const old = document.getElementById(selectedId);
      if (old) old.style.fill = defaultColor;
    }
    selectedId = p.id;
    p.style.fill = "#bcdcff";
    const territoryName = idToName(p.id);
    if (selectedEl) selectedEl.textContent = "Selected: ${territoryName}";
    const neighbors = neighborsOf(territoryName);
    highlightAdjacent(neighbors);
  });
});

init();
