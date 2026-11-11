/**
 * HumanNova 3D Atlas — Model Loader
 * Loads and processes segmented GLB anatomical models for male & female human bodies.
 */

window.AtlasModelLoader = (function() {
  let currentModelGroup = null;
  let currentGender = "male";
  let activeMeshes = [];
  let layerMap = {
    skin: [],
    muscles: [],
    veins: [],
    bones: [],
    organs: []
  };

  const MODEL_PATHS = {
    male: "models/male/male-atlas.glb",
    female: "models/female/female-atlas.glb"
  };

  function loadModel(gender, onProgress, onComplete, onError) {
    const scene = AtlasViewer.getScene();
    if (!scene) return;

    currentGender = gender;

    // 1. Dispose previous model
    if (currentModelGroup) {
      scene.remove(currentModelGroup);
      disposeHierarchy(currentModelGroup);
      currentModelGroup = null;
    }

    activeMeshes = [];
    layerMap = { skin: [], muscles: [], veins: [], bones: [], organs: [] };

    const loader = new THREE.GLTFLoader();
    const modelUrl = MODEL_PATHS[gender] || MODEL_PATHS.male;

    console.log(`[ModelLoader] Loading ${gender} anatomical model from: ${modelUrl}`);

    loader.load(
      modelUrl,
      (gltf) => {
        currentModelGroup = gltf.scene;
        processModelHierarchy(currentModelGroup);
        scene.add(currentModelGroup);

        console.log(`[ModelLoader] Loaded ${activeMeshes.length} anatomical meshes.`);
        if (onComplete) onComplete(currentModelGroup, layerMap);
      },
      (xhr) => {
        if (xhr.lengthComputable && onProgress) {
          const percent = Math.round((xhr.loaded / xhr.total) * 100);
          onProgress(percent);
        } else if (onProgress) {
          onProgress(75); // generic progress fallback
        }
      },
      (err) => {
        console.error(`[ModelLoader] Failed to load model: ${modelUrl}`, err);
        if (onError) onError(err);
      }
    );
  }

  function processModelHierarchy(root) {
    root.traverse((node) => {
      if (node.isMesh) {
        // Enable shadows
        node.castShadow = true;
        node.receiveShadow = true;

        // Save original position & rotation for exploded view
        node.userData.originalPosition = node.position.clone();
        node.userData.originalScale = node.scale.clone();
        node.userData.originalRotation = node.rotation.clone();

        // Categorize into layer
        const layer = determineLayer(node);
        node.userData.layer = layer;
        layerMap[layer].push(node);
        activeMeshes.push(node);

        // Ensure materials have depth test & proper blend
        if (node.material) {
          if (Array.isArray(node.material)) {
            node.material.forEach(m => setupMaterial(m, layer));
          } else {
            setupMaterial(node.material, layer);
          }
        }
      }
    });
  }

  function setupMaterial(mat, layer) {
    if (layer === "skin") {
      mat.transparent = true;
      mat.opacity = 0.22;
      mat.depthWrite = false;
    } else {
      mat.depthWrite = true;
    }
  }

  function determineLayer(mesh) {
    const name = (mesh.name || "").toLowerCase();
    const extras = mesh.userData && mesh.userData.extras;

    if (extras && extras.layer) {
      return extras.layer;
    }

    if (name.startsWith("skin_")) return "skin";
    if (name.startsWith("muscle_") || name.startsWith("tendon_") || name.includes("breast")) return "muscles";
    if (name.startsWith("vein_") || name.startsWith("artery_") || name.startsWith("vessel_")) return "veins";
    if (name.startsWith("bone_")) return "bones";
    if (name.startsWith("organ_") || name.startsWith("male_") || name.startsWith("female_")) return "organs";

    return "organs";
  }

  function disposeHierarchy(node) {
    node.traverse((child) => {
      if (child.isMesh) {
        if (child.geometry) child.geometry.dispose();
        if (child.material) {
          if (Array.isArray(child.material)) {
            child.material.forEach(m => m.dispose());
          } else {
            child.material.dispose();
          }
        }
      }
    });
  }

  return {
    loadModel,
    getCurrentGender: () => currentGender,
    getCurrentModelGroup: () => currentModelGroup,
    getActiveMeshes: () => activeMeshes,
    getLayerMap: () => layerMap
  };
})();
