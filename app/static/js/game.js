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

// --- Cached label positions ---
const centroidCache = new Map();

function approxCentroid(path, samples = 30) {
  const total = path.getTotalLength();
  let sx = 0, sy = 0;

  for (let i = 0; i < samples; i++) {
    const t = (i + 0.5) / samples;
    const p = path.getPointAtLength(total * t);
    sx += p.x;
    sy += p.y;
  }
  return { x: sx / samples, y: sy / samples };
}

function buildCentroidCacheOnce() {
  if (!layer) return;
  if (centroidCache.size > 0) return;

  layer.querySelectorAll("path").forEach(path => {
    const id = path.id;
    if (!id) return;
    centroidCache.set(id, approxCentroid(path, 20));
  });
}


// -- Global State / DOM Refs --
let map = null;
let latestState = null;

const layer = document.getElementById("layer4"); // contains the 42 territories
const selectedEl = document.getElementById("selected"); // get selected territory display
const troopsEl = document.getElementById("troopsLeft");

let selectedId = null;
let lasthighlighted = new Set();

let attackOrigin = null;
let attackTargets = new Set();

let phase = "setup";
let currentPlayer = 1;
let playerCount = 2;

let moveOrigin = null;
let moveTarget = new Set();

let gameOver = false;

function showWinScreen(winner) {
  gameOver = true;

  let overlay = document.getElementById("winOverlay");
  if (overlay) overlay.remove();

  overlay = document.createElement("div");
  overlay.id = "winOverlay";
  overlay.style.position = "fixed";
  overlay.style.inset = "0";
  overlay.style.background = "rgba(0,0,0,0.7)";
  overlay.style.display = "flex";
  overlay.style.alignItems = "center";
  overlay.style.justifyContent = "center";
  overlay.style.zIndex = "9999";

  const card = document.createElement("div");
  card.style.background = "white";
  card.style.padding = "24px";
  card.style.borderRadius = "12px";
  card.style.maxWidth = "520px";
  card.style.width = "90%";
  card.style.textAlign = "center";

  const h = document.createElement("h1");
  h.textContent = `Player ${winner} wins!`;
  h.style.marginBottom = "12px";

  const p = document.createElement("p");
  p.textContent = "Game over.";
  p.style.marginBottom = "20px";

  const btn = document.createElement("button");
  btn.textContent = "Return to Menu";
  btn.className = "btn btn-primary";
  btn.addEventListener("click", () => {
    window.location.href = "/menu";
  });

  card.appendChild(h);
  card.appendChild(p);
  card.appendChild(btn);
  overlay.appendChild(card);
  document.body.appendChild(overlay);
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
  
  attackOrigin = null;
  attackTargets.clear();
  
  moveOrigin = null;
  moveTarget.clear();
  
  lasthighlighted.clear();
  updateHud();
  repaint();
}

const turnEl = document.getElementById("turn");
const phaseEl = document.getElementById("phase");
const resetBtn = document.getElementById("reset");
const endTurnBtn = document.getElementById("endPhase");
const toAttackBtn = document.getElementById("toAttack");
const toReinforceBtn = document.getElementById("toReinforce");

function updateHud() {
  if (phaseEl) phaseEl.textContent = `Phase: ${phase}`;
  if (turnEl) turnEl.textContent = `Current Player: Player ${currentPlayer}`;

  const pool = latestState?.armies?.[currentPlayer - 1];
  if (troopsEl) troopsEl.textContent = `Troops left: ${pool ?? "?"}`;
}

