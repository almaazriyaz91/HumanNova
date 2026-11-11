/**
 * HumanNova — Landing Page Interactive Engine
 * Handles 3D hero preview teaser, smooth navigation, and model triggers.
 */

document.addEventListener("DOMContentLoaded", () => {
  initHeroPreview();
  setupSmoothScrolling();
});

function initHeroPreview() {
  const container = document.getElementById("hero-canvas-container");
  if (!container || typeof THREE === "undefined") return;

  const width = container.clientWidth;
  const height = container.clientHeight;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 50);
  camera.position.set(0, 1.1, 2.5);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  container.appendChild(renderer.domElement);

  // Lighting
  const ambLight = new THREE.AmbientLight(0xffffff, 0.8);
  scene.add(ambLight);
  const dirLight = new THREE.DirectionalLight(0x38bdf8, 1.4);
  dirLight.position.set(2, 4, 3);
  scene.add(dirLight);

  let modelMesh = null;

  // Load Male Model as Teaser
  if (typeof THREE.GLTFLoader !== "undefined") {
    const loader = new THREE.GLTFLoader();
    loader.load(
      "models/male/male-atlas.glb",
      (gltf) => {
        modelMesh = gltf.scene;
        // Hide skin on preview to showcase ecorche muscles
        modelMesh.traverse(n => {
          if (n.isMesh && (n.name.startsWith("skin_") || n.userData.layer === "skin")) {
            n.visible = false;
          }
        });
        scene.add(modelMesh);
      },
      undefined,
      (err) => {
        console.warn("[HeroPreview] Teaser model preview error:", err);
      }
    );
  }

  // Animation Loop: Slow elegant rotation
  function animate() {
    requestAnimationFrame(animate);
    if (modelMesh) {
      modelMesh.rotation.y += 0.008;
    }
    renderer.render(scene, camera);
  }
  animate();

  window.addEventListener("resize", () => {
    if (!container || !renderer || !camera) return;
    const w = container.clientWidth;
    const h = container.clientHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  });
}

function setupSmoothScrolling() {
  const links = document.querySelectorAll('a[href^="#"]');
  links.forEach(link => {
    link.addEventListener("click", (e) => {
      const targetId = link.getAttribute("href");
      if (targetId === "#") return;
      const targetEl = document.querySelector(targetId);
      if (targetEl) {
        e.preventDefault();
        targetEl.scrollIntoView({ behavior: "smooth" });
      }
    });
  });
}
