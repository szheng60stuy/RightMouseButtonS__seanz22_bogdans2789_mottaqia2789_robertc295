// -- Constants / Color Helpers --
const defaultColor = "#eaeaea";
const PLAYER_COLORS = {
  0: "#eaeaea",
  1: "#bcdcff",
  2: "#ffd6d6",
  3: "#d6ffd9",
  4: "#fff3b0",
  5: "#e3d6ff",
  6: "#ffdca8",
};

function baseColorFor(id) {
  if (!latestState) return defaultColor;
  const territoryName = idToName(id);
  const info = latestState.territories?.[territoryName];
  if (!info) return defaultColor;

  return PLAYER_COLORS[info.owner] || defaultColor;
}

// -- Global State / DOM Refs --
let map = null;
let latestState = null;

const layer = document.getElementById("layer4"); // contains the 42 territories
const selectedEl = document.getElementById("selected"); // get selected territory display

let selectedId = null;
let lasthighlighted = new Set();

let phase = "setup";
let currentPlayer = 1;

// -- ID/Name Conversion Helpers --

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

// -- Data Fetching / API Calls --

async function loadMap() {
  const response = await fetch("/api/map");
  map = await response.json();
}

async function fetchState() {
  const response = await fetch("/api/state");
  return await response.json();
}

async function isUnoccupied(territory) {
  const response = await fetch("/api/availableSet", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({})
  });
  const data = await response.json();
  return data.out.includes(territory);
}

async function placeArmy(territory, player, army=1) {
  const response = await fetch("/api/addTerritory", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({home: null, territory, player, army})
  });
  await updateState();
}

async function updateState() {
  latestState = await fetchState();
  repaint();
}

// -- Rendering / UI Updates --

function applyState(state) {
  for (const [territory, info] of Object.entries(state.territories)) {
    const id = nameToId(territory);
    const el = document.getElementById(id);
    if (el) {
      el.style.fill = PLAYER_COLORS[info.owner] || "#eaeaea";
    }
  }
}

function repaint() {
  if (latestState) applyState(latestState);

  lasthighlighted.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.style.fill = "#f7e3a1";
  });

  if (selectedId) {
    const el = document.getElementById(selectedId);
    if (el) el.style.fill = "#bcdcff";
  }
}

// -- Map / Neighbor Utilities --
function neighborsOf(territory) {
  return (map && map[territory] && map[territory].neighbors) ? map[territory].neighbors : [];
}

// -- Highlight Helpers --
function clearHighlights() {
  lasthighlighted.clear();
  repaint();
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

// -- Init / Event Listeners --
async function init() {
  await loadMap();
  updateState();
}

// animations and event listeners for each territory
layer.querySelectorAll("path").forEach(p => {
  p.style.cursor = "pointer";
  p.style.transition = "fill 120ms, stroke-width 120ms";
  p.style.stroke = "#111";
  p.style.strokeWidth = "1";

  p.addEventListener("mouseenter", () => {
    p.style.strokeWidth = "2";
    if (p.id !== selectedId && !lasthighlighted.has(p.id)) p.style.fill = "#d6d6d6";
  });

  p.addEventListener("mouseleave", () => {
    p.style.strokeWidth = "1";
    repaint();
  });

  // highlight selected territory and adjacent territories
  p.addEventListener("click",async () => {
    // unselect old territory
    selectedId = p.id
    
    lasthighlighted.clear();
    const territoryName = idToName(p.id);
    neighborsOf(territoryName).forEach(name => lasthighlighted.add(nameToId(name)));

    if (await isUnoccupied(territoryName)) {
      await placeArmy(territoryName, 1, 1); // assuming player 1 for now
    } else {
      repaint();
    }

    if (selectedId) selectedEl.textContent = `Selected Territory: ${territoryName}`;
  });
});

init();
