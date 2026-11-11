/**
 * HumanNova 3D Atlas — Real-time Anatomy Search
 * Provides instant search with autocomplete dropdown, structure highlight, and camera focus.
 */

window.AtlasSearch = (function() {
  let searchInput, resultsDropdown;

  function init() {
    searchInput = document.getElementById("atlas-search-input");
    resultsDropdown = document.getElementById("search-results-dropdown");

    if (!searchInput || !resultsDropdown) return;

    searchInput.addEventListener("input", onSearchInput);
    searchInput.addEventListener("focus", onSearchInput);

    // Hide dropdown when clicking outside
    document.addEventListener("click", (e) => {
      if (!searchInput.contains(e.target) && !resultsDropdown.contains(e.target)) {
        hideDropdown();
      }
    });
  }

  function onSearchInput() {
    const query = searchInput.value.trim().toLowerCase();
    if (!query) {
      hideDropdown();
      return;
    }

    const currentGender = AtlasModelLoader.getCurrentGender();
    const results = [];

    // Filter structures
    const allStructures = window.HumanNovaAnatomy.structures;
    for (const id in allStructures) {
      const s = allStructures[id];
      const g = s.gender || "both";
      if (g !== "both" && g !== currentGender) continue;

      const name = (s.name || "").toLowerCase();
      const system = (s.system || "").toLowerCase();
      const desc = (s.description || "").toLowerCase();

      if (name.includes(query) || system.includes(query) || id.includes(query) || desc.includes(query)) {
        results.push(s);
      }
    }

    renderResults(results);
  }

  function renderResults(results) {
    resultsDropdown.innerHTML = "";
    if (results.length === 0) {
      const emptyItem = document.createElement("div");
      emptyItem.className = "search-result-item";
      emptyItem.innerHTML = `<span style="color: var(--text-muted);">No anatomical structures found</span>`;
      resultsDropdown.appendChild(emptyItem);
      resultsDropdown.style.display = "flex";
      return;
    }

    results.slice(0, 8).forEach(s => {
      const item = document.createElement("div");
      item.className = "search-result-item";
      item.innerHTML = `
        <span class="search-result-name">${s.name}</span>
        <span class="search-result-system">${s.system}</span>
      `;
      item.addEventListener("click", () => {
        selectResult(s);
      });
      resultsDropdown.appendChild(item);
    });

    resultsDropdown.style.display = "flex";
  }

  function selectResult(structure) {
    hideDropdown();
    searchInput.value = structure.name;

    // Trigger 3D selection
    const success = AtlasSelection.selectById(structure.id);
    if (!success) {
      console.warn(`[AtlasSearch] Structure '${structure.id}' not selectable in current visual state.`);
    }
  }

  function hideDropdown() {
    if (resultsDropdown) resultsDropdown.style.display = "none";
  }

  return {
    init
  };
})();
