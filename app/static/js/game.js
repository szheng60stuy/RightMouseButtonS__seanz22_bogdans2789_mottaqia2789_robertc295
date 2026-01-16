// -- Constants / Color Helpers --
const defaultColor = "#eaeaea";
const PLAYER_COLORS = {
  0: "#eaeaea",
  1: "#bcdcff",
  2: "#ffd6d6",
  3: "#d6ffd9",
  4: "#fff3b0",
  5: "#e3d6ff",
  6: "#7f70ff",
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
let playerCount = 2;

let moveOrigin = null;
let moveTarget = new Set();

function isMyTurn() {
  if (!latestState) return true;
  if (latestState.turn === 0) return true;
  return latestState.turn === currentPlayer;
}

function canClickTerritory(territory) {
  return isMyTurn();
}

function setPhase(next) {
  const ok =
    (phase === "setup" && next === "deploy") ||
    (phase === "deploy" && next === "attack") ||
    (phase === "attack" && next === "reinforce") ||
    (phase === "reinforce" && next === "deploy");
  
  if (!ok) return;

  phase = next;
  selectedId = null;
  lasthighlighted.clear();
  updateHud();
  repaint();
}

const turnEl = document.getElementById("turn");
const phaseEl = document.getElementById("phase");
const resetBtn = document.getElementById("reset");
const endTurnBtn = document.getElementById("endTurn");
const toAttackBtn = document.getElementById("toAttack");
const toReinforceBtn = document.getElementById("toReinforce");

function updateHud() {
  if (phaseEl) phaseEl.textContent = `Phase: ${phase}`;
  if (turnEl) turnEl.textContent = `Current Player: Player ${currentPlayer}`;
}

if (toAttackBtn) {
  toAttackBtn.addEventListener("click", () => {
    if (!isMyTurn()) return;
    setPhase("attack");
  });
}

if (toReinforceBtn) {
  toReinforceBtn.addEventListener("click", () => {
    if (!isMyTurn()) return;
    setPhase("reinforce");
  });
}

if (endTurnBtn) {
  endTurnBtn.addEventListener("click", async () => {
    const response = await fetch("/api/endTurn", {method: "POST"});
    const data = await response.json();
    currentPlayer = data.turn;

    phase = "deploy";
    selectedId = null;
    lasthighlighted.clear();
    updateHud();
    repaint();
  });
}

async function resetGame() {
  await fetch("/api/reset", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({})
  });

  phase = "setup";
  currentPlayer = 1;
  updateHud();

  selectedId = null;
  lasthighlighted.clear();

  await updateState();
  if (selectedEl) selectedEl.textContent = `Selected: None`;
}

if (resetBtn) {
  resetBtn.addEventListener("click", resetGame);
}



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
  if (latestState && latestState.turn && latestState.turn !== 0) {
    currentPlayer = latestState.turn;
    updateHud();
  }
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

function IncPlayers()
{
  currentPlayer++;
  let players = 0; //PUT THE PLAYER NUMBER FUNCTION HERE
  if (currentPlayer>players) currentPlayer = 1;
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

  const start = await fetch("/api/start", { method: "POST" }).then(r => r.json()); // initialize game state
  playerCount = start.players || 2;

  updateHud();
  await updateState();
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
    if (!canClickTerritory()) return;

    // always refresh info from state
    const territoryName = idToName(p.id);
    const info = latestState.territories?.[territoryName];

    // ---- PHASE LOGIC ----
    if (phase === "setup") {
      if (!await isUnoccupied(territoryName)) return;
    
      await placeArmy(territoryName, currentPlayer, 1);
      await updateState();
    
      const data = await fetch("/api/availableSet", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({})
      }).then(r => r.json());
    
      if (data.out.length === 0) {
        phase = "deploy";
        updateHud();
        await updateState();
      } else {
        currentPlayer = (currentPlayer % playerCount) + 1;
        updateHud();
      }
    }

    else if (phase === "deploy") {
      if (!info || info.owner !== currentPlayer) return;
      await placeArmy(territoryName, currentPlayer, 1);
      await updateState();
    }

    else if (phase === "attack") {
      // for now: selection only (no placement)
      selectedId = p.id;
      repaint();
    }

    else if (phase === "reinforce") {
      if (!moveOrigin) {
        if (!info || info.owner !== currentPlayer) return;
        if ((info.armies || 0) < 2) return;
      
        moveOrigin = territoryName;
      
        const data = await fetch("/api/availableMove", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({ territory: moveOrigin, player: currentPlayer })
        }).then(r => r.json());
      
        moveTarget = new Set(data.out || []);
        lasthighlighted = new Set([...moveTarget].map(nameToId)); // highlight ids, not names
        repaint();
        return;
      }
    
      if (!moveTarget.has(territoryName)) {
        moveOrigin = null;
        moveTarget.clear();
        lasthighlighted.clear();
        repaint();
        return;
      }
    
      await fetch("/api/move", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ home: moveOrigin, territory: territoryName, player: currentPlayer, army: 1 })
      });
    
      moveOrigin = null;
      moveTarget.clear();
      lasthighlighted.clear();
      await updateState();
    }


    if (info) {
      selectedEl.textContent = `Selected: ${territoryName} | Owner: Player ${info.owner} | Troops: ${info.armies} | Phase: ${phase}`;
    } else {
      selectedEl.textContent = `Selected: ${territoryName} | Unoccupied | Phase: ${phase}`;
    }
  });
});

init();
