/**
 * HumanNova 3D Atlas — Viewer Engine (Ultra-Realistic PBR Upgrade)
 * Sets up the Three.js scene, camera, studio lighting, environment map,
 * OrbitControls, and animation loop for anatomical reference rendering.
 *
 * Three.js r134 — MeshPhysicalMaterial, PMREMGenerator, RoomEnvironment
 */

window.AtlasViewer = (function() {
  let scene, camera, renderer, controls;
  let container;
  let animationId = null;
  let isAutoRotate = false;
  let isWireframe = false;

  // External render callbacks (exploded-view tweening, etc.)
  const onRenderCallbacks = [];

  // ─── Init ────────────────────────────────────────────────────────────────
  function init(containerId) {
    container = document.getElementById(containerId);
    if (!container) {
      console.error('[AtlasViewer] Container \'#' + containerId + '\' not found.');
      return;
    }

    const width  = container.clientWidth;
    const height = container.clientHeight;

    // 1. Scene — deep space black, NO fog (keeps model crisp)
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x08090f);

    // Vignette: large inside-out dark sphere around the scene
    const bgSphere = new THREE.Mesh(
      new THREE.SphereGeometry(50, 16, 8),
      new THREE.MeshBasicMaterial({ color: 0x040508, side: THREE.BackSide })
    );
    scene.add(bgSphere);

    // 2. Camera (Perspective)
    camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(0, 1.1, 2.6);

    // 3. Renderer — full PBR pipeline
    renderer = new THREE.WebGLRenderer({
      antialias:         true,
      alpha:             true,
      powerPreference:   'high-performance'
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2.5));
    renderer.physicallyCorrectLights = true;          // PBR energy conservation (r134)
    renderer.toneMapping              = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure      = 1.1;
    renderer.outputEncoding           = THREE.sRGBEncoding;
    renderer.shadowMap.enabled        = true;
    renderer.shadowMap.type           = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);

    // 4. Environment map — RoomEnvironment PMREM for wet-tissue reflections
    setupEnvironmentMap();

    // 5. OrbitControls
    if (typeof THREE.OrbitControls !== 'undefined') {
      controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.enableDamping  = true;
      controls.dampingFactor  = 0.05;
      controls.target.set(0, 0.95, 0);  // Focus on mid-torso / body centre
      controls.minDistance    = 0.4;
      controls.maxDistance    = 6.0;
      controls.maxPolarAngle  = Math.PI - 0.05;
    }

    // 6. Professional anatomical studio lighting
    setupLighting();

    // 7. Reflective ground disc (replaces PolarGridHelper)
    setupGround();

    // 8. Responsive resize
    window.addEventListener('resize', onWindowResize);

    // 9. Animation loop
    animate();
    console.log('[AtlasViewer] PBR viewer initialized (Three.js r134).');
  }

  // ─── Environment Map ─────────────────────────────────────────────────────
  function setupEnvironmentMap() {
    if (typeof THREE.RoomEnvironment !== 'undefined') {
      // Preferred path: RoomEnvironment PMREM (r134 CDN)
      var pmremGenerator = new THREE.PMREMGenerator(renderer);
      pmremGenerator.compileEquirectangularShader();
      var envScene   = new THREE.RoomEnvironment();
      var envTexture = pmremGenerator.fromScene(envScene, 0.04).texture;
      scene.environment = envTexture;
      pmremGenerator.dispose();
      console.log('[AtlasViewer] RoomEnvironment PMREM applied.');
    } else {
      // Fallback: neutral-grey DataTexture env map
      var size = 4;
      var data = new Uint8Array(size * size * 4);
      for (var i = 0; i < size * size; i++) {
        var off = i * 4;
        data[off]     = 180;
        data[off + 1] = 185;
        data[off + 2] = 190;
        data[off + 3] = 255;
      }
      var fallbackTex = new THREE.DataTexture(data, size, size, THREE.RGBAFormat);
      fallbackTex.needsUpdate = true;
      scene.environment = fallbackTex;
      console.warn('[AtlasViewer] RoomEnvironment not found — using fallback DataTexture env.');
    }
  }

  // ─── Studio Lighting ─────────────────────────────────────────────────────
  function setupLighting() {
    // Hemisphere ambient — sky blue-grey over earthy ground
    var hemi = new THREE.HemisphereLight(0x8898aa, 0x544836, 0.5);
    scene.add(hemi);

    // Key light — warm diffuse from upper-right front
    var keyLight = new THREE.DirectionalLight(0xfff8f0, 1.6);
    keyLight.position.set(2.5, 4, 3);
    keyLight.castShadow              = true;
    keyLight.shadow.mapSize.width    = 2048;
    keyLight.shadow.mapSize.height   = 2048;
    keyLight.shadow.camera.near      = 0.1;
    keyLight.shadow.camera.far       = 20;
    keyLight.shadow.bias             = -0.0005;
    scene.add(keyLight);

    // Fill light — cool blue from upper-left front
    var fillLight = new THREE.DirectionalLight(0xe8f4ff, 0.8);
    fillLight.position.set(-3, 2, 2);
    scene.add(fillLight);

    // Rim / contour light — pure white from directly behind
    var rimLight = new THREE.DirectionalLight(0xffffff, 0.9);
    rimLight.position.set(0, 2, -4);
    scene.add(rimLight);

    // Under fill — warm bounce from below (simulates bounce off operating table)
    var underFill = new THREE.DirectionalLight(0xffe8d0, 0.4);
    underFill.position.set(0, -3, 1);
    scene.add(underFill);
  }

  // ─── Ground Disc ─────────────────────────────────────────────────────────
  function setupGround() {
    var ground = new THREE.Mesh(
      new THREE.CircleGeometry(2, 64),
      new THREE.MeshStandardMaterial({
        color:       0x0a0c14,
        roughness:   0.8,
        metalness:   0.1,
        transparent: true,
        opacity:     0.6
      })
    );
    ground.rotation.x  = -Math.PI / 2;
    ground.position.y  = -0.02;
    ground.receiveShadow = true;
    scene.add(ground);
  }

  // ─── Resize Handler ──────────────────────────────────────────────────────
  function onWindowResize() {
    if (!container || !renderer || !camera) return;
    var width  = container.clientWidth;
    var height = container.clientHeight;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
  }

  // ─── Animation Loop ──────────────────────────────────────────────────────
  function animate() {
    animationId = requestAnimationFrame(animate);

    if (controls) {
      controls.autoRotate      = isAutoRotate;
      controls.autoRotateSpeed = 1.2;
      controls.update();
    }

    for (var i = 0; i < onRenderCallbacks.length; i++) {
      onRenderCallbacks[i]();
    }

    renderer.render(scene, camera);
  }

  // ─── Public API ──────────────────────────────────────────────────────────
  function addRenderCallback(cb) {
    onRenderCallbacks.push(cb);
  }

  function toggleAutoRotate(state) {
    isAutoRotate = (state !== undefined) ? state : !isAutoRotate;
    return isAutoRotate;
  }

  function toggleWireframe(state) {
    isWireframe = (state !== undefined) ? state : !isWireframe;
    scene.traverse(function(obj) {
      if (obj.isMesh && obj.material) {
        if (Array.isArray(obj.material)) {
          obj.material.forEach(function(m) { m.wireframe = isWireframe; });
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
    getScene:    function() { return scene;    },
    getCamera:   function() { return camera;   },
    getRenderer: function() { return renderer; },
    getControls: function() { return controls; },
    addRenderCallback,
    toggleAutoRotate,
    toggleWireframe,
    resetCamera
  };
})();
