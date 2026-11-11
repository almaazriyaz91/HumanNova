/**
 * HumanNova 3D Atlas — Camera & Viewport Controls
 * Anatomical view presets: Anterior (Front), Posterior (Back), Lateral (Sides), Superior (Top).
 */

window.AtlasModelControls = (function() {
  const PRESETS = {
    front: { pos: [0, 1.1, 2.6], target: [0, 0.95, 0] },
    back:  { pos: [0, 1.1, -2.6], target: [0, 0.95, 0] },
    left:  { pos: [-2.6, 1.1, 0], target: [0, 0.95, 0] },
    right: { pos: [2.6, 1.1, 0], target: [0, 0.95, 0] },
    top:   { pos: [0, 3.2, 0.2], target: [0, 0.95, 0] }
  };

  let isTransitioning = false;
  let targetCamPos = null;
  let targetLookAt = null;

  function setViewPreset(presetName) {
    const preset = PRESETS[presetName] || PRESETS.front;
    const camera = AtlasViewer.getCamera();
    const controls = AtlasViewer.getControls();
    if (!camera || !controls) return;

    targetCamPos = new THREE.Vector3(...preset.pos);
    targetLookAt = new THREE.Vector3(...preset.target);
    isTransitioning = true;
  }

  function focusOnMesh(mesh) {
    if (!mesh) return;
    const box = new THREE.Box3().setFromObject(mesh);
    const center = new THREE.Vector3();
    box.getCenter(center);
    const size = new THREE.Vector3();
    box.getSize(size);

    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = AtlasViewer.getCamera().fov * (Math.PI / 180);
    const cameraDistance = Math.max(maxDim / (2 * Math.tan(fov / 2)), 0.6) * 1.5;

    targetLookAt = center.clone();
    targetCamPos = center.clone().add(new THREE.Vector3(0, 0.1, cameraDistance));
    isTransitioning = true;
  }

  // Smooth lerp update called on every frame
  function update() {
    if (!isTransitioning || !targetCamPos || !targetLookAt) return;
    const camera = AtlasViewer.getCamera();
    const controls = AtlasViewer.getControls();

    camera.position.lerp(targetCamPos, 0.08);
    controls.target.lerp(targetLookAt, 0.08);

    if (camera.position.distanceTo(targetCamPos) < 0.01 && controls.target.distanceTo(targetLookAt) < 0.01) {
      camera.position.copy(targetCamPos);
      controls.target.copy(targetLookAt);
      isTransitioning = false;
    }
  }

  // Register with viewer
  if (typeof AtlasViewer !== 'undefined') {
    AtlasViewer.addRenderCallback(update);
  }

  return {
    setViewPreset,
    focusOnMesh
  };
})();
