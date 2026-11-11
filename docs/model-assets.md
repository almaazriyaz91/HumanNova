# HumanNova — 3D Anatomical Model Assets Documentation

## 1. Asset Generation Methodology

All 3D anatomical models in HumanNova were procedurally created using custom Python algorithms and Blender integration scripts designed specifically for medical education.

### 1.1 Generation Scripts
- `generator/generate_anatomy_models.py`: Python engine utilizing `numpy` and binary glTF 2.0 specifications to construct multi-mesh anatomical hierarchies and compile compliant `.glb` files.
- `generator/anatomy_builder.py`: Anatomical geometry builder generating muscles, organs, vessels, skeleton, and gender-specific reproductive systems.
- `generator/geometry_utils.py`: High-performance procedural mesh generators (swept tubes, ellipsoids, lofts, normal calculations, binary packing).
- `generator/blender_anatomy_generator.py`: Native Blender script utilizing the `bpy` module for running or modifying models directly inside Blender.

## 2. Generated 3D Asset Manifest

### 2.1 Complete Anatomical Atlases
| Model File | Layer Contents | Segmented Meshes | File Size | Description |
| :--- | :--- | :---: | :---: | :--- |
| `frontend/models/male/male-atlas.glb` | Muscles, Organs, Veins, Bones, Skin, Male Genitalia | 111 | ~665 KB | Full male anatomical figure modeled in anatomical position. |
| `frontend/models/female/female-atlas.glb` | Muscles, Organs, Veins, Bones, Skin, Breasts, Uterus/Ovaries | 115 | ~697 KB | Full female anatomical figure featuring female reproductive system. |

### 2.2 Individual 3D Anatomical Models (`frontend/models/individual/`)
- **Organs:**
  - `organs/heart.glb`: Cardiac muscle, atria, ventricles, aortic arch
  - `organs/brain.glb`: Left/right cerebral hemispheres, cerebellum, brainstem
  - `organs/lungs.glb`: Left lung (2 lobes), right lung (3 lobes), trachea
  - `organs/liver.glb`: Hepatic lobes and parenchymal wedge
  - `organs/stomach.glb`: J-shaped gastric organ
  - `organs/kidneys.glb`: Renal cortex, pelvis, adrenal caps
  - `organs/female_reproductive.glb`: Uterus, fallopian tubes, bilateral ovaries
- **Muscles:**
  - `muscles/pectoralis_major.glb`: Clavicular and sternocostal heads
  - `muscles/biceps_brachii.glb`: Biceps bellies with tendons
  - `muscles/rectus_abdominis.glb`: 8 distinct muscle segments and linea alba
  - `muscles/quadriceps_femoris.glb`: Rectus femoris, vastus lateralis, vastus medialis, patellar tendon
- **Veins & Arteries:**
  - `veins/cardiovascular_tree.glb`: Aorta, vena cava, carotids, jugulars, femoral vessels
- **Skeletal Bones:**
  - `bones/cranium.glb`: Neurocranium dome and mandible
  - `bones/ribcage_spine.glb`: Vertebral column, sternum, thoracic ribs
  - `bones/pelvis.glb`: Pelvic girdle, iliac crests, sacrum

## 3. PBR Material & Color Palette

All assets use glTF 2.0 PBR Metallic-Roughness materials calibrated for anatomical accuracy:
- **Muscle Crimson:** `baseColorFactor: [0.68, 0.17, 0.14, 1.0]`, `metallic: 0.08`, `roughness: 0.55`
- **Tendon Pearl:** `baseColorFactor: [0.94, 0.92, 0.88, 1.0]`, `metallic: 0.15`, `roughness: 0.35`
- **Bone Ivory:** `baseColorFactor: [0.91, 0.88, 0.80, 1.0]`, `metallic: 0.05`, `roughness: 0.65`
- **Arterial Red:** `baseColorFactor: [0.85, 0.12, 0.12, 1.0]`, `metallic: 0.10`, `roughness: 0.35`
- **Venous Blue:** `baseColorFactor: [0.12, 0.45, 0.88, 1.0]`, `metallic: 0.10`, `roughness: 0.35`
- **Female Reproductive Rose:** `baseColorFactor: [0.96, 0.48, 0.62, 1.0]`, `metallic: 0.10`, `roughness: 0.40`
- **Skin Translucent:** `baseColorFactor: [0.92, 0.78, 0.70, 0.22]`, `alphaMode: BLEND`, `doubleSided: true`

## 4. Licensing & Attribution
- All generated meshes and procedural scripts are released under the project repository license for hackathon evaluation and educational non-commercial study.