if (endTurnBtn) {
  endTurnBtn.addEventListener("click", async () => {
    if (phase === "attack") {
      setPhase("reinforce");
      return;
    }

    if (phase !== "reinforce") return;

    const response = await fetch("/api/endTurn", { method: "POST" });
    const data = await response.json();
    currentPlayer = data.turn;

    phase = "deploy";
    attackOrigin = null;
    attackTargets.clear();
    moveOrigin = null;
    moveTarget.clear();
    selectedId = null;
    lasthighlighted.clear();

    await updateState();
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


// --- Troop Labels (SVG text overlays) ---
const svg = layer?.ownerSVGElement || document.querySelector("svg");
let labelsLayer = null;

function ensureLabelsLayer() {
  if (!layer) return null;
  if (labelsLayer) return labelsLayer;

  labelsLayer = document.createElementNS("http://www.w3.org/2000/svg", "g");
  labelsLayer.setAttribute("id", "troopLabels");
  labelsLayer.style.pointerEvents = "none";
  layer.appendChild(labelsLayer);
  return labelsLayer;
}

function getOrCreateLabel(id) {
  const g = ensureLabelsLayer();
  if (!g) return null;

  let t = g.querySelector(`text[data-for='${id}']`);
  if (t) return t;

  t = document.createElementNS("http://www.w3.org/2000/svg", "text");
  t.setAttribute("data-for", id);
  t.setAttribute("text-anchor", "middle");
  t.setAttribute("dominant-baseline", "middle");
  t.style.fontSize = "12px";
  t.style.fontWeight = "700";
  t.style.paintOrder = "stroke";
  t.style.stroke = "white";
  t.style.strokeWidth = "3px";
  t.style.fill = "#111";
  g.appendChild(t);
  return t;
}

function updateTroopLabels(state) {
  if (!state?.territories) return;

  for (const [territoryName, info] of Object.entries(state.territories)) {
    const id = nameToId(territoryName);
    const path = document.getElementById(id);
    if (!path) continue;

    const pos = centroidCache.get(id);
    if (!pos) continue;

    const label = getOrCreateLabel(id);
    if (!label) continue;

    label.setAttribute("x", pos.x);
    label.setAttribute("y", pos.y);

    const n = Number(info.armies ?? 0);
    label.textContent = n > 0 ? String(n) : "";
  }
}


// centroid-ish point by sampling the path (usually inside, not on border)
function approxCentroid(path, samples = 30) {
  const total = path.getTotalLength();
  let sx = 0, sy = 0;

  for (let i = 0; i < samples; i++) {
    const t = (i + 0.5) / samples;      // midpoints of each segment
    const p = path.getPointAtLength(total * t);
    sx += p.x;
    sy += p.y;
  }
  return { x: sx / samples, y: sy / samples };
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

async function placeArmy(territory, player, army = 1) {
  const response = await fetch("/api/addTerritory", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ home: null, territory, player, army })
  });
  const data = await response.json();
  if (!data.success) {
    console.error(data.error);
    return false;
  }
  await updateState();
  return true;
}

async function updateState() {
  latestState = await fetchState();
  if (latestState?.winner && latestState.winner !== 0) {
    showWinScreen(latestState.winner);
    return;
  }

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

function setHighlightedByNames(names) {
  lasthighlighted.clear();
  (names || []).forEach(name => lasthighlighted.add(nameToId(name)));
  repaint(true);
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

  if (latestState) updateTroopLabels(latestState);
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

  buildCentroidCacheOnce();

  const start = await fetch("/api/start", { method: "POST" }).then(r => r.json());
  playerCount = start.players || 2;
  currentPlayer = 1;

  await updateState();
  updateHud();
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
    // always refresh info from state
    const territoryName = idToName(p.id);
    const info = latestState.territories?.[territoryName];

    // ---- PHASE LOGIC ----
    if (phase === "setup") {
      if (!await isUnoccupied(territoryName)) return;
        
      const ok = await placeArmy(territoryName, currentPlayer, 1);
      if (!ok) return;
        
      // advance the turn on the server
      await fetch("/api/nextTurn", { method: "POST" });
        
      // resync client with server turn
      await updateState();
        
      const data = await fetch("/api/availableSet", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({})
      }).then(r => r.json());
    
      if (data.out.length === 0) {
        phase = "deploy";
        updateHud();
      }
      return;
    }

    else if (phase === "deploy") {
      if (!info || info.owner !== currentPlayer) return;
    
      const ok = await placeArmy(territoryName, currentPlayer, 1);
      if (!ok) return;
      await updateState();

      const pools = latestState.armies || [];

      const anyoneHasTroops = pools.slice(0, playerCount).some(x => x > 0);
      if (!anyoneHasTroops) {
        phase = "attack";
        updateHud();
        return;
      }
    
      if ((pools[currentPlayer - 1] || 0) > 0) {
        updateHud();
        return;
      }
    
      await fetch("/api/endTurn", { method: "POST" });
      await updateState();
    }

    else if (phase === "attack") {
      if (!attackOrigin) {
        if (!info || info.owner !== currentPlayer) return;
        if ((info.armies || 0) < 2) return;
      
        attackOrigin = territoryName;
        selectedId = nameToId(attackOrigin);
      
        const data = await fetch("/api/availableAttack", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ territory: attackOrigin, player: currentPlayer })
        }).then(r => r.json());
      
        attackTargets = new Set(data.out || []);
        setHighlightedByNames([...attackTargets]);
        return;
      }
    
      if (!attackTargets.has(territoryName)) {
        attackOrigin = null;
        attackTargets.clear();
        lasthighlighted.clear();
        selectedId = null;
        repaint(true);
        return;
      }
    
      const result = await fetch("/api/attackTerritory", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          territory: territoryName,
          player: currentPlayer,
          origin: attackOrigin
        })
      }).then(r => r.json());
    
      await updateState();
    
      const originInfo = latestState?.territories?.[attackOrigin];
      if (!originInfo || (originInfo.armies || 0) < 2) {
        attackOrigin = null;
        attackTargets.clear();
        lasthighlighted.clear();
        selectedId = null;
        repaint(true);
        return;
      }
    
      const data2 = await fetch("/api/availableAttack", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ territory: attackOrigin, player: currentPlayer })
      }).then(r => r.json());
    
      attackTargets = new Set(data2.out || []);
      setHighlightedByNames([...attackTargets]);
    
      if (selectedEl) {
        selectedEl.textContent =
          `Attack from ${attackOrigin} -> ${territoryName}: ${result.out ? "hit" : "miss"} | Phase: ${phase}`;
      }
      return;
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


    const freshInfo = latestState?.territories?.[territoryName] || null;

    if (freshInfo) {
      selectedEl.textContent =
        `Selected: ${territoryName} | Owner: Player ${freshInfo.owner} | Troops: ${freshInfo.armies} | Phase: ${phase}`;
    } else {
      selectedEl.textContent = `Selected: ${territoryName} | Unoccupied | Phase: ${phase}`;
    }

  });
});

init();
