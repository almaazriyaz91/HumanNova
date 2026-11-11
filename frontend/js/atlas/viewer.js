/**
 * HumanNova 3D Atlas — Viewer Engine
 * Sets up the Three.js scene, camera, lighting, OrbitControls, and animation loop.
 */

window.AtlasViewer = (function() {
  let scene, camera, renderer, controls;
  let container;
  let animationId = null;
  let isAutoRotate = false;
  let isWireframe = false;
  
  // Custom event hooks
  const onRenderCallbacks = [];

  function init(containerId) {
    container = document.getElementById(containerId);
    if (!container) {
      console.error(`[AtlasViewer] Container '#${containerId}' not found.`);
      return;
    }

    const width = container.clientWidth;
    const height = container.clientHeight;

    // 1. Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x06080d);
    scene.fog = new THREE.FogExp2(0x06080d, 0.12);

    // 2. Camera (Perspective)
    camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(0, 1.1, 2.6);

    // 3. Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.25;
    renderer.outputEncoding = THREE.sRGBEncoding;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    container.appendChild(renderer.domElement);

    // 4. OrbitControls
    if (typeof THREE.OrbitControls !== 'undefined') {
      controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.target.set(0, 0.95, 0); // Focus on mid-torso / center of human body
      controls.minDistance = 0.4;
      controls.maxDistance = 6.0;
      controls.maxPolarAngle = Math.PI - 0.05;
    }

    // 5. Studio Lighting Setup
    setupLighting();

    // 6. Subtle Ground Grid & Reflection
    setupGround();

    // 7. Responsive Resize Observer
    window.addEventListener('resize', onWindowResize);

    // 8. Animation Loop
    animate();
    console.log("[AtlasViewer] 3D Viewer initialized successfully.");
  }

  function setupLighting() {
    // Soft Ambient Light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);

    // Key Light (Warm Front-Right)
    const keyLight = new THREE.DirectionalLight(0xfff5ea, 1.4);
    keyLight.position.set(3, 4, 3.5);
    keyLight.castShadow = true;
    keyLight.shadow.mapSize.width = 1024;
    keyLight.shadow.mapSize.height = 1024;
    scene.add(keyLight);

    // Fill Light (Cool Cyan Front-Left)
    const fillLight = new THREE.DirectionalLight(0x38bdf8, 0.85);
    fillLight.position.set(-3, 2, 2.5);
    scene.add(fillLight);

    // Rim / Backlight (Electric Blue Contouring)
    const rimLight = new THREE.DirectionalLight(0x818cf8, 1.2);
    rimLight.position.set(0, 3, -3.5);
    scene.add(rimLight);

    // Bottom Underlight (Gentle bounce)
    const bounceLight = new THREE.DirectionalLight(0x1e293b, 0.4);
    bounceLight.position.set(0, -2, 1);
    scene.add(bounceLight);
  }

  function setupGround() {
    // Radial circular subtle grid
    const gridHelper = new THREE.PolarGridHelper(1.8, 16, 8, 32, 0x1e293b, 0x0f172a);
    gridHelper.position.y = -0.01;
    scene.add(gridHelper);
  }

  function onWindowResize() {
    if (!container || !renderer || !camera) return;
    const width = container.clientWidth;
    const height = container.clientHeight;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
  }

  function animate() {
    animationId = requestAnimationFrame(animate);

    if (controls) {
      if (isAutoRotate) {
        controls.autoRotate = true;
        controls.autoRotateSpeed = 1.2;
      } else {
        controls.autoRotate = false;
      }
      controls.update();
    }

    // Call external registered update loops (e.g., exploded view tweening)
    for (let cb of onRenderCallbacks) {
      cb();
    }

    renderer.render(scene, camera);
  }

  function addRenderCallback(cb) {
    onRenderCallbacks.push(cb);
  }

  function toggleAutoRotate(state) {
    isAutoRotate = (state !== undefined) ? state : !isAutoRotate;
    return isAutoRotate;
  }

  function toggleWireframe(state) {
    isWireframe = (state !== undefined) ? state : !isWireframe;
    scene.traverse((obj) => {
      if (obj.isMesh && obj.material) {
        if (Array.isArray(obj.material)) {
          obj.material.forEach(m => m.wireframe = isWireframe);
        } else {
          obj.material.wireframe = isWireframe;
        }
      }
    });
    return isWireframe;
  }

  function resetCamera() {
    if (!controls) return;
    controls.reset();
    camera.position.set(0, 1.1, 2.6);
    controls.target.set(0, 0.95, 0);
  }

  return {
    init,
    getScene: () => scene,
    getCamera: () => camera,
    getRenderer: () => renderer,
    getControls: () => controls,
    addRenderCallback,
    toggleAutoRotate,
    toggleWireframe,
    resetCamera
  };
})();
