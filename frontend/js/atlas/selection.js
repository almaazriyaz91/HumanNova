/**
 * HumanNova 3D Atlas — Structure Selection & Inspection
 * Raycasting-based anatomical picking, highlight shaders, and information card integration.
 */

window.AtlasSelection = (function() {
  let raycaster, mouse;
  let selectedMesh = null;
  let originalEmissive = null;
  let isIsolated = false;

  function init() {
    raycaster = new THREE.Raycaster();
    mouse = new THREE.Vector2();

    const canvas = AtlasViewer.getRenderer().domElement;
    canvas.addEventListener('pointerdown', onPointerDown);

    setupCardActions();
  }

  function onPointerDown(event) {
    // Only handle primary left click
    if (event.button !== 0) return;

    const rect = event.target.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    pickStructure();
  }

  function pickStructure() {
    const camera = AtlasViewer.getCamera();
    const meshes = AtlasModelLoader.getActiveMeshes().filter(m => m.visible && m.userData.layer !== "skin");

    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(meshes, true);

    if (intersects.length > 0) {
      const hitMesh = intersects[0].object;
      selectMesh(hitMesh);
    } else {
      // Clicked background: don't immediately deselect if card is open, or deselect on double click
    }
  }

  function selectMesh(mesh, shouldFocus = false) {
    if (!mesh) return;

    // Restore previous selection highlight
    clearHighlight();

    selectedMesh = mesh;

    // Apply Electric Blue Highlight
    if (mesh.material) {
      if (Array.isArray(mesh.material)) {
        mesh.material.forEach(m => applyMeshGlow(m));
      } else {
        applyMeshGlow(mesh.material);
      }
    }

    // Resolve anatomy data
    const structure = resolveStructureData(mesh);
    displayInfoCard(structure, mesh);

    // Sync with OctSem AI Assistant
    if (window.OctSemChat) {
      OctSemChat.setActiveContext(structure);
    }

    if (shouldFocus && window.AtlasModelControls) {
      AtlasModelControls.focusOnMesh(mesh);
    }
  }

  function applyMeshGlow(mat) {
    if (!mat) return;
    if (mat.emissive) {
      originalEmissive = mat.emissive.clone();
      mat.emissive.setHex(0x38bdf8);
      mat.emissiveIntensity = 0.65;
    }
  }

  function clearHighlight() {
    if (selectedMesh && selectedMesh.material) {
      if (Array.isArray(selectedMesh.material)) {
        selectedMesh.material.forEach(m => {
          if (m.emissive) {
            m.emissive.setHex(0x000000);
            m.emissiveIntensity = 0;
          }
        });
      } else if (selectedMesh.material.emissive) {
        selectedMesh.material.emissive.setHex(0x000000);
        selectedMesh.material.emissiveIntensity = 0;
      }
    }
    selectedMesh = null;
  }

  function resolveStructureData(mesh) {
    const meshName = mesh.name || "";
    // 1. Check mesh.userData.extras
    if (mesh.userData && mesh.userData.extras && mesh.userData.extras.structure_id) {
      const ext = mesh.userData.extras;
      const cached = window.HumanNovaAnatomy.structures[ext.structure_id];
      if (cached) return cached;
      return {
        id: ext.structure_id,
        name: ext.name || meshName,
        system: ext.system || "Human Anatomy",
        layer: ext.layer || "organs",
        description: "Anatomical structure identified in current 3D model."
      };
    }

    // 2. Lookup in HumanNovaAnatomy
    const matched = window.HumanNovaAnatomy.findStructureByMeshName(meshName);
    if (matched) return matched;

    // 3. Fallback generic
    return {
      id: meshName,
      name: formatMeshName(meshName),
      system: "Anatomical Structure",
      layer: mesh.userData.layer || "organs",
      description: "Select structure to explore detailed anatomy and learning concepts with OctSem AI."
    };
  }

  function formatMeshName(raw) {
    return raw.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
  }

  function displayInfoCard(structure, mesh) {
    const card = document.getElementById("anatomy-info-card");
    if (!card) return;

    document.getElementById("card-structure-name").textContent = structure.name || "Structure";
    document.getElementById("card-system-badge").textContent = structure.system || "Anatomy";
    document.getElementById("card-layer-badge").textContent = (structure.layer || "organs").toUpperCase();
    
    document.getElementById("card-description-text").textContent = structure.description || "Reviewed anatomical structure.";
    document.getElementById("card-location-text").textContent = structure.location || "Positioned in standard anatomical alignment.";
    document.getElementById("card-function-text").textContent = structure.function || "Supports physiological and anatomical homeostasis.";
    document.getElementById("card-clinical-text").textContent = structure.clinical_notes || "Clinical correlation available in OctSem AI.";

    card.style.display = "block";
  }

  function hideInfoCard() {
    const card = document.getElementById("anatomy-info-card");
    if (card) card.style.display = "none";
    clearHighlight();
    if (isIsolated) restoreIsolation();
  }

  function setupCardActions() {
    const closeBtn = document.getElementById("card-close-btn");
    if (closeBtn) closeBtn.addEventListener("click", hideInfoCard);

    const askAiBtn = document.getElementById("card-ask-ai-btn");
    if (askAiBtn) {
      askAiBtn.addEventListener("click", () => {
        if (window.OctSemChat) {
          OctSemChat.openSidebar();
          OctSemChat.promptQuickQuestion("Explain the clinical importance of this structure.");
        }
      });
    }

    const isolateBtn = document.getElementById("card-isolate-btn");
    if (isolateBtn) {
      isolateBtn.addEventListener("click", () => {
        if (!selectedMesh) return;
        if (!isIsolated) {
          isolateStructure(selectedMesh);
          isolateBtn.innerHTML = '<i class="fa-solid fa-eye"></i> Show Full Body';
        } else {
          restoreIsolation();
          isolateBtn.innerHTML = '<i class="fa-solid fa-cube"></i> Isolate in 3D';
        }
      });
    }
  }

  function isolateStructure(mesh) {
    const allMeshes = AtlasModelLoader.getActiveMeshes();
    allMeshes.forEach(m => {
      m.visible = (m === mesh);
    });
    isIsolated = true;
    if (window.AtlasModelControls) {
      AtlasModelControls.focusOnMesh(mesh);
    }
  }

  function restoreIsolation() {
    const activeLayers = window.AtlasLayers ? AtlasLayers.getActiveLayerState() : null;
    const allMeshes = AtlasModelLoader.getActiveMeshes();
    
    allMeshes.forEach(m => {
      const layer = m.userData.layer;
      if (activeLayers && activeLayers[layer] !== undefined) {
        m.visible = activeLayers[layer];
      } else {
        m.visible = true;
      }
    });
    isIsolated = false;
  }

  function selectById(structureId) {
    const s = window.HumanNovaAnatomy.structures[structureId];
    if (!s) return false;

    const allMeshes = AtlasModelLoader.getActiveMeshes();
    for (let m of allMeshes) {
      if (s.model_mesh_names && s.model_mesh_names.includes(m.name)) {
        selectMesh(m, true);
        return true;
      }
      if (m.name.toLowerCase().includes(structureId.toLowerCase())) {
        selectMesh(m, true);
        return true;
      }
    }
    return false;
  }

  return {
    init,
    selectMesh,
    selectById,
    clearHighlight,
    hideInfoCard
  };
})();
