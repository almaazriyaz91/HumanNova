/**
 * HumanNova 3D Atlas — Anatomical Layer Visibility
 * Controls visibility for: Skin, Muscles, Veins & Blood Vessels, Bones, Organs.
 */

window.AtlasLayers = (function() {
  const layerState = {
    skin: false,     // Skin off by default to reveal muscles/ecorche as in reference images!
    muscles: true,
    veins: true,
    bones: true,
    organs: true
  };

  function init() {
    const layerItems = document.querySelectorAll(".layer-item");
    layerItems.forEach(item => {
      const layerName = item.dataset.layer;
      const checkbox = item.querySelector(".layer-checkbox");

      if (checkbox) {
        checkbox.checked = layerState[layerName];
        updateItemUI(item, layerState[layerName]);

        item.addEventListener("click", (e) => {
          if (e.target !== checkbox) {
            checkbox.checked = !checkbox.checked;
          }
          setLayerVisibility(layerName, checkbox.checked);
          updateItemUI(item, checkbox.checked);
        });

        checkbox.addEventListener("change", () => {
          setLayerVisibility(layerName, checkbox.checked);
          updateItemUI(item, checkbox.checked);
        });
      }
    });
  }

  function setLayerVisibility(layerName, isVisible) {
    layerState[layerName] = isVisible;
    const layerMap = AtlasModelLoader.getLayerMap();
    const meshes = layerMap[layerName] || [];

    meshes.forEach(m => {
      m.visible = isVisible;
    });

    console.log(`[AtlasLayers] Layer '${layerName}' set to visible=${isVisible} (${meshes.length} objects)`);
  }

  function updateItemUI(item, isActive) {
    if (isActive) {
      item.classList.add("active");
    } else {
      item.classList.remove("active");
    }
  }

  function applyCurrentLayers() {
    for (const layer in layerState) {
      setLayerVisibility(layer, layerState[layer]);
    }
  }

  return {
    init,
    setLayerVisibility,
    applyCurrentLayers,
    getActiveLayerState: () => ({ ...layerState })
  };
})();
