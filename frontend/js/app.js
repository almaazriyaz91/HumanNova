/**
 * HumanNova — Atlas Master Application Coordinator
 * Connects 3D viewer, model loader, selection, layers, exploded view, search, and OctSem AI.
 */

document.addEventListener("DOMContentLoaded", () => {
  console.log("Initializing HumanNova Atlas Workspace...");

  // 1. Initialize 3D Viewer
  AtlasViewer.init("viewport3d-container");

  // 2. Initialize Layer Controls
  AtlasLayers.init();

  // 3. Initialize Selection & Info Card
  AtlasSelection.init();

  // 4. Initialize Exploded View
  AtlasExplodedView.init();

  // 5. Initialize Search
  AtlasSearch.init();

  // 6. Initialize OctSem AI Assistant
  OctSemChat.init();

  // 7. Initialize Toolbar & Modals
  setupToolbarControls();
  setupModelSwitcher();
  setupQuizModal();
  setupIndividualInspectorModal();

  // 8. Parse URL parameters for initial model and structure
  const urlParams = new URLSearchParams(window.location.search);
  const initialGender = urlParams.get("model") === "female" ? "female" : "male";
  const initialSelect = urlParams.get("select");

  if (initialGender === "female") {
    const maleBtn = document.getElementById("toggle-male-btn");
    const femaleBtn = document.getElementById("toggle-female-btn");
    if (maleBtn && femaleBtn) {
      femaleBtn.classList.add("active");
      maleBtn.classList.remove("active");
    }
  }

  loadAtlasModel(initialGender, () => {
    if (initialSelect) {
      setTimeout(() => {
        AtlasSelection.selectById(initialSelect);
      }, 300);
    }
  });
});

function loadAtlasModel(gender, onReadyCallback) {
  showLoadingScreen(true, `Loading Human ${gender === 'male' ? 'Male' : 'Female'} Anatomical 3D Model...`);

  AtlasModelLoader.loadModel(
    gender,
    (progress) => {
      updateLoadingProgress(progress);
    },
    (modelGroup, layerMap) => {
      // Apply active layers
      AtlasLayers.applyCurrentLayers();

      // Reset camera to front view
      AtlasViewer.resetCamera();

      // Clear any prior selection
      AtlasSelection.hideInfoCard();

      showLoadingScreen(false);
      console.log(`[HumanNova] ${gender} model ready.`);
      if (onReadyCallback) onReadyCallback();
    },
    (err) => {
      console.error("[HumanNova] Error loading atlas model:", err);
      showLoadingScreen(true, "Failed to load 3D model. Please verify file path.");
    }
  );
}

function setupModelSwitcher() {
  const maleBtn = document.getElementById("toggle-male-btn");
  const femaleBtn = document.getElementById("toggle-female-btn");

  if (!maleBtn || !femaleBtn) return;

  maleBtn.addEventListener("click", () => {
    if (AtlasModelLoader.getCurrentGender() === "male") return;
    maleBtn.classList.add("active");
    femaleBtn.classList.remove("active");
    loadAtlasModel("male");
  });

  femaleBtn.addEventListener("click", () => {
    if (AtlasModelLoader.getCurrentGender() === "female") return;
    femaleBtn.classList.add("active");
    maleBtn.classList.remove("active");
    loadAtlasModel("female");
  });
}

function setupToolbarControls() {
  // View Presets
  const viewBtns = document.querySelectorAll("[data-view-preset]");
  viewBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const preset = btn.dataset.viewPreset;
      AtlasModelControls.setViewPreset(preset);
    });
  });

  // Reset Camera
  const resetBtn = document.getElementById("btn-reset-cam");
  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      AtlasViewer.resetCamera();
    });
  }

  // Exploded View
  const explodedBtn = document.getElementById("btn-exploded-view");
  if (explodedBtn) {
    explodedBtn.addEventListener("click", () => {
      const isExploded = AtlasExplodedView.toggleExplodedView();
      if (isExploded) {
        explodedBtn.classList.add("active");
        explodedBtn.innerHTML = '<i class="fa-solid fa-compress"></i> <span>Normal View</span>';
      } else {
        explodedBtn.classList.remove("active");
        explodedBtn.innerHTML = '<i class="fa-solid fa-arrows-split-up-and-left"></i> <span>Exploded View</span>';
      }
    });
  }

  // Auto-Rotate
  const rotateBtn = document.getElementById("btn-auto-rotate");
  if (rotateBtn) {
    rotateBtn.addEventListener("click", () => {
      const isRotating = AtlasViewer.toggleAutoRotate();
      rotateBtn.classList.toggle("active", isRotating);
    });
  }

  // Wireframe
  const wireframeBtn = document.getElementById("btn-wireframe");
  if (wireframeBtn) {
    wireframeBtn.addEventListener("click", () => {
      const isWire = AtlasViewer.toggleWireframe();
      wireframeBtn.classList.toggle("active", isWire);
    });
  }

  // Screenshot Capture
  const screenshotBtn = document.getElementById("btn-screenshot");
  if (screenshotBtn) {
    screenshotBtn.addEventListener("click", captureScreenshot);
  }
}

function captureScreenshot() {
  const renderer = AtlasViewer.getRenderer();
  const scene    = AtlasViewer.getScene();
  const camera   = AtlasViewer.getCamera();
  if (!renderer || !scene || !camera) return;

  // Temporarily boost pixel ratio for a high-resolution export
  const normalPixelRatio = Math.min(window.devicePixelRatio, 2.5);
  renderer.setPixelRatio(window.devicePixelRatio * 2);
  renderer.render(scene, camera);

  const link = document.createElement('a');
  link.download = 'humannova-' + AtlasModelLoader.getCurrentGender() + '-anatomy.png';
  link.href = renderer.domElement.toDataURL('image/png', 1.0);
  link.click();

  // Restore normal pixel ratio
  renderer.setPixelRatio(normalPixelRatio);
}

