let map = null

async function loadMap() {
  const response = await fetch("/api/map");
  map = await response.json();
}

async function fetchState() {
  const response = await fetch("/api/state");
  return await response.json();
}

async function isUnoccupied(territory) {
  const response = await fetch("/api/avaliableSet", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({})
  });
  const data = await response.json();
  return data.out.includes(territory);
}

async function placeArmy(territory, player, army=1) {
  const response = await fetch("/api/placeArmy", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({territory: territory, player, army})
  });
  await updateState();
}

function applyState(state) {
  for (const [territory, info] of Object.entries(state.territories)) {
    const id = nameToId(territory);
    const el = document.getElementById(id);
    if (el) {
      el.style.fill = PLAYER_COLORS[info.owner] || "#eaeaea";
    }
  }
}

function neighborsOf(territory) {
  return (map && map[territory] && map[territory].neighbors) ? map[territory].neighbors : [];
}

const layer = document.getElementById("layer4"); // contains the 42 territories
const selectedEl = document.getElementById("selected"); // get selected territory display

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

let selectedId = null;  

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
let lasthighlighted = new Set();

let latestState = null;
async function updateState() {
  latestState = await fetchState();
  applyState(latestState);
}

function clearHighlights() {
  lasthighlighted.clear();
  if (latestState) applyState(latestState);
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
  await loadMap();
  const state = await fetchState();
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
    if (p.id === selectedId) {
      p.style.fill = "#bcdcff"; 
    } else if (lasthighlighted.has(p.id)) {
      p.style.fill = "#f7e3a1";
    } else {
      p.style.fill = defaultColor;
    }
  });
  // highlight selected territory and adjacent territories
  p.addEventListener("click",async () => {
    // unselect old territory
    clearHighlights();
    selectedId = p.id

    const territoryName = idToName(p.id);

    highlightAdjacent(neighborsOf(territoryName));

    if (await isUnoccupied(territoryName)) {
      await placeArmy(territoryName, 1, 1); // assuming player 1 for now
    }
  });
});

init();
