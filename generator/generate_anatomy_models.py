"""
HumanNova 3D Anatomy Model Generator
Generates full male and female 3D anatomical models along with individual organ/muscle/bone/vein models.
Exports standard glTF 2.0 binary (.glb) files optimized for Three.js rendering.
"""

import os
import sys

# Ensure root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from generator.geometry_utils import save_glb_scene
from generator.anatomy_builder import (
    get_materials, build_organs, build_muscles,
    build_vessels, build_bones, build_skin
)

def generate_male_atlas(output_path):
    print("Building Male Anatomical Atlas...")
    materials = get_materials()
    meshes = []
    
    # Layer 1: Skeletal System (Bones)
    meshes.extend(build_bones("male"))
    # Layer 2: Circulatory System (Veins & Arteries)
    meshes.extend(build_vessels())
    # Layer 3: Visceral System (Internal Organs)
    meshes.extend(build_organs("male"))
    # Layer 4: Muscular System (Muscles & Tendons)
    meshes.extend(build_muscles("male"))
    # Layer 5: Integumentary System (Skin)
    meshes.extend(build_skin("male"))
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    save_glb_scene(meshes, materials, output_path)

def generate_female_atlas(output_path):
    print("Building Female Anatomical Atlas...")
    materials = get_materials()
    meshes = []
    
    # Layer 1: Skeletal System (Bones)
    meshes.extend(build_bones("female"))
    # Layer 2: Circulatory System (Veins & Arteries)
    meshes.extend(build_vessels())
    # Layer 3: Visceral System (Internal Organs + Uterus/Ovaries)
    meshes.extend(build_organs("female"))
    # Layer 4: Muscular System (Muscles, Breasts & Tendons)
    meshes.extend(build_muscles("female"))
    # Layer 5: Integumentary System (Skin)
    meshes.extend(build_skin("female"))
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    save_glb_scene(meshes, materials, output_path)

def generate_individual_models(base_dir):
    print("Generating Individual Anatomical 3D Models...")
    materials = get_materials()
    
    # 1. ORGANS
    organs_all = build_organs("female")
    
    # Heart
    heart_meshes = [m for m in organs_all if "heart" in m.name or "aorta" in m.name]
    save_glb_scene(heart_meshes, materials, os.path.join(base_dir, "organs", "heart.glb"))
    
    # Brain
    brain_meshes = [m for m in organs_all if "brain" in m.name or "cerebellum" in m.name]
    save_glb_scene(brain_meshes, materials, os.path.join(base_dir, "organs", "brain.glb"))
    
    # Lungs
    lung_meshes = [m for m in organs_all if "lung" in m.name or "trachea" in m.name]
    save_glb_scene(lung_meshes, materials, os.path.join(base_dir, "organs", "lungs.glb"))
    
    # Liver
    liver_meshes = [m for m in organs_all if "liver" in m.name]
    save_glb_scene(liver_meshes, materials, os.path.join(base_dir, "organs", "liver.glb"))
    
    # Stomach
    stomach_meshes = [m for m in organs_all if "stomach" in m.name]
    save_glb_scene(stomach_meshes, materials, os.path.join(base_dir, "organs", "stomach.glb"))
    
    # Kidneys
    kidney_meshes = [m for m in organs_all if "kidney" in m.name]
    save_glb_scene(kidney_meshes, materials, os.path.join(base_dir, "organs", "kidneys.glb"))
    
    # Female Reproductive
    repro_meshes = [m for m in organs_all if "uterus" in m.name or "fallopian" in m.name or "ovary" in m.name]
    save_glb_scene(repro_meshes, materials, os.path.join(base_dir, "organs", "female_reproductive.glb"))

    # 2. MUSCLES
    muscles_all = build_muscles("male")
    
    # Pectoralis Major
    pec_meshes = [m for m in muscles_all if "pectoralis" in m.name]
    save_glb_scene(pec_meshes, materials, os.path.join(base_dir, "muscles", "pectoralis_major.glb"))
    
    # Biceps Brachii
    bic_meshes = [m for m in muscles_all if "biceps_brachii" in m.name]
    save_glb_scene(bic_meshes, materials, os.path.join(base_dir, "muscles", "biceps_brachii.glb"))
    
    # Rectus Abdominis
    ab_meshes = [m for m in muscles_all if "rectus_abdominis" in m.name or "linea_alba" in m.name]
    save_glb_scene(ab_meshes, materials, os.path.join(base_dir, "muscles", "rectus_abdominis.glb"))
    
    # Quadriceps Femoris
    quad_meshes = [m for m in muscles_all if "rectus_femoris" in m.name or "vastus" in m.name or "patellar" in m.name]
    save_glb_scene(quad_meshes, materials, os.path.join(base_dir, "muscles", "quadriceps_femoris.glb"))

    # 3. VEINS & ARTERIES
    vessels_all = build_vessels()
    save_glb_scene(vessels_all, materials, os.path.join(base_dir, "veins", "cardiovascular_tree.glb"))

    # 4. BONES
    bones_all = build_bones("male")
    
    # Cranium (Skull)
    skull_meshes = [m for m in bones_all if "cranium" in m.name or "mandible" in m.name]
    save_glb_scene(skull_meshes, materials, os.path.join(base_dir, "bones", "cranium.glb"))
    
    # Ribcage & Spine
    thorax_meshes = [m for m in bones_all if "rib" in m.name or "sternum" in m.name or "vertebral" in m.name]
    save_glb_scene(thorax_meshes, materials, os.path.join(base_dir, "bones", "ribcage_spine.glb"))
    
    # Pelvis
    pelvis_meshes = [m for m in bones_all if "pelvis" in m.name]
    save_glb_scene(pelvis_meshes, materials, os.path.join(base_dir, "bones", "pelvis.glb"))

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    male_path = os.path.join(root_dir, 'frontend', 'models', 'male', 'male-atlas.glb')
    female_path = os.path.join(root_dir, 'frontend', 'models', 'female', 'female-atlas.glb')
    ind_dir = os.path.join(root_dir, 'frontend', 'models', 'individual')
    
    generate_male_atlas(male_path)
    generate_female_atlas(female_path)
    generate_individual_models(ind_dir)
    print("\nAll 3D Anatomical models successfully generated!")

if __name__ == '__main__':
    main()
