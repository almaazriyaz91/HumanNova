# HumanNova — Student & Evaluator User Guide

Welcome to **HumanNova**, an interactive 3D anatomy learning platform built to help medical students, nursing learners, and health science scholars master human anatomy with the guidance of OctSem AI.

---

## 1. Getting Started

### 1.1 Launching the Application
You can run HumanNova in two ways:

#### Option A: FastAPI Full-Stack Server (Recommended)
1. Navigate to the project root in your terminal:
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```
2. Open your browser and navigate to:
   - **Home / Landing Page:** `http://localhost:8000/`
   - **Interactive 3D Atlas Workspace:** `http://localhost:8000/atlas`
   - **API Documentation (Swagger UI):** `http://localhost:8000/docs`

#### Option B: Static Web Server
Serve the `frontend/` directory using any local static web server (such as Python's `http.server`, VS Code Live Server, or Nginx):
```bash
python -m http.server 5500 --directory frontend
```
Then visit `http://localhost:5500/`.

---

## 2. Navigating the 3D Atlas Workspace

### 2.1 3D Orbit & Camera Controls
- **Rotate:** Click and drag with the left mouse button (or single-finger drag on touch screens).
- **Zoom:** Scroll the mouse wheel up or down (or pinch-to-zoom on touch screens).
- **Pan:** Click and drag with the right mouse button (or two-finger drag).
- **Anatomical Presets:** Use the floating toolbar at the bottom of the screen to snap directly to:
  - **Front** (Anterior view)
  - **Back** (Posterior view)
  - **Left / Right** (Lateral views)
  - **Top** (Superior view)
- **Reset Camera:** Click the circular arrows button in the header or toolbar.

### 2.2 Male & Female Model Switcher
Located in the top header bar:
- Click **Male** to load the complete male anatomical atlas.
- Click **Female** to load the female anatomical atlas (including the uterus, fallopian tubes, and ovaries).

### 2.3 Layer Visibility Controls
Located in the floating panel on the left:
- **Skin:** Toggle the outer translucent surface envelope.
- **Muscles:** Show or hide striated skeletal muscles and tendons.
- **Vessels:** Show or hide the cardiovascular vascular network (Aorta, Vena Cava, Carotids, Femoral vessels).
- **Bones:** Show or hide the skeletal system (Cranium, Spine, Ribcage, Pelvis, Limbs).
- **Organs:** Show or hide the internal visceral organs (Brain, Heart, Lungs, Liver, Stomach, Kidneys, Intestines, Bladder).

### 2.4 Structure Selection & Inspection
1. Click on any visible organ, muscle, or bone in the 3D viewport.
2. The clicked structure will immediately highlight with an **electric blue emissive glow**.
3. The **Anatomy Information Card** will open on the left, displaying:
   - Common anatomical and Latin name
   - System classification
   - Concise reviewed educational description
   - Anatomical location & relations
   - Physiological function
   - Clinical relevance and pathology
4. **Isolate in 3D:** Click the "Isolate in 3D" button on the card to hide everything else and focus exclusively on this structure.

### 2.5 Exploded View Mode
Click the **Exploded View** button in the bottom toolbar:
- The anatomical layers will smoothly move outward along radial displacement vectors.
- This allows you to inspect deep structures (such as internal organs and vessels) without surface occlusion.
- Click **Normal View** to smoothly return the model to its standard anatomical position.

---

## 3. Learning with OctSem AI

The **OctSem AI Learning Assistant** is located in the right sidebar.

1. **Context-Aware Assistance:** When you select any structure in the 3D viewport, its name, layer, and system automatically populate the AI context banner.
2. **Asking Questions:**
   - Type any question into the input field (e.g., *"Explain the blood supply of this organ"*, *"What are the four chambers?"*, *"Give me a medical mnemonic for this"*).
   - Or click any of the suggested prompt pills (Function, Pathologies, Innervation, Mnemonic).
3. **Session-Only History:** Conversations are maintained during your active browser session.

### Adding Your Live OpenRouter API Key
Per instructions, API keys are left blank by default. The system includes a built-in educational knowledge engine that answers immediately.
To connect your live OpenRouter AI account:
1. Open the `.env` file in the project root.
2. Add your OpenRouter API key:
   ```env
   OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
   OPENROUTER_MODEL=nvidia/nemotron-3.5-super-vl:free
   ```
3. Restart the FastAPI server. OctSem AI will now stream responses directly from your configured AI model!

---

## 4. Quizzes & Practice (Phase 8 Feature)
Click **Quiz & Practice** in the top header:
- Take multiple-choice anatomy quizzes categorized by system.
- Select your answers and submit to receive score calculation and detailed medical explanations.

---

## 5. Individual 3D Library
Click **3D Library** in the header to browse and isolate individual high-detail models of organs (Heart, Brain, Lungs, Liver, Uterus), muscles (Pectoralis, Biceps, Rectus Abdominis), and bones (Cranium, Pelvis).
