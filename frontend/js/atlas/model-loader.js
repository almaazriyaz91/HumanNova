/**
 * HumanNova 3D Atlas — Model Loader (Ultra-Realistic PBR Upgrade)
 * Loads segmented GLB anatomical models and replaces all materials with
 * MeshPhysicalMaterial tuned per anatomical layer for maximum realism.
 *
 * Layer material strategy (Three.js r134):
 *   skin    — translucent, DoubleSide, no depthWrite
 *   muscles — sheen for sub-surface scatter simulation
 *   veins   — clearcoat for wet vessel surfaces
 *   bones   — slightly rough ivory
 *   organs  — clearcoat for serous membrane sheen
 */

window.AtlasModelLoader = (function() {
  var currentModelGroup = null;
  var currentGender     = 'male';
  var activeMeshes      = [];
  var layerMap = {
    skin:    [],
    muscles: [],
    veins:   [],
    bones:   [],
    organs:  []
  };

  var MODEL_PATHS = {
    male:   'models/male/male-atlas.glb',
    female: 'models/female/female-atlas.glb'
  };

  // ─── Public: loadModel ───────────────────────────────────────────────────
  function loadModel(gender, onProgress, onComplete, onError) {
    var scene = AtlasViewer.getScene();
    if (!scene) return;

    currentGender = gender;

    // Dispose previous model
    if (currentModelGroup) {
      scene.remove(currentModelGroup);
      disposeHierarchy(currentModelGroup);
      currentModelGroup = null;
    }

    activeMeshes = [];
    layerMap = { skin: [], muscles: [], veins: [], bones: [], organs: [] };

    var loader   = new THREE.GLTFLoader();
    var modelUrl = MODEL_PATHS[gender] || MODEL_PATHS.male;

    console.log('[ModelLoader] Loading ' + gender + ' model from: ' + modelUrl);

    loader.load(
      modelUrl,
      function(gltf) {
        currentModelGroup = gltf.scene;
        processModelHierarchy(currentModelGroup);
        scene.add(currentModelGroup);
        console.log('[ModelLoader] Loaded ' + activeMeshes.length + ' anatomical meshes.');
        if (onComplete) onComplete(currentModelGroup, layerMap);
      },
      function(xhr) {
        if (xhr.lengthComputable && onProgress) {
          onProgress(Math.round((xhr.loaded / xhr.total) * 100));
        } else if (onProgress) {
          onProgress(75); // generic fallback
        }
      },
      function(err) {
        console.error('[ModelLoader] Failed to load model: ' + modelUrl, err);
        if (onError) onError(err);
      }
    );
  }

  // ─── Traverse & process loaded scene ────────────────────────────────────
  function processModelHierarchy(root) {
    root.traverse(function(node) {
      if (!node.isMesh) return;

      node.castShadow    = true;
      node.receiveShadow = true;

      // Save original transform for exploded view
      node.userData.originalPosition = node.position.clone();
      node.userData.originalScale    = node.scale.clone();
      node.userData.originalRotation = node.rotation.clone();

      // Categorize into layer
      var layer         = determineLayer(node);
      node.userData.layer = layer;
      layerMap[layer].push(node);
      activeMeshes.push(node);

      // Replace material(s) with enhanced MeshPhysicalMaterial
      if (node.material) {
        if (Array.isArray(node.material)) {
          node.material = node.material.map(function(m) {
            return enhanceMaterialRealism(m, layer, node.name);
          });
        } else {
          node.material = enhanceMaterialRealism(node.material, layer, node.name);
        }
      }
    });
  }

  // ─── Core: MeshPhysicalMaterial factory ─────────────────────────────────
  /**
   * Creates a new MeshPhysicalMaterial from an existing material, adding
   * layer-specific PBR properties for anatomical realism.
   *
   * NOTE on Three.js r134 sheen API:
   *   - `sheen` is a Number (0–1 intensity scalar, added in r128)
   *   - `sheenColor` is a THREE.Color  (added in r134)
   *   - `sheenRoughness` is a Number   (added in r134)
   */
  function enhanceMaterialRealism(mat, layer, meshName) {
    var enhanced = new THREE.MeshPhysicalMaterial();

    // ── Copy base properties from source material ──
    if (mat.color)      enhanced.color.copy(mat.color);
    if (mat.map)        enhanced.map        = mat.map;
    if (mat.normalMap)  enhanced.normalMap  = mat.normalMap;
    if (mat.roughnessMap)  enhanced.roughnessMap  = mat.roughnessMap;
    if (mat.metalnessMap)  enhanced.metalnessMap  = mat.metalnessMap;
    if (mat.aoMap)      enhanced.aoMap      = mat.aoMap;
    if (mat.emissive)   enhanced.emissive.copy(mat.emissive);
    if (mat.emissiveMap)   enhanced.emissiveMap   = mat.emissiveMap;

    // Always biological — no metalness
    enhanced.metalness = 0.0;
    enhanced.roughness = mat.roughness != null ? mat.roughness : 0.7;

    // Env map intensity for environment reflections
    enhanced.envMapIntensity = 1.0;

    // ── Layer-specific overrides ──
    if (layer === 'organs') {
      // Wet serous membrane — clearcoat simulates peritoneal/pleural sheen
      enhanced.roughness          = 0.4;
      enhanced.clearcoat          = 0.35;
      enhanced.clearcoatRoughness = 0.15;
      enhanced.envMapIntensity    = 1.2;

    } else if (layer === 'muscles') {
      // Striated muscle — sheen simulates sub-surface scatter through fasciae
      enhanced.roughness      = 0.72;
      enhanced.sheen          = 0.2;              // intensity scalar (r128+)
      enhanced.sheenColor     = new THREE.Color(0x8b1515);  // deep red
      enhanced.sheenRoughness = 0.8;

    } else if (layer === 'veins') {
      // Vascular walls — higher clearcoat than organs, slight translucency
      enhanced.roughness          = 0.35;
      enhanced.clearcoat          = 0.5;
      enhanced.clearcoatRoughness = 0.1;
      enhanced.envMapIntensity    = 1.4;

    } else if (layer === 'bones') {
      // Cortical bone — slightly rough ivory
      enhanced.roughness = 0.65;

    } else if (layer === 'skin') {
      // Epidermis — translucent silhouette, double-sided for inner glow
      enhanced.roughness   = 0.5;
      enhanced.transparent = true;
      enhanced.opacity     = 0.18;
      enhanced.side        = THREE.DoubleSide;
      enhanced.depthWrite  = false;
    }

    // Dispose old material to free GPU memory
    if (mat !== enhanced && typeof mat.dispose === 'function') {
      mat.dispose();
    }

    return enhanced;
  }

  // ─── Layer detection ─────────────────────────────────────────────────────
  function determineLayer(mesh) {
    var name   = (mesh.name || '').toLowerCase();
    var extras = mesh.userData && mesh.userData.extras;

    if (extras && extras.layer) return extras.layer;

    if (name.startsWith('skin_'))   return 'skin';
    if (name.startsWith('muscle_') || name.startsWith('tendon_') || name.includes('breast')) return 'muscles';
    if (name.startsWith('vein_')   || name.startsWith('artery_') || name.startsWith('vessel_')) return 'veins';
    if (name.startsWith('bone_'))   return 'bones';
    if (name.startsWith('organ_')  || name.startsWith('male_')   || name.startsWith('female_')) return 'organs';

    return 'organs'; // default
  }

  // ─── Disposal ────────────────────────────────────────────────────────────
  function disposeHierarchy(node) {
    node.traverse(function(child) {
      if (!child.isMesh) return;
      if (child.geometry) child.geometry.dispose();
      if (child.material) {
        if (Array.isArray(child.material)) {
          child.material.forEach(function(m) { m.dispose(); });
        } else {
          child.material.dispose();
        }
      }
    });
  }

  // ─── Public API ──────────────────────────────────────────────────────────
  return {
    loadModel,
    getCurrentGender:      function() { return currentGender;      },
    getCurrentModelGroup:  function() { return currentModelGroup;  },
    getActiveMeshes:       function() { return activeMeshes;       },
    getLayerMap:           function() { return layerMap;           }
  };
})();
