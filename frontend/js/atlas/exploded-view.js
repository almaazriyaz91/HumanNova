/**
 * HumanNova 3D Atlas — Exploded View Module
 * Smoothly separates anatomical layers radially using mathematical offsets, allowing students
 * to inspect internal relationships without confusing overlaps, and smoothly restores original positions.
 */

window.AtlasExplodedView = (function() {
  let isExploded = false;
  let animProgress = 0.0; // 0 = normal, 1 = exploded
  let targetProgress = 0.0;
  const SPEED = 0.06;

  function init() {
    AtlasViewer.addRenderCallback(updateAnimation);
  }

  function toggleExplodedView() {
    isExploded = !isExploded;
    targetProgress = isExploded ? 1.0 : 0.0;
    return isExploded;
  }

  function setExplodedState(state) {
    isExploded = state;
    targetProgress = isExploded ? 1.0 : 0.0;
  }

  function updateAnimation() {
    if (Math.abs(animProgress - targetProgress) < 0.001) {
      animProgress = targetProgress;
      return;
    }

    // Smooth quadratic ease
    animProgress += (targetProgress - animProgress) * SPEED;

    const meshes = AtlasModelLoader.getActiveMeshes();
    for (let i = 0; i < meshes.length; i++) {
      const mesh = meshes[i];
      const origPos = mesh.userData.originalPosition;
      if (!origPos) continue;

      let offset = [0, 0, 0];
      if (mesh.userData.extras && mesh.userData.extras.exploded_offset) {
        offset = mesh.userData.extras.exploded_offset;
      } else {
        // Compute default radial expansion based on layer
        const layer = mesh.userData.layer;
        if (layer === "organs") offset = [0, 0, 0.35];
        else if (layer === "muscles") offset = [origPos.x * 0.8, 0, 0.2];
        else if (layer === "veins") offset = [0, 0, 0.15];
        else if (layer === "bones") offset = [0, 0, -0.15];
        else if (layer === "skin") offset = [0, 0, 0.45];
      }

      mesh.position.x = origPos.x + offset[0] * animProgress;
      mesh.position.y = origPos.y + offset[1] * animProgress;
      mesh.position.z = origPos.z + offset[2] * animProgress;
    }
  }

  return {
    init,
    toggleExplodedView,
    setExplodedState,
    isExploded: () => isExploded
  };
})();