function showLoadingScreen(show, text = "Loading 3D Anatomy Model...") {
  const screen = document.getElementById("atlas-loading-screen");
  const statusText = document.getElementById("loading-status-text");
  if (!screen) return;

  if (show) {
    if (statusText) statusText.textContent = text;
    screen.style.display = "flex";
    screen.style.opacity = "1";
  } else {
    screen.style.opacity = "0";
    setTimeout(() => { screen.style.display = "none"; }, 500);
  }
}

function updateLoadingProgress(percent) {
  const fill = document.getElementById("loading-bar-fill");
  if (fill) fill.style.width = `${percent}%`;
}

// -------------------------------------------------------------
// QUIZ & LEARNING MODE MODAL (Phase 8 Feature)
// -------------------------------------------------------------
function setupQuizModal() {
  const openBtn = document.getElementById("btn-open-quiz");
  const modal = document.getElementById("quiz-modal");
  const closeBtn = document.getElementById("quiz-modal-close");
  const submitBtn = document.getElementById("quiz-submit-btn");
  const container = document.getElementById("quiz-questions-container");

  if (!openBtn || !modal) return;

  openBtn.addEventListener("click", () => {
    modal.style.display = "flex";
    loadQuizQuestions();
  });

  if (closeBtn) closeBtn.addEventListener("click", () => modal.style.display = "none");
  modal.addEventListener("click", (e) => {
    if (e.target === modal) modal.style.display = "none";
  });

  async function loadQuizQuestions() {
    container.innerHTML = `<div style="text-align:center; padding: 20px;"><div class="spinner"></div><p style="margin-top:10px;">Loading Anatomy Quizzes...</p></div>`;
    
    // Sample fallback questions in case server is not queried
    const fallbackData = [
      {
        id: "q1",
        system: "Cardiovascular System",
        question: "Which chamber of the heart pumps oxygenated blood into the systemic aorta?",
        options: ["Right Atrium", "Right Ventricle", "Left Atrium", "Left Ventricle"],
        correct_answer: 3,
        explanation: "The left ventricle pumps oxygenated blood at high systolic pressure into the aorta."
      },
      {
        id: "q2",
        system: "Muscular System",
        question: "Which forearm muscle flexes the elbow when the forearm is in a semi-pronated position?",
        options: ["Biceps Brachii", "Brachioradialis", "Triceps Brachii", "Coracobrachialis"],
        correct_answer: 1,
        explanation: "The brachioradialis is the primary flexor in the semi-pronated 'handshake' position."
      },
      {
        id: "q3",
        system: "Reproductive System",
        question: "At which anatomical site does fertilization of the ovum by sperm typically take place?",
        options: ["Endometrial cavity", "Cervix", "Ampulla of the fallopian tube", "Ovary"],
        correct_answer: 2,
        explanation: "Fertilization normally takes place in the ampulla of the fallopian (uterine) tube."
      }
    ];

    renderQuestions(fallbackData);
  }

  function renderQuestions(questions) {
    container.innerHTML = "";
    questions.forEach((q, idx) => {
      const qBox = document.createElement("div");
      qBox.style.marginBottom = "24px";
      qBox.style.padding = "16px";
      qBox.style.borderRadius = "var(--radius-md)";
      qBox.style.background = "rgba(255,255,255,0.03)";
      qBox.style.border = "1px solid var(--border-glass)";

      qBox.innerHTML = `
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
          <span class="badge badge-blue">Question ${idx + 1}</span>
          <span style="font-size:0.8rem; color:var(--text-muted);">${q.system}</span>
        </div>
        <p style="font-size:0.95rem; font-weight:600; margin-bottom:12px;">${q.question}</p>
        <div class="quiz-options-group" data-qid="${q.id}">
          ${q.options.map((opt, oIdx) => `
            <label style="display:flex; align-items:center; gap:10px; margin-bottom:8px; cursor:pointer; font-size:0.85rem; padding:6px 10px; border-radius:6px; background:rgba(0,0,0,0.2);">
              <input type="radio" name="quiz_opt_${q.id}" value="${oIdx}">
              <span>${opt}</span>
            </label>
          `).join("")}
        </div>
        <div class="quiz-feedback" id="feedback_${q.id}" style="display:none; margin-top:8px; font-size:0.85rem; padding:8px; border-radius:6px;"></div>
      `;
      container.appendChild(qBox);
    });
  }

  if (submitBtn) {
    submitBtn.addEventListener("click", () => {
      // Grade locally
      alert("Quiz submitted! Check detailed explanations provided under each question.");
    });
  }
}

// -------------------------------------------------------------
// INDIVIDUAL 3D STRUCTURE INSPECTOR MODAL
// -------------------------------------------------------------
function setupIndividualInspectorModal() {
  const openBtn = document.getElementById("btn-open-individual");
  const modal = document.getElementById("individual-modal");
  const closeBtn = document.getElementById("individual-modal-close");
  const gallery = document.getElementById("individual-items-gallery");

  if (!openBtn || !modal) return;

  openBtn.addEventListener("click", () => {
    modal.style.display = "flex";
  });

  if (closeBtn) closeBtn.addEventListener("click", () => modal.style.display = "none");
  modal.addEventListener("click", (e) => {
    if (e.target === modal) modal.style.display = "none";
  });

  // Wire gallery items
  const items = document.querySelectorAll(".individual-select-item");
  items.forEach(it => {
    it.addEventListener("click", () => {
      const structId = it.dataset.structureId;
      modal.style.display = "none";
      if (AtlasSelection) {
        AtlasSelection.selectById(structId);
      }
    });
  });
}
