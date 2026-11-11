# HumanNova — System Architecture & Technical Specifications

## 1. High-Level Architecture Overview

HumanNova operates as a modern decoupled client-server application engineered for high-performance interactive 3D anatomy visualization and context-aware artificial intelligence.

```
                      +-----------------------------+
                      |            USER             |
                      +--------------+--------------+
                                     |
                                     v
                 +---------------------------------------+
                 |       HUMAN NOVA WEB FRONTEND         |
                 |       HTML5 + CSS3 + ES6 Modules      |
                 +-------------------+-------------------+
                                     |
           +-------------------------+-------------------------+
           |                         |                         |
           v                         v                         v
   +---------------+        +------------------+     +-------------------+
   |   Three.js    |        |   Anatomy UI &   |     |    OctSem AI      |
   |   3D Viewer   |        |   Layer Controls |     |  Chat Interface   |
   +-------+-------+        +--------+---------+     +---------+---------+
           |                         |                         |
           v                         v                         |
   +---------------+        +------------------+               |
   | GLB 3D Models |        |  Anatomy Data &  |               |
   | Male & Female |        | Structure Mapping|               |
   +---------------+        +--------+---------+               |
                                     |                         |
                                     +------------+------------+
                                                  |
                                             HTTP / JSON
                                                  |
                                                  v
                                      +-----------------------+
                                      |    FASTAPI BACKEND    |
                                      +-----------+-----------+
                                                  |
                               +------------------+------------------+
                               |                                     |
                               v                                     v
                    +--------------------+                +--------------------+
                    | Anatomy API Router |                |  AI Service Layer  |
                    | & Structure Data   |                +----------+---------+
                    +--------------------+                           |
                                                                     v
                                                          +--------------------+
                                                          |   OpenRouter API   |
                                                          |  (NVIDIA Nemotron) |
                                                          +--------------------+
```

## 2. Core Subsystems

### 2.1 3D Anatomical Visualization Engine (Three.js)
- **WebGL Rendering:** Configured with `ACESFilmicToneMapping`, `sRGBEncoding`, PCF soft shadow maps, and fog blending.
- **Cinematic Studio Lighting:**
  - Key Directional Light: Warm high-angle illumination with shadow casting.
  - Fill Directional Light: Cool cyan low-contrast ambient fill.
  - Rim Backlight: Electric blue silhouette contouring matching platform branding.
  - Ambient Light: Uniform diffuse visibility across deep cavity structures.
- **OrbitControls:** Smooth damping, zoom clamped between 0.4m and 6.0m, polar angle locked to prevent under-floor disorientation.
- **Raycasting Picker:** Detects mouse and pointer interactions on meshes, resolves mesh names to stable medical identifiers, and highlights selections with electric blue (`#38bdf8`) emissive shaders.

### 2.2 Anatomical Segmentation & Layers
The platform supports 5 independent interactive layers:
1. **Skin (Integumentary System):** Translucent body surface envelope (`opacity: 0.22`, `alphaMode: BLEND`).
2. **Muscles (Muscular System):** Ecorche crimson striated muscle bellies with glistening white pearl aponeuroses and tendons.
3. **Veins & Vessels (Cardiovascular System):** Oxygenated arterial network in arterial red and systemic venous conduits in venous blue.
4. **Bones (Skeletal System):** Neurocranium, mandible, vertebral column, ribcage, sternum, pelvis, and appendicular skeleton in natural bone ivory.
5. **Organs (Visceral System):** Brain, heart, lungs, liver, stomach, spleen, kidneys, pancreas, intestines, and reproductive systems (male & female specific).

### 2.3 Exploded View Engine
- Every anatomical mesh object contains an assigned radial displacement vector (`extras.exploded_offset`).
- The Exploded View module executes smooth quadratic easing between natural anatomical positions and exploded spatial configurations in the animation loop.

### 2.4 OctSem AI Assistant
- Context-aware prompting: When a structure is selected on the 3D stage, its identifier, common name, system, anatomical landmarks, and reviewed clinical significance are injected directly into the LLM context prompt.
- Dual-Mode Resiliency:
  - **Live Mode:** Dispatches prompts to OpenRouter API (configured for `nvidia/nemotron-3.5-super-vl:free` or specified model) using secure server-side tokens.
  - **Educational Knowledge Fallback Mode:** When an API key is not entered (or if upstream rate limits occur), the engine constructs structured, reviewed medical explanations from the internal knowledge base.

### 2.5 FastAPI Backend
- RESTful routing with Pydantic request validation and CORS middleware.
- Modular architecture:
  - `routes/anatomy.py`: Health checks, search, and metadata querying.
  - `routes/chat.py`: Contextual chat endpoint with session tokens.
  - `routes/quiz.py`: MCQ question bank and grading engine.
