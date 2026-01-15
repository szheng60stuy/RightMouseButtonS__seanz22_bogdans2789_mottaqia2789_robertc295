console.log("game.js loaded");


// territory tables taken from game.py but without the continent grouping
const territories = {
    // --- North America ---
    "Alaska": ["Northwest Territory", "Alberta", "Kamchatka"],
    "Northwest Territory": [ "Alaska", "Alberta", "Ontario", "Greenland"],
    "Greenland": ["Northwest Territory", "Ontario", "Quebec", "Iceland"],
    "Alberta": ["Alaska", "Northwest Territory", "Ontario", "Western United States"],
    "Ontario": ["Northwest Territory", "Greenland", "Quebec", "Eastern United States", "Western United States", "Alberta"],
    "Quebec": ["Ontario", "Greenland", "Eastern United States"],
    "Western United States": ["Alberta", "Ontario", "Eastern United States", "Central America"],
    "Eastern United States": ["Ontario", "Quebec", "Western United States", "Central America"],
    "Central America": ["Western United States", "Eastern United States", "Venezuela"],

    // --- South America ---
    "Venezuela": ["Central America", "Brazil", "Peru"],
    "Peru": ["Venezuela", "Brazil", "Argentina"],
    "Brazil": ["Venezuela", "Peru", "Argentina", "North Africa"],
    "Argentina": ["Peru", "Brazil"],

    // --- Europe ---
    "Iceland": ["Greenland", "Great Britain", "Scandinavia"],
    "Scandinavia": ["Iceland", "Northern Europe", "Ukraine"],
    "Great Britain": ["Iceland", "Scandinavia", "Northern Europe", "Western Europe"],
    "Northern Europe": ["Great Britain", "Scandinavia", "Ukraine", "Southern Europe", "Western Europe"],
    "Western Europe": ["Great Britain", "Northern Europe", "Southern Europe", "North Africa"],
    "Southern Europe": ["Western Europe", "Northern Europe", "Ukraine", "Middle East", "Egypt"],

    // --- Africa ---
    "North Africa": ["Brazil", "Western Europe", "Southern Europe", "Egypt", "East Africa", "Congo"],
    "Egypt": ["North Africa", "Southern Europe", "Middle East", "East Africa"],
    "East Africa": ["Egypt", "North Africa", "Congo", "South Africa", "Madagascar", "Middle East"],
    "Congo": ["North Africa", "East Africa", "South Africa"],
    "South Africa": ["Congo", "East Africa", "Madagascar"],
    "Madagascar": ["South Africa", "East Africa"],

    // --- Asia ---
    "Ural": ["Ukraine", "Siberia", "China", "Afghanistan"],
    "Siberia": ["Ural", "Yakutsk", "Irkutsk", "Mongolia", "China"],
    "Yakutsk": ["Siberia", "Irkutsk", "Kamchatka"],
    "Kamchatka": ["Yakutsk", "Irkutsk", "Mongolia", "Japan", "Alaska"],
    "Irkutsk": ["Siberia", "Yakutsk", "Kamchatka", "Mongolia"],
    "Mongolia": ["Siberia", "Irkutsk", "Kamchatka", "Japan", "China"],
    "Japan": ["Kamchatka", "Mongolia"],
    "Afghanistan": ["Ukraine", "Ural", "China", "India", "Middle East"],
    "Middle East": ["Southern Europe", "Egypt", "East Africa", "Afghanistan", "India"],
    "India": ["Middle East", "Afghanistan", "China", "Siam"],
    "China": ["Ural", "Siberia", "Mongolia", "India", "Siam", "Afghanistan"],
    "Siam": ["India", "China", "Indonesia"],
    "Ukraine": ["Scandinavia", "Northern Europe", "Southern Europe", "Ural", "Afghanistan"],

    // --- Australia ---
    "Indonesia": ["Siam", "New Guinea", "Western Australia"],
    "New Guinea": ["Indonesia", "Western Australia", "Eastern Australia"],
    "Western Australia": ["Indonesia", "New Guinea", "Eastern Australia"],
    "Eastern Australia": ["Western Australia", "New Guinea"]
	}
  
  const layer = document.getElementById("layer4"); // contains the 42 territories
  const selectedEl = document.getElementById("selected"); // get selected territory display
  
  let selectedId = null;  
  let lasthighlighted = [];
  
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
      if (el && id !== selectedId) el.style.fill = "#eaeaea";
    });
    lasthighlighted = [];
  }
  // function to highlight adjacent territories
  function highlightAdjacent(name) {
    const adjacents = territories[name];
    adjacents.forEach(adj => {
      const adjId = nameToId(adj);
      const el = document.getElementById(adjId);
      if (el) {
        el.style.fill = "#000000";
        lasthighlighted.push(adjId);
      }
    });
  }

  // animations and event listeners for each territory
  layer.querySelectorAll("path").forEach(p => {
    p.style.cursor = "pointer";
    p.style.fill = "#eaeaea";          // default territory color
    p.style.transition = "fill 120ms, stroke-width 120ms";
    p.style.stroke = "#111";
    p.style.strokeWidth = "1";

    p.addEventListener("mouseenter", () => {
      if (p.id !== selectedId && (p.id in lasthighlighted)) p.style.fill = "#d6d6d6";
      p.style.strokeWidth = "2";
    });

    p.addEventListener("mouseleave", () => {
      if (p.id !== selectedId && (p.id in lasthighlighted)) p.style.fill = "#eaeaea";
      p.style.strokeWidth = "1";
    });


    // highlight selected territory and adjacent territories
    p.addEventListener("click", () => {
      // unselect old territory
      clearHighlights();
      if (selectedId) {
        const old = document.getElementById(selectedId);
        if (old) old.style.fill = "#eaeaea";
      }

      selectedId = p.id;
      p.style.fill = "#bcdcff";

      const territoryName = idToName(p.id);
      highlightAdjacent(territoryName);
    });
  });
