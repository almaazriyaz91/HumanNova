"""
HumanNova Anatomy Builder
Creates complete, medically structured 3D anatomical models with segmented layers:
- Muscles (Ecorche style with muscle bellies and white tendons, matching reference images)
- Internal Organs (Brain, Heart, Lungs, Liver, Stomach, Kidneys, Intestines, Bladder, etc.)
- Veins & Arteries (Cardiovascular system with Aorta, Vena Cava, Jugular, Femoral, etc.)
- Skeletal Bones (Cranium, Spine, Ribcage, Pelvis, Limbs)
- Male / Female specific reproductive structures and morphological variations
- Skin / Integumentary envelope with translucency
"""

import numpy as np
from generator.geometry_utils import (
    MeshData, compute_smooth_normals, create_ellipsoid,
    create_cylinder, create_tube, create_muscle_belly
)

# Standard Anatomical Color Palette
MAT_MUSCLE_RED = 0        # Deep crimson muscle fiber #a02820
MAT_TENDON_WHITE = 1      # Gleaming white/cream tendon #f0ebe1
MAT_BONE_IVORY = 2        # Natural bone ivory #e5dfcb
MAT_ARTERY_RED = 3        # Oxygenated arterial red #d63031
MAT_VEIN_BLUE = 4         # Deoxygenated venous blue #0984e3
MAT_ORGAN_HEART = 5       # Cardiac tissue #b71540
MAT_ORGAN_LUNG = 6        # Pulmonary tissue #e17055
MAT_ORGAN_LIVER = 7       # Hepatic brown/ruby #6d214f
MAT_ORGAN_BRAIN = 8       # Cerebral cortex soft pink #f8a5c2
MAT_ORGAN_STOMACH = 9     # Gastric coral #e66767
MAT_ORGAN_KIDNEY = 10     # Renal deep crimson #78281f
MAT_ORGAN_INTESTINE = 11  # Enteric ochre/pink #ea8685
MAT_REPRODUCTIVE_F = 12   # Uterine/ovarian rose #fd79a8
MAT_REPRODUCTIVE_M = 13   # Male reproductive tone #cf6a87
MAT_SKIN_TRANSLUCENT = 14 # Epidermal translucent #f3d1b5

def get_materials():
    return [
        {
            "name": "Anatomy_Muscle_Crimson",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.68, 0.17, 0.14, 1.0],
                "metallicFactor": 0.08,
                "roughnessFactor": 0.55
            }
        },
        {
            "name": "Anatomy_Tendon_Pearl",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.94, 0.92, 0.88, 1.0],
                "metallicFactor": 0.15,
                "roughnessFactor": 0.35
            }
        },
        {
            "name": "Anatomy_Bone_Ivory",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.91, 0.88, 0.80, 1.0],
                "metallicFactor": 0.05,
                "roughnessFactor": 0.65
            }
        },
        {
            "name": "Anatomy_Artery_Red",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.85, 0.12, 0.12, 1.0],
                "metallicFactor": 0.1,
                "roughnessFactor": 0.35
            }
        },
        {
            "name": "Anatomy_Vein_Blue",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.12, 0.45, 0.88, 1.0],
                "metallicFactor": 0.1,
                "roughnessFactor": 0.35
            }
        },
        {
            "name": "Anatomy_Organ_Heart",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.72, 0.08, 0.18, 1.0],
                "metallicFactor": 0.1,
                "roughnessFactor": 0.4
            }
        },
        {
            "name": "Anatomy_Organ_Lung",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.88, 0.45, 0.42, 1.0],
                "metallicFactor": 0.05,
                "roughnessFactor": 0.6
            }
        },
        {
            "name": "Anatomy_Organ_Liver",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.46, 0.14, 0.18, 1.0],
                "metallicFactor": 0.1,
                "roughnessFactor": 0.45
            }
        },
        {
            "name": "Anatomy_Organ_Brain",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.92, 0.68, 0.72, 1.0],
                "metallicFactor": 0.05,
                "roughnessFactor": 0.55
            }
        },
        {
            "name": "Anatomy_Organ_Stomach",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.86, 0.38, 0.40, 1.0],
                "metallicFactor": 0.08,
                "roughnessFactor": 0.5
            }
        },
        {
            "name": "Anatomy_Organ_Kidney",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.52, 0.15, 0.12, 1.0],
                "metallicFactor": 0.1,
                "roughnessFactor": 0.45
            }
        },
        {
            "name": "Anatomy_Organ_Intestine",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.88, 0.54, 0.48, 1.0],
                "metallicFactor": 0.08,
                "roughnessFactor": 0.55
            }
        },
        {
            "name": "Anatomy_Reproductive_Female",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.96, 0.48, 0.62, 1.0],
                "metallicFactor": 0.1,
                "roughnessFactor": 0.4
            }
        },
        {
            "name": "Anatomy_Reproductive_Male",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.82, 0.42, 0.45, 1.0],
                "metallicFactor": 0.08,
                "roughnessFactor": 0.5
            }
        },
        {
            "name": "Anatomy_Skin_Translucent",
            "alphaMode": "BLEND",
            "doubleSided": True,
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.92, 0.78, 0.70, 0.22],
                "metallicFactor": 0.05,
                "roughnessFactor": 0.4
            }
        }
    ]

# -------------------------------------------------------------
# INTERNAL ORGANS BUILDER
# -------------------------------------------------------------
def build_organs(gender="male"):
    meshes = []
    
    # 1. BRAIN (Cerebrum Left & Right, Cerebellum, Brainstem)
    pos_bl, norm_bl, ind_bl = create_ellipsoid(0.045, 0.055, 0.065, n_lat=16, n_lon=20, offset=(-0.024, 1.66, 0.01))
    meshes.append(MeshData(
        "organ_brain_hemisphere_l", pos_bl, norm_bl, ind_bl, MAT_ORGAN_BRAIN,
        extras={"structure_id": "brain", "name": "Left Cerebral Hemisphere", "system": "Nervous System", "layer": "organs", "exploded_offset": [-0.15, 0.15, 0.35]}
    ))
    
    pos_br, norm_br, ind_br = create_ellipsoid(0.045, 0.055, 0.065, n_lat=16, n_lon=20, offset=(0.024, 1.66, 0.01))
    meshes.append(MeshData(
        "organ_brain_hemisphere_r", pos_br, norm_br, ind_br, MAT_ORGAN_BRAIN,
        extras={"structure_id": "brain", "name": "Right Cerebral Hemisphere", "system": "Nervous System", "layer": "organs", "exploded_offset": [0.15, 0.15, 0.35]}
    ))
    
    pos_cb, norm_cb, ind_cb = create_ellipsoid(0.04, 0.025, 0.035, n_lat=12, n_lon=16, offset=(0.0, 1.59, -0.035))
    meshes.append(MeshData(
        "organ_cerebellum", pos_cb, norm_cb, ind_cb, MAT_ORGAN_BRAIN,
        extras={"structure_id": "cerebellum", "name": "Cerebellum", "system": "Nervous System", "layer": "organs", "exploded_offset": [0.0, 0.08, 0.30]}
    ))
    
    pos_bs, norm_bs, ind_bs = create_cylinder(0.012, 0.015, 0.05, n_radial=12, offset=(0.0, 1.54, -0.01))
    meshes.append(MeshData(
        "organ_brainstem", pos_bs, norm_bs, ind_bs, MAT_ORGAN_BRAIN,
        extras={"structure_id": "brainstem", "name": "Brainstem", "system": "Nervous System", "layer": "organs", "exploded_offset": [0.0, 0.02, 0.25]}
    ))
    
    # 2. HEART
    pos_h, norm_h, ind_h = create_ellipsoid(0.045, 0.055, 0.04, n_lat=16, n_lon=20, offset=(-0.025, 1.28, 0.045))
    meshes.append(MeshData(
        "organ_heart", pos_h, norm_h, ind_h, MAT_ORGAN_HEART,
        extras={"structure_id": "heart", "name": "Heart", "system": "Cardiovascular System", "layer": "organs", "exploded_offset": [-0.18, 0.05, 0.45]}
    ))
    # Aortic Arch
    aorta_path = [
        [-0.02, 1.32, 0.04], [-0.015, 1.35, 0.035], [-0.005, 1.365, 0.02],
        [0.005, 1.355, 0.0], [0.005, 1.31, -0.01], [0.005, 1.20, -0.015]
    ]
    pos_ao, norm_ao, ind_ao = create_tube(aorta_path, 0.011, n_radial=12)
    meshes.append(MeshData(
        "vessel_aortic_arch", pos_ao, norm_ao, ind_ao, MAT_ARTERY_RED,
        extras={"structure_id": "aorta", "name": "Aorta & Aortic Arch", "system": "Cardiovascular System", "layer": "veins", "exploded_offset": [0.0, 0.05, 0.35]}
    ))
    
    # 3. LUNGS (Left - 2 lobes, Right - 3 lobes)
    pos_ll, norm_ll, ind_ll = create_ellipsoid(0.048, 0.09, 0.055, n_lat=16, n_lon=20, offset=(-0.085, 1.29, 0.02))
    meshes.append(MeshData(
        "organ_lung_left", pos_ll, norm_ll, ind_ll, MAT_ORGAN_LUNG,
        extras={"structure_id": "lungs", "name": "Left Lung", "system": "Respiratory System", "layer": "organs", "exploded_offset": [-0.35, 0.05, 0.35]}
    ))
    
    pos_lr, norm_lr, ind_lr = create_ellipsoid(0.054, 0.095, 0.06, n_lat=16, n_lon=20, offset=(0.085, 1.29, 0.02))
    meshes.append(MeshData(
        "organ_lung_right", pos_lr, norm_lr, ind_lr, MAT_ORGAN_LUNG,
        extras={"structure_id": "lungs", "name": "Right Lung", "system": "Respiratory System", "layer": "organs", "exploded_offset": [0.35, 0.05, 0.35]}
    ))
    
    # Trachea
    trachea_path = [[0.0, 1.48, -0.005], [0.0, 1.41, 0.005], [0.0, 1.35, 0.01]]
    pos_tr, norm_tr, ind_tr = create_tube(trachea_path, 0.012, n_radial=12)
    meshes.append(MeshData(
        "organ_trachea", pos_tr, norm_tr, ind_tr, MAT_BONE_IVORY,
        extras={"structure_id": "trachea", "name": "Trachea", "system": "Respiratory System", "layer": "organs", "exploded_offset": [0.0, 0.08, 0.25]}
    ))

    # 4. LIVER
    pos_liv, norm_liv, ind_liv = create_ellipsoid(0.095, 0.06, 0.065, n_lat=16, n_lon=20, offset=(0.05, 1.16, 0.04))
    meshes.append(MeshData(
        "organ_liver", pos_liv, norm_liv, ind_liv, MAT_ORGAN_LIVER,
        extras={"structure_id": "liver", "name": "Liver", "system": "Digestive System", "layer": "organs", "exploded_offset": [0.28, -0.05, 0.40]}
    ))
    
    # 5. STOMACH (J-shaped tube)
    stomach_path = [
        [-0.01, 1.22, 0.01], [-0.03, 1.18, 0.04], [-0.07, 1.16, 0.045],
        [-0.06, 1.11, 0.04], [-0.01, 1.10, 0.035], [0.02, 1.11, 0.02]
    ]
    stomach_radii = [0.022, 0.04, 0.048, 0.042, 0.028, 0.018]
    pos_st, norm_st, ind_st = create_tube(stomach_path, stomach_radii, n_radial=16)
    meshes.append(MeshData(
        "organ_stomach", pos_st, norm_st, ind_st, MAT_ORGAN_STOMACH,
        extras={"structure_id": "stomach", "name": "Stomach", "system": "Digestive System", "layer": "organs", "exploded_offset": [-0.25, -0.05, 0.42]}
    ))
    
    # 6. SPLEEN
    pos_sp, norm_sp, ind_sp = create_ellipsoid(0.025, 0.04, 0.02, n_lat=12, n_lon=16, offset=(-0.11, 1.16, 0.01))
    meshes.append(MeshData(
        "organ_spleen", pos_sp, norm_sp, ind_sp, MAT_ORGAN_HEART,
        extras={"structure_id": "spleen", "name": "Spleen", "system": "Lymphatic / Immune System", "layer": "organs", "exploded_offset": [-0.32, -0.03, 0.32]}
    ))
    
    # 7. KIDNEYS (Bean-shaped)
    pos_kl, norm_kl, ind_kl = create_ellipsoid(0.028, 0.045, 0.025, n_lat=14, n_lon=18, offset=(-0.065, 1.11, -0.035))
    meshes.append(MeshData(
        "organ_kidney_left", pos_kl, norm_kl, ind_kl, MAT_ORGAN_KIDNEY,
        extras={"structure_id": "kidneys", "name": "Left Kidney", "system": "Urinary System", "layer": "organs", "exploded_offset": [-0.22, -0.08, -0.15]}
    ))
    pos_kr, norm_kr, ind_kr = create_ellipsoid(0.028, 0.045, 0.025, n_lat=14, n_lon=18, offset=(0.065, 1.09, -0.035))
    meshes.append(MeshData(
        "organ_kidney_right", pos_kr, norm_kr, ind_kr, MAT_ORGAN_KIDNEY,
        extras={"structure_id": "kidneys", "name": "Right Kidney", "system": "Urinary System", "layer": "organs", "exploded_offset": [0.22, -0.08, -0.15]}
    ))
    
    # 8. PANCREAS
    pos_pan, norm_pan, ind_pan = create_ellipsoid(0.055, 0.016, 0.02, n_lat=12, n_lon=16, offset=(-0.01, 1.12, 0.015))
    meshes.append(MeshData(
        "organ_pancreas", pos_pan, norm_pan, ind_pan, MAT_ORGAN_INTESTINE,
        extras={"structure_id": "pancreas", "name": "Pancreas", "system": "Endocrine / Digestive System", "layer": "organs", "exploded_offset": [0.0, -0.06, 0.30]}
    ))
    
    # 9. INTESTINES (Small & Large Colon)
    pos_si, norm_si, ind_si = create_ellipsoid(0.065, 0.065, 0.045, n_lat=16, n_lon=20, offset=(0.0, 0.99, 0.04))
    meshes.append(MeshData(
        "organ_small_intestine", pos_si, norm_si, ind_si, MAT_ORGAN_INTESTINE,
        extras={"structure_id": "small_intestine", "name": "Small Intestine (Jejunum & Ileum)", "system": "Digestive System", "layer": "organs", "exploded_offset": [0.0, -0.15, 0.45]}
    ))
    
    colon_path = [
        [0.08, 0.93, 0.03], [0.085, 1.06, 0.04], [0.05, 1.08, 0.05],
        [0.0, 1.08, 0.05], [-0.05, 1.08, 0.05], [-0.085, 1.06, 0.04],
        [-0.08, 0.93, 0.03], [-0.04, 0.88, 0.02], [0.0, 0.84, -0.01]
    ]
    pos_col, norm_col, ind_col = create_tube(colon_path, 0.02, n_radial=14)
    meshes.append(MeshData(
        "organ_large_intestine", pos_col, norm_col, ind_col, MAT_ORGAN_INTESTINE,
        extras={"structure_id": "large_intestine", "name": "Large Intestine (Colon)", "system": "Digestive System", "layer": "organs", "exploded_offset": [0.0, -0.12, 0.50]}
    ))
    
    # 10. BLADDER
    pos_bld, norm_bld, ind_bld = create_ellipsoid(0.032, 0.03, 0.028, n_lat=12, n_lon=16, offset=(0.0, 0.88, 0.035))
    meshes.append(MeshData(
        "organ_urinary_bladder", pos_bld, norm_bld, ind_bld, MAT_ORGAN_INTESTINE,
        extras={"structure_id": "bladder", "name": "Urinary Bladder", "system": "Urinary System", "layer": "organs", "exploded_offset": [0.0, -0.18, 0.35]}
    ))

    # GENDER REPRODUCTIVE SYSTEM
    if gender == "female":
        # Uterus (Fundus, Body, Cervix) matching Image 2 prominent coral organ!
        pos_ut, norm_ut, ind_ut = create_ellipsoid(0.022, 0.032, 0.018, n_lat=14, n_lon=18, offset=(0.0, 0.91, 0.025))
        meshes.append(MeshData(
            "organ_uterus", pos_ut, norm_ut, ind_ut, MAT_REPRODUCTIVE_F,
            extras={"structure_id": "uterus", "name": "Uterus", "system": "Reproductive System", "layer": "organs", "exploded_offset": [0.0, -0.12, 0.38]}
        ))
        # Left Fallopian Tube & Ovary
        tube_l = [[-0.015, 0.93, 0.025], [-0.04, 0.94, 0.028], [-0.065, 0.925, 0.022]]
        pos_ftl, norm_ftl, ind_ftl = create_tube(tube_l, 0.005, n_radial=10)
        meshes.append(MeshData(
            "organ_fallopian_tube_l", pos_ftl, norm_ftl, ind_ftl, MAT_REPRODUCTIVE_F,
            extras={"structure_id": "fallopian_tubes", "name": "Left Fallopian Tube", "system": "Reproductive System", "layer": "organs", "exploded_offset": [-0.15, -0.1, 0.38]}
        ))
        pos_ovl, norm_ovl, ind_ovl = create_ellipsoid(0.011, 0.008, 0.007, n_lat=10, n_lon=12, offset=(-0.06, 0.915, 0.02))
        meshes.append(MeshData(
            "organ_ovary_l", pos_ovl, norm_ovl, ind_ovl, MAT_TENDON_WHITE,
            extras={"structure_id": "ovaries", "name": "Left Ovary", "system": "Reproductive System", "layer": "organs", "exploded_offset": [-0.16, -0.1, 0.38]}
        ))
        
        # Right Fallopian Tube & Ovary
        tube_r = [[0.015, 0.93, 0.025], [0.04, 0.94, 0.028], [0.065, 0.925, 0.022]]
        pos_ftr, norm_ftr, ind_ftr = create_tube(tube_r, 0.005, n_radial=10)
        meshes.append(MeshData(
            "organ_fallopian_tube_r", pos_ftr, norm_ftr, ind_ftr, MAT_REPRODUCTIVE_F,
            extras={"structure_id": "fallopian_tubes", "name": "Right Fallopian Tube", "system": "Reproductive System", "layer": "organs", "exploded_offset": [0.15, -0.1, 0.38]}
        ))
        pos_ovr, norm_ovr, ind_ovr = create_ellipsoid(0.011, 0.008, 0.007, n_lat=10, n_lon=12, offset=(0.06, 0.915, 0.02))
        meshes.append(MeshData(
            "organ_ovary_r", pos_ovr, norm_ovr, ind_ovr, MAT_TENDON_WHITE,
            extras={"structure_id": "ovaries", "name": "Right Ovary", "system": "Reproductive System", "layer": "organs", "exploded_offset": [0.16, -0.1, 0.38]}
        ))
        
        # Female Breasts / Mammary Tissue
        pos_mbl, norm_mbl, ind_mbl = create_ellipsoid(0.052, 0.052, 0.045, n_lat=16, n_lon=20, offset=(-0.095, 1.28, 0.11))
        meshes.append(MeshData(
            "female_breast_l", pos_mbl, norm_mbl, ind_mbl, MAT_MUSCLE_RED,
            extras={"structure_id": "mammary_glands", "name": "Left Breast (Mammary Gland)", "system": "Reproductive System", "layer": "muscles", "exploded_offset": [-0.25, 0.05, 0.40]}
        ))
        pos_mbr, norm_mbr, ind_mbr = create_ellipsoid(0.052, 0.052, 0.045, n_lat=16, n_lon=20, offset=(0.095, 1.28, 0.11))
        meshes.append(MeshData(
            "female_breast_r", pos_mbr, norm_mbr, ind_mbr, MAT_MUSCLE_RED,
            extras={"structure_id": "mammary_glands", "name": "Right Breast (Mammary Gland)", "system": "Reproductive System", "layer": "muscles", "exploded_offset": [0.25, 0.05, 0.40]}
        ))
    else:
        # Male Genitalia (Penis & Scrotum) matching Image 1
        penis_path = [[0.0, 0.865, 0.04], [0.0, 0.84, 0.065], [0.0, 0.79, 0.065]]
        pos_pen, norm_pen, ind_pen = create_tube(penis_path, [0.015, 0.014, 0.016], n_radial=14)
        meshes.append(MeshData(
            "male_penis", pos_pen, norm_pen, ind_pen, MAT_REPRODUCTIVE_M,
            extras={"structure_id": "penis", "name": "Penis", "system": "Reproductive System", "layer": "organs", "exploded_offset": [0.0, -0.15, 0.35]}
        ))
        pos_sc, norm_sc, ind_sc = create_ellipsoid(0.024, 0.026, 0.02, n_lat=12, n_lon=16, offset=(0.0, 0.81, 0.04))
        meshes.append(MeshData(
            "male_scrotum", pos_sc, norm_sc, ind_sc, MAT_REPRODUCTIVE_M,
            extras={"structure_id": "testes", "name": "Scrotum & Testes", "system": "Reproductive System", "layer": "organs", "exploded_offset": [0.0, -0.18, 0.35]}
        ))
        pos_pr, norm_pr, ind_pr = create_ellipsoid(0.018, 0.016, 0.016, n_lat=10, n_lon=14, offset=(0.0, 0.86, 0.01))
        meshes.append(MeshData(
            "male_prostate", pos_pr, norm_pr, ind_pr, MAT_ORGAN_KIDNEY,
            extras={"structure_id": "prostate", "name": "Prostate Gland", "system": "Reproductive System", "layer": "organs", "exploded_offset": [0.0, -0.12, 0.25]}
        ))
        
    return meshes

# -------------------------------------------------------------
# MUSCLES BUILDER (Ecorche style with tendons & deep muscle bellies)
# -------------------------------------------------------------
def build_muscles(gender="male"):
    meshes = []
    
    # Proportional adjustments
    w_shoulder = 0.20 if gender == "male" else 0.17
    w_pelvis = 0.14 if gender == "male" else 0.16
    waist_taper = 0.88 if gender == "female" else 1.0
    
    # 1. HEAD & FACIAL MUSCLES
    pos_front, norm_front, ind_front = create_ellipsoid(0.065, 0.04, 0.04, n_lat=12, n_lon=16, offset=(0.0, 1.68, 0.055))
    meshes.append(MeshData(
        "muscle_frontalis", pos_front, norm_front, ind_front, MAT_MUSCLE_RED,
        extras={"structure_id": "frontalis", "name": "Frontalis Muscle", "system": "Muscular System", "layer": "muscles", "exploded_offset": [0.0, 0.2, 0.35]}
    ))
    
    # Temporalis Left & Right
    pos_templ, norm_templ, ind_templ = create_ellipsoid(0.015, 0.035, 0.04, n_lat=12, n_lon=16, offset=(-0.065, 1.65, 0.01))
    meshes.append(MeshData(
        "muscle_temporalis_l", pos_templ, norm_templ, ind_templ, MAT_MUSCLE_RED,
        extras={"structure_id": "temporalis", "name": "Left Temporalis", "system": "Muscular System", "layer": "muscles", "exploded_offset": [-0.25, 0.15, 0.1]}
    ))
    pos_tempr, norm_tempr, ind_tempr = create_ellipsoid(0.015, 0.035, 0.04, n_lat=12, n_lon=16, offset=(0.065, 1.65, 0.01))
    meshes.append(MeshData(
        "muscle_temporalis_r", pos_tempr, norm_tempr, ind_tempr, MAT_MUSCLE_RED,
        extras={"structure_id": "temporalis", "name": "Right Temporalis", "system": "Muscular System", "layer": "muscles", "exploded_offset": [0.25, 0.15, 0.1]}
    ))
    
    # Masseter Left & Right
    pos_masl, norm_masl, ind_masl = create_ellipsoid(0.018, 0.03, 0.02, n_lat=10, n_lon=14, offset=(-0.055, 1.56, 0.035))
    meshes.append(MeshData(
        "muscle_masseter_l", pos_masl, norm_masl, ind_masl, MAT_MUSCLE_RED,
        extras={"structure_id": "masseter", "name": "Left Masseter", "system": "Muscular System", "layer": "muscles", "exploded_offset": [-0.2, 0.05, 0.2]}
    ))
    pos_masr, norm_masr, ind_masr = create_ellipsoid(0.018, 0.03, 0.02, n_lat=10, n_lon=14, offset=(0.055, 1.56, 0.035))
    meshes.append(MeshData(
        "muscle_masseter_r", pos_masr, norm_masr, ind_masr, MAT_MUSCLE_RED,
        extras={"structure_id": "masseter", "name": "Right Masseter", "system": "Muscular System", "layer": "muscles", "exploded_offset": [0.2, 0.05, 0.2]}
    ))

    # 2. NECK: Sternocleidomastoid & Trapezius
    pos_scml, norm_scml, ind_scml = create_muscle_belly(
        [-0.05, 1.57, -0.01], [-0.015, 1.45, 0.04], belly_radii=(0.016, 0.012), curve_bend=[-0.01, 0.0, 0.02]
    )
    meshes.append(MeshData(
        "muscle_sternocleidomastoid_l", pos_scml, norm_scml, ind_scml, MAT_MUSCLE_RED,
        extras={"structure_id": "sternocleidomastoid", "name": "Left Sternocleidomastoid", "system": "Muscular System", "layer": "muscles", "exploded_offset": [-0.15, 0.08, 0.25]}
    ))
    pos_scmr, norm_scmr, ind_scmr = create_muscle_belly(
        [0.05, 1.57, -0.01], [0.015, 1.45, 0.04], belly_radii=(0.016, 0.012), curve_bend=[0.01, 0.0, 0.02]
    )
    meshes.append(MeshData(
        "muscle_sternocleidomastoid_r", pos_scmr, norm_scmr, ind_scmr, MAT_MUSCLE_RED,
        extras={"structure_id": "sternocleidomastoid", "name": "Right Sternocleidomastoid", "system": "Muscular System", "layer": "muscles", "exploded_offset": [0.15, 0.08, 0.25]}
    ))

    # 3. CHEST: Pectoralis Major (Left & Right)
    pos_pecl, norm_pecl, ind_pecl = create_muscle_belly(
        [-0.015, 1.34, 0.065], [-w_shoulder + 0.04, 1.37, 0.03], belly_radii=(0.055, 0.035), curve_bend=[-0.02, 0.01, 0.03]
    )
    meshes.append(MeshData(
        "muscle_pectoralis_major_l", pos_pecl, norm_pecl, ind_pecl, MAT_MUSCLE_RED,
        extras={"structure_id": "pectoralis_major", "name": "Left Pectoralis Major", "system": "Muscular System", "layer": "muscles", "exploded_offset": [-0.25, 0.05, 0.35]}
    ))
    pos_pecr, norm_pecr, ind_pecr = create_muscle_belly(
        [0.015, 1.34, 0.065], [w_shoulder - 0.04, 1.37, 0.03], belly_radii=(0.055, 0.035), curve_bend=[0.02, 0.01, 0.03]
    )
    meshes.append(MeshData(
        "muscle_pectoralis_major_r", pos_pecr, norm_pecr, ind_pecr, MAT_MUSCLE_RED,
        extras={"structure_id": "pectoralis_major", "name": "Right Pectoralis Major", "system": "Muscular System", "layer": "muscles", "exploded_offset": [0.25, 0.05, 0.35]}
    ))

    # 4. ABDOMEN: Rectus Abdominis (8 segments) + Tendon Intersections
    levels = [1.24, 1.17, 1.10, 1.02]
    for seg_idx, y_level in enumerate(levels):
        # Left segment
        pos_seg_l, norm_seg_l, ind_seg_l = create_ellipsoid(0.028, 0.028, 0.018, n_lat=12, n_lon=16, offset=(-0.034, y_level, 0.065))
        meshes.append(MeshData(
            f"muscle_rectus_abdominis_l_{seg_idx+1}", pos_seg_l, norm_seg_l, ind_seg_l, MAT_MUSCLE_RED,
            extras={"structure_id": "rectus_abdominis", "name": f"Rectus Abdominis (Left Belly {seg_idx+1})", "system": "Muscular System", "layer": "muscles", "exploded_offset": [-0.15, 0.0, 0.40]}
        ))
        # Right segment
        pos_seg_r, norm_seg_r, ind_seg_r = create_ellipsoid(0.028, 0.028, 0.018, n_lat=12, n_lon=16, offset=(0.034, y_level, 0.065))
        meshes.append(MeshData(
            f"muscle_rectus_abdominis_r_{seg_idx+1}", pos_seg_r, norm_seg_r, ind_seg_r, MAT_MUSCLE_RED,
            extras={"structure_id": "rectus_abdominis", "name": f"Rectus Abdominis (Right Belly {seg_idx+1})", "system": "Muscular System", "layer": "muscles", "exploded_offset": [0.15, 0.0, 0.40]}
        ))
        
    # Linea Alba (Central tendon strip)
    la_path = [[0.0, 1.30, 0.066], [0.0, 1.15, 0.068], [0.0, 0.95, 0.062]]
    pos_la, norm_la, ind_la = create_tube(la_path, 0.007, n_radial=10)
    meshes.append(MeshData(
        "tendon_linea_alba", pos_la, norm_la, ind_la, MAT_TENDON_WHITE,
        extras={"structure_id": "linea_alba", "name": "Linea Alba & Aponeurosis", "system": "Muscular System", "layer": "muscles", "exploded_offset": [0.0, 0.0, 0.42]}
    ))

    # External Obliques (Lateral abdominal flank)
    pos_eobl, norm_eobl, ind_eobl = create_muscle_belly(
        [-0.09, 1.25, 0.02], [-w_pelvis + 0.02, 0.96, 0.04], belly_radii=(0.035, 0.025), curve_bend=[-0.03, 0.0, 0.02]
    )
    meshes.append(MeshData(
        "muscle_external_oblique_l", pos_eobl, norm_eobl, ind_eobl, MAT_MUSCLE_RED,
        extras={"structure_id": "external_oblique", "name": "Left External Oblique", "system": "Muscular System", "layer": "muscles", "exploded_offset": [-0.3, 0.0, 0.25]}
    ))
    pos_eobr, norm_eobr, ind_eobr = create_muscle_belly(
        [0.09, 1.25, 0.02], [w_pelvis - 0.02, 0.96, 0.04], belly_radii=(0.035, 0.025), curve_bend=[0.03, 0.0, 0.02]
    )
    meshes.append(MeshData(
        "muscle_external_oblique_r", pos_eobr, norm_eobr, ind_eobr, MAT_MUSCLE_RED,
        extras={"structure_id": "external_oblique", "name": "Right External Oblique", "system": "Muscular System", "layer": "muscles", "exploded_offset": [0.3, 0.0, 0.25]}
    ))

    # Serratus Anterior (Rib slips)
    pos_serl, norm_serl, ind_serl = create_ellipsoid(0.02, 0.06, 0.03, n_lat=12, n_lon=14, offset=(-0.13, 1.23, 0.01))
    meshes.append(MeshData(
        "muscle_serratus_anterior_l", pos_serl, norm_serl, ind_serl, MAT_MUSCLE_RED,
        extras={"structure_id": "serratus_anterior", "name": "Left Serratus Anterior", "system": "Muscular System", "layer": "muscles", "exploded_offset": [-0.35, 0.0, 0.15]}
    ))
    pos_serr, norm_serr, ind_serr = create_ellipsoid(0.02, 0.06, 0.03, n_lat=12, n_lon=14, offset=(0.13, 1.23, 0.01))
    meshes.append(MeshData(
        "muscle_serratus_anterior_r", pos_serr, norm_serr, ind_serr, MAT_MUSCLE_RED,
        extras={"structure_id": "serratus_anterior", "name": "Right Serratus Anterior", "system": "Muscular System", "layer": "muscles", "exploded_offset": [0.35, 0.0, 0.15]}
    ))

    # 5. SHOULDERS: Deltoids (Cap covering shoulder joint)
    pos_deltl, norm_deltl, ind_deltl = create_ellipsoid(0.045, 0.07, 0.045, n_lat=14, n_lon=18, offset=(-w_shoulder, 1.38, 0.0))
    meshes.append(MeshData(
        "muscle_deltoid_l", pos_deltl, norm_deltl, ind_deltl, MAT_MUSCLE_RED,
        extras={"structure_id": "deltoid", "name": "Left Deltoid Muscle", "system": "Muscular System", "layer": "muscles", "exploded_offset": [-0.35, 0.1, 0.15]}
    ))
    pos_deltr, norm_deltr, ind_deltr = create_ellipsoid(0.045, 0.07, 0.045, n_lat=14, n_lon=18, offset=(w_shoulder, 1.38, 0.0))
    meshes.append(MeshData(
        "muscle_deltoid_r", pos_deltr, norm_deltr, ind_deltr, MAT_MUSCLE_RED,
        extras={"structure_id": "deltoid", "name": "Right Deltoid Muscle", "system": "Muscular System", "layer": "muscles", "exploded_offset": [0.35, 0.1, 0.15]}
    ))

    # 6. UPPER ARMS: Biceps Brachii & Triceps Brachii
    # Biceps Left
    pos_bicl, norm_bicl, ind_bicl = create_muscle_belly(
        [-w_shoulder, 1.34, 0.01], [-w_shoulder - 0.04, 1.15, 0.02], belly_radii=(0.032, 0.028), curve_bend=[-0.015, 0.0, 0.025]
    )
    meshes.append(MeshData(
        "muscle_biceps_brachii_l", pos_bicl, norm_bicl, ind_bicl, MAT_MUSCLE_RED,
        extras={"structure_id": "biceps_brachii", "name": "Left Biceps Brachii", "system": "Muscular System", "layer": "muscles", "exploded_offset": [-0.35, -0.05, 0.3]}
    ))
    # Biceps Right
    pos_bicr, norm_bicr, ind_bicr = create_muscle_belly(
        [w_shoulder, 1.34, 0.01], [w_shoulder + 0.04, 1.15, 0.02], belly_radii=(0.032, 0.028), curve_bend=[0.015, 0.0, 0.025]
    )
    meshes.append(MeshData(
        "muscle_biceps_brachii_r", pos_bicr, norm_bicr, ind_bicr, MAT_MUSCLE_RED,
        extras={"structure_id": "biceps_brachii", "name": "Right Biceps Brachii", "system": "Muscular System", "layer": "muscles", "exploded_offset": [0.35, -0.05, 0.3]}
    ))
    
    # Triceps Left & Right (Posterior arm)
    pos_tril, norm_tril, ind_tril = create_muscle_belly(
        [-w_shoulder, 1.35, -0.015], [-w_shoulder - 0.035, 1.16, -0.02], belly_radii=(0.034, 0.03), curve_bend=[-0.015, 0.0, -0.02]
    )
    meshes.append(MeshData(
        "muscle_triceps_brachii_l", pos_tril, norm_tril, ind_tril, MAT_MUSCLE_RED,
        extras={"structure_id": "triceps_brachii", "name": "Left Triceps Brachii", "system": "Muscular System", "layer": "muscles", "exploded_offset": [-0.35, -0.05, -0.2]}
    ))
    pos_trir, norm_trir, ind_trir = create_muscle_belly(
        [w_shoulder, 1.35, -0.015], [w_shoulder + 0.035, 1.16, -0.02], belly_radii=(0.034, 0.03), curve_bend=[0.015, 0.0, -0.02]
    )
    meshes.append(MeshData(
        "muscle_triceps_brachii_r", pos_trir, norm_trir, ind_trir, MAT_MUSCLE_RED,
        extras={"structure_id": "triceps_brachii", "name": "Right Triceps Brachii", "system": "Muscular System", "layer": "muscles", "exploded_offset": [0.35, -0.05, -0.2]}
    ))

    # 7. FOREARMS: Brachioradialis & Forearm Flexors
    pos_bral, norm_bral, ind_bral = create_muscle_belly(
        [-w_shoulder - 0.04, 1.16, 0.01], [-w_shoulder - 0.08, 0.94, 0.02], belly_radii=(0.028, 0.022), curve_bend=[-0.02, 0.0, 0.01]
    )
    meshes.append(MeshData(
        "muscle_brachioradialis_l", pos_bral, norm_bral, ind_bral, MAT_MUSCLE_RED,
        extras={"structure_id": "brachioradialis", "name": "Left Brachioradialis & Flexors", "system": "Muscular System", "layer": "muscles", "exploded_offset": [-0.4, -0.1, 0.2]}
    ))
    pos_brar, norm_brar, ind_brar = create_muscle_belly(
        [w_shoulder + 0.04, 1.16, 0.01], [w_shoulder + 0.08, 0.94, 0.02], belly_radii=(0.028, 0.022), curve_bend=[0.02, 0.0, 0.01]
    )
    meshes.append(MeshData(
        "muscle_brachioradialis_r", pos_brar, norm_brar, ind_brar, MAT_MUSCLE_RED,
        extras={"structure_id": "brachioradialis", "name": "Right Brachioradialis & Flexors", "system": "Muscular System", "layer": "muscles", "exploded_offset": [0.4, -0.1, 0.2]}
    ))

    # Hands & Tendons
    pos_hndl, norm_hndl, ind_hndl = create_ellipsoid(0.018, 0.05, 0.012, n_lat=10, n_lon=14, offset=(-w_shoulder - 0.09, 0.88, 0.02))
    meshes.append(MeshData(
        "tendon_hand_l", pos_hndl, norm_hndl, ind_hndl, MAT_TENDON_WHITE,
        extras={"structure_id": "hand_tendons", "name": "Left Hand & Palmar Tendons", "system": "Muscular System", "layer": "muscles", "exploded_offset": [-0.45, -0.15, 0.15]}
    ))
    pos_hndr, norm_hndr, ind_hndr = create_ellipsoid(0.018, 0.05, 0.012, n_lat=10, n_lon=14, offset=(w_shoulder + 0.09, 0.88, 0.02))
    meshes.append(MeshData(
        "tendon_hand_r", pos_hndr, norm_hndr, ind_hndr, MAT_TENDON_WHITE,
        extras={"structure_id": "hand_tendons", "name": "Right Hand & Palmar Tendons", "system": "Muscular System", "layer": "muscles", "exploded_offset": [0.45, -0.15, 0.15]}
    ))

    # 8. THIGHS: Quadriceps (Rectus Femoris, Vastus Lateralis, Vastus Medialis, Sartorius)
    # Rectus Femoris Left
    pos_rfl, norm_rfl, ind_rfl = create_muscle_belly(
        [-0.09, 0.88, 0.04], [-0.075, 0.54, 0.045], belly_radii=(0.038, 0.032), curve_bend=[-0.01, 0.0, 0.03]
    )
    meshes.append(MeshData(
        "muscle_rectus_femoris_l", pos_rfl, norm_rfl, ind_rfl, MAT_MUSCLE_RED,
        extras={"structure_id": "rectus_femoris", "name": "Left Rectus Femoris", "system": "Muscular System", "layer": "muscles", "exploded_offset": [-0.25, -0.1, 0.35]}
    ))
    # Rectus Femoris Right
    pos_rfr, norm_rfr, ind_rfr = create_muscle_belly(
        [0.09, 0.88, 0.04], [0.075, 0.54, 0.045], belly_radii=(0.038, 0.032), curve_bend=[0.01, 0.0, 0.03]
    )
    meshes.append(MeshData(
        "muscle_rectus_femoris_r", pos_rfr, norm_rfr, ind_rfr, MAT_MUSCLE_RED,
        extras={"structure_id": "rectus_femoris", "name": "Right Rectus Femoris", "system": "Muscular System", "layer": "muscles", "exploded_offset": [0.25, -0.1, 0.35]}
    ))

    # Vastus Lateralis Left & Right (Outer thigh muscle bulge)
    pos_vll, norm_vll, ind_vll = create_muscle_belly(
        [-0.12, 0.85, 0.01], [-0.095, 0.55, 0.02], belly_radii=(0.045, 0.035), curve_bend=[-0.03, 0.0, 0.02]
    )
    meshes.append(MeshData(
        "muscle_vastus_lateralis_l", pos_vll, norm_vll, ind_vll, MAT_MUSCLE_RED,
        extras={"structure_id": "vastus_lateralis", "name": "Left Vastus Lateralis", "system": "Muscular System", "layer": "muscles", "exploded_offset": [-0.35, -0.1, 0.25]}
    ))
    pos_vlr, norm_vlr, ind_vlr = create_muscle_belly(
        [0.12, 0.85, 0.01], [0.095, 0.55, 0.02], belly_radii=(0.045, 0.035), curve_bend=[0.03, 0.0, 0.02]
    )
    meshes.append(MeshData(
        "muscle_vastus_lateralis_r", pos_vlr, norm_vlr, ind_vlr, MAT_MUSCLE_RED,
        extras={"structure_id": "vastus_lateralis", "name": "Right Vastus Lateralis", "system": "Muscular System", "layer": "muscles", "exploded_offset": [0.35, -0.1, 0.25]}
    ))

    # Vastus Medialis (Teardrop suprapatellar belly, prominent in anatomical atlas!)
    pos_vml, norm_vml, ind_vml = create_ellipsoid(0.03, 0.05, 0.025, n_lat=12, n_lon=16, offset=(-0.055, 0.55, 0.04))
    meshes.append(MeshData(
        "muscle_vastus_medialis_l", pos_vml, norm_vml, ind_vml, MAT_MUSCLE_RED,
        extras={"structure_id": "vastus_medialis", "name": "Left Vastus Medialis (Teardrop)", "system": "Muscular System", "layer": "muscles", "exploded_offset": [-0.18, -0.1, 0.32]}
    ))
    pos_vmr, norm_vmr, ind_vmr = create_ellipsoid(0.03, 0.05, 0.025, n_lat=12, n_lon=16, offset=(0.055, 0.55, 0.04))
    meshes.append(MeshData(
        "muscle_vastus_medialis_r", pos_vmr, norm_vmr, ind_vmr, MAT_MUSCLE_RED,
        extras={"structure_id": "vastus_medialis", "name": "Right Vastus Medialis (Teardrop)", "system": "Muscular System", "layer": "muscles", "exploded_offset": [0.18, -0.1, 0.32]}
    ))

    # Sartorius (Long diagonal ribbon across anterior thigh)
    sart_l = [[-0.12, 0.88, 0.03], [-0.08, 0.72, 0.04], [-0.045, 0.52, 0.02]]
    pos_sartl, norm_sartl, ind_sartl = create_tube(sart_l, 0.012, n_radial=10)
    meshes.append(MeshData(
        "muscle_sartorius_l", pos_sartl, norm_sartl, ind_sartl, MAT_MUSCLE_RED,
        extras={"structure_id": "sartorius", "name": "Left Sartorius Muscle", "system": "Muscular System", "layer": "muscles", "exploded_offset": [-0.22, -0.1, 0.35]}
    ))
    sart_r = [[0.12, 0.88, 0.03], [0.08, 0.72, 0.04], [0.045, 0.52, 0.02]]
    pos_sartr, norm_sartr, ind_sartr = create_tube(sart_r, 0.012, n_radial=10)
    meshes.append(MeshData(
        "muscle_sartorius_r", pos_sartr, norm_sartr, ind_sartr, MAT_MUSCLE_RED,
        extras={"structure_id": "sartorius", "name": "Right Sartorius Muscle", "system": "Muscular System", "layer": "muscles", "exploded_offset": [0.22, -0.1, 0.35]}
    ))

    # 9. KNEE: Patellar Tendon (White glistening tendon)
    pos_ptl, norm_ptl, ind_ptl = create_cylinder(0.015, 0.012, 0.06, n_radial=12, offset=(-0.075, 0.47, 0.05))
    meshes.append(MeshData(
        "tendon_patellar_l", pos_ptl, norm_ptl, ind_ptl, MAT_TENDON_WHITE,
        extras={"structure_id": "patellar_tendon", "name": "Left Patellar Tendon", "system": "Muscular System", "layer": "muscles", "exploded_offset": [-0.15, -0.15, 0.3]}
    ))
    pos_ptr, norm_ptr, ind_ptr = create_cylinder(0.015, 0.012, 0.06, n_radial=12, offset=(0.075, 0.47, 0.05))
    meshes.append(MeshData(
        "tendon_patellar_r", pos_ptr, norm_ptr, ind_ptr, MAT_TENDON_WHITE,
        extras={"structure_id": "patellar_tendon", "name": "Right Patellar Tendon", "system": "Muscular System", "layer": "muscles", "exploded_offset": [0.15, -0.15, 0.3]}
    ))

    # 10. LOWER LEGS: Tibialis Anterior & Gastrocnemius & Achilles Tendon
    # Tibialis Anterior Left & Right
    pos_tal, norm_tal, ind_tal = create_muscle_belly(
        [-0.075, 0.45, 0.035], [-0.055, 0.15, 0.04], belly_radii=(0.026, 0.022), curve_bend=[-0.01, 0.0, 0.015]
    )
    meshes.append(MeshData(
        "muscle_tibialis_anterior_l", pos_tal, norm_tal, ind_tal, MAT_MUSCLE_RED,
        extras={"structure_id": "tibialis_anterior", "name": "Left Tibialis Anterior", "system": "Muscular System", "layer": "muscles", "exploded_offset": [-0.22, -0.15, 0.25]}
    ))
    pos_tar, norm_tar, ind_tar = create_muscle_belly(
        [0.075, 0.45, 0.035], [0.055, 0.15, 0.04], belly_radii=(0.026, 0.022), curve_bend=[0.01, 0.0, 0.015]
    )
    meshes.append(MeshData(
        "muscle_tibialis_anterior_r", pos_tar, norm_tar, ind_tar, MAT_MUSCLE_RED,
        extras={"structure_id": "tibialis_anterior", "name": "Right Tibialis Anterior", "system": "Muscular System", "layer": "muscles", "exploded_offset": [0.22, -0.15, 0.25]}
    ))

    # Gastrocnemius (Calf bellies - Medial and Lateral)
    pos_gasl, norm_gasl, ind_gasl = create_muscle_belly(
        [-0.075, 0.48, -0.02], [-0.065, 0.24, -0.025], belly_radii=(0.036, 0.032), curve_bend=[-0.015, 0.0, -0.02]
    )
    meshes.append(MeshData(
        "muscle_gastrocnemius_l", pos_gasl, norm_gasl, ind_gasl, MAT_MUSCLE_RED,
        extras={"structure_id": "gastrocnemius", "name": "Left Gastrocnemius (Calf)", "system": "Muscular System", "layer": "muscles", "exploded_offset": [-0.25, -0.15, -0.2]}
    ))
    pos_gasr, norm_gasr, ind_gasr = create_muscle_belly(
        [0.075, 0.48, -0.02], [0.065, 0.24, -0.025], belly_radii=(0.036, 0.032), curve_bend=[0.015, 0.0, -0.02]
    )
    meshes.append(MeshData(
        "muscle_gastrocnemius_r", pos_gasr, norm_gasr, ind_gasr, MAT_MUSCLE_RED,
        extras={"structure_id": "gastrocnemius", "name": "Right Gastrocnemius (Calf)", "system": "Muscular System", "layer": "muscles", "exploded_offset": [0.25, -0.15, -0.2]}
    ))

    # Achilles Tendon (Calcaneal tendon in pearl white)
    pos_achl, norm_achl, ind_achl = create_cylinder(0.012, 0.015, 0.16, n_radial=12, offset=(-0.065, 0.14, -0.03))
    meshes.append(MeshData(
        "tendon_achilles_l", pos_achl, norm_achl, ind_achl, MAT_TENDON_WHITE,
        extras={"structure_id": "achilles_tendon", "name": "Left Achilles Tendon", "system": "Muscular System", "layer": "muscles", "exploded_offset": [-0.2, -0.2, -0.2]}
    ))
    pos_achr, norm_achr, ind_achr = create_cylinder(0.012, 0.015, 0.16, n_radial=12, offset=(0.065, 0.14, -0.03))
    meshes.append(MeshData(
        "tendon_achilles_r", pos_achr, norm_achr, ind_achr, MAT_TENDON_WHITE,
        extras={"structure_id": "achilles_tendon", "name": "Right Achilles Tendon", "system": "Muscular System", "layer": "muscles", "exploded_offset": [0.2, -0.2, -0.2]}
    ))

    # Feet Extensor Tendons & Dorsal Aponeurosis
    pos_ftl, norm_ftl, ind_ftl = create_ellipsoid(0.03, 0.018, 0.07, n_lat=10, n_lon=14, offset=(-0.065, 0.03, 0.04))
    meshes.append(MeshData(
        "tendon_foot_l", pos_ftl, norm_ftl, ind_ftl, MAT_TENDON_WHITE,
        extras={"structure_id": "foot_tendons", "name": "Left Dorsal Foot Tendons", "system": "Muscular System", "layer": "muscles", "exploded_offset": [-0.2, -0.25, 0.2]}
    ))
    pos_ftr, norm_ftr, ind_ftr = create_ellipsoid(0.03, 0.018, 0.07, n_lat=10, n_lon=14, offset=(0.065, 0.03, 0.04))
    meshes.append(MeshData(
        "tendon_foot_r", pos_ftr, norm_ftr, ind_ftr, MAT_TENDON_WHITE,
        extras={"structure_id": "foot_tendons", "name": "Right Dorsal Foot Tendons", "system": "Muscular System", "layer": "muscles", "exploded_offset": [0.2, -0.25, 0.2]}
    ))

    return meshes

# -------------------------------------------------------------
# VEINS & ARTERIES BUILDER (Cardiovascular System)
# -------------------------------------------------------------
def build_vessels():
    meshes = []
    
    # 1. ARTERIES (Red)
    # Carotid Arteries (Left & Right to head)
    carotid_l = [[-0.01, 1.35, 0.02], [-0.025, 1.48, 0.01], [-0.03, 1.60, 0.01]]
    pos_cl, norm_cl, ind_cl = create_tube(carotid_l, 0.006, n_radial=10)
    meshes.append(MeshData(
        "artery_carotid_l", pos_cl, norm_cl, ind_cl, MAT_ARTERY_RED,
        extras={"structure_id": "carotid_artery", "name": "Left Common Carotid Artery", "system": "Cardiovascular System", "layer": "veins", "exploded_offset": [-0.1, 0.1, 0.2]}
    ))
    carotid_r = [[0.01, 1.35, 0.02], [0.025, 1.48, 0.01], [0.03, 1.60, 0.01]]
    pos_cr, norm_cr, ind_cr = create_tube(carotid_r, 0.006, n_radial=10)
    meshes.append(MeshData(
        "artery_carotid_r", pos_cr, norm_cr, ind_cr, MAT_ARTERY_RED,
        extras={"structure_id": "carotid_artery", "name": "Right Common Carotid Artery", "system": "Cardiovascular System", "layer": "veins", "exploded_offset": [0.1, 0.1, 0.2]}
    ))
    
    # Brachial Arteries (Arm supply)
    brachial_l = [[-0.04, 1.37, 0.01], [-0.17, 1.32, 0.0], [-0.19, 1.15, 0.01], [-0.22, 0.92, 0.02]]
    pos_bal, norm_bal, ind_bal = create_tube(brachial_l, 0.005, n_radial=10)
    meshes.append(MeshData(
        "artery_brachial_l", pos_bal, norm_bal, ind_bal, MAT_ARTERY_RED,
        extras={"structure_id": "brachial_vessels", "name": "Left Brachial & Radial Artery", "system": "Cardiovascular System", "layer": "veins", "exploded_offset": [-0.3, 0.0, 0.2]}
    ))
    brachial_r = [[0.04, 1.37, 0.01], [0.17, 1.32, 0.0], [0.19, 1.15, 0.01], [0.22, 0.92, 0.02]]
    pos_bar, norm_bar, ind_bar = create_tube(brachial_r, 0.005, n_radial=10)
    meshes.append(MeshData(
        "artery_brachial_r", pos_bar, norm_bar, ind_bar, MAT_ARTERY_RED,
        extras={"structure_id": "brachial_vessels", "name": "Right Brachial & Radial Artery", "system": "Cardiovascular System", "layer": "veins", "exploded_offset": [0.3, 0.0, 0.2]}
    ))

    # Abdominal Aorta & Iliac / Femoral Arteries
    femoral_art_l = [[-0.005, 1.05, -0.01], [-0.025, 0.93, 0.01], [-0.045, 0.86, 0.03], [-0.065, 0.52, 0.03], [-0.055, 0.12, 0.02]]
    pos_fal, norm_fal, ind_fal = create_tube(femoral_art_l, 0.006, n_radial=10)
    meshes.append(MeshData(
        "artery_femoral_l", pos_fal, norm_fal, ind_fal, MAT_ARTERY_RED,
        extras={"structure_id": "femoral_vessels", "name": "Left Femoral Artery", "system": "Cardiovascular System", "layer": "veins", "exploded_offset": [-0.15, -0.1, 0.2]}
    ))
    femoral_art_r = [[0.005, 1.05, -0.01], [0.025, 0.93, 0.01], [0.045, 0.86, 0.03], [0.065, 0.52, 0.03], [0.055, 0.12, 0.02]]
    pos_far, norm_far, ind_far = create_tube(femoral_art_r, 0.006, n_radial=10)
    meshes.append(MeshData(
        "artery_femoral_r", pos_far, norm_far, ind_far, MAT_ARTERY_RED,
        extras={"structure_id": "femoral_vessels", "name": "Right Femoral Artery", "system": "Cardiovascular System", "layer": "veins", "exploded_offset": [0.15, -0.1, 0.2]}
    ))

    # 2. VEINS (Blue)
    # Superior & Inferior Vena Cava
    ivc_path = [[0.015, 0.90, -0.01], [0.015, 1.10, -0.01], [0.012, 1.25, 0.01]]
    pos_ivc, norm_ivc, ind_ivc = create_tube(ivc_path, 0.012, n_radial=12)
    meshes.append(MeshData(
        "vein_inferior_vena_cava", pos_ivc, norm_ivc, ind_ivc, MAT_VEIN_BLUE,
        extras={"structure_id": "vena_cava", "name": "Inferior Vena Cava", "system": "Cardiovascular System", "layer": "veins", "exploded_offset": [0.05, 0.0, 0.25]}
    ))
    svc_path = [[0.015, 1.31, 0.025], [0.015, 1.39, 0.02], [0.01, 1.44, 0.015]]
    pos_svc, norm_svc, ind_svc = create_tube(svc_path, 0.011, n_radial=12)
    meshes.append(MeshData(
        "vein_superior_vena_cava", pos_svc, norm_svc, ind_svc, MAT_VEIN_BLUE,
        extras={"structure_id": "vena_cava", "name": "Superior Vena Cava", "system": "Cardiovascular System", "layer": "veins", "exploded_offset": [0.05, 0.08, 0.25]}
    ))
    
    # Internal Jugular Veins (Left & Right)
    jugular_l = [[-0.02, 1.43, 0.015], [-0.038, 1.50, 0.01], [-0.045, 1.59, 0.01]]
    pos_jl, norm_jl, ind_jl = create_tube(jugular_l, 0.007, n_radial=10)
    meshes.append(MeshData(
        "vein_jugular_l", pos_jl, norm_jl, ind_jl, MAT_VEIN_BLUE,
        extras={"structure_id": "jugular_vein", "name": "Left Internal Jugular Vein", "system": "Cardiovascular System", "layer": "veins", "exploded_offset": [-0.15, 0.1, 0.2]}
    ))
    jugular_r = [[0.02, 1.43, 0.015], [0.038, 1.50, 0.01], [0.045, 1.59, 0.01]]
    pos_jr, norm_jr, ind_jr = create_tube(jugular_r, 0.007, n_radial=10)
    meshes.append(MeshData(
        "vein_jugular_r", pos_jr, norm_jr, ind_jr, MAT_VEIN_BLUE,
        extras={"structure_id": "jugular_vein", "name": "Right Internal Jugular Vein", "system": "Cardiovascular System", "layer": "veins", "exploded_offset": [0.15, 0.1, 0.2]}
    ))

    # Great Saphenous Veins (Superficial lower limb venous return)
    saphenous_l = [[-0.035, 0.86, 0.035], [-0.045, 0.65, 0.03], [-0.048, 0.45, 0.02], [-0.04, 0.12, 0.03]]
    pos_sapl, norm_sapl, ind_sapl = create_tube(saphenous_l, 0.005, n_radial=10)
    meshes.append(MeshData(
        "vein_great_saphenous_l", pos_sapl, norm_sapl, ind_sapl, MAT_VEIN_BLUE,
        extras={"structure_id": "saphenous_vein", "name": "Left Great Saphenous Vein", "system": "Cardiovascular System", "layer": "veins", "exploded_offset": [-0.12, -0.1, 0.25]}
    ))
    saphenous_r = [[0.035, 0.86, 0.035], [0.045, 0.65, 0.03], [0.048, 0.45, 0.02], [0.04, 0.12, 0.03]]
    pos_sapr, norm_sapr, ind_sapr = create_tube(saphenous_r, 0.005, n_radial=10)
    meshes.append(MeshData(
        "vein_great_saphenous_r", pos_sapr, norm_sapr, ind_sapr, MAT_VEIN_BLUE,
        extras={"structure_id": "saphenous_vein", "name": "Right Great Saphenous Vein", "system": "Cardiovascular System", "layer": "veins", "exploded_offset": [0.12, -0.1, 0.25]}
    ))

    return meshes

# -------------------------------------------------------------
# BONES & SKELETON BUILDER (Skeletal System)
# -------------------------------------------------------------
def build_bones(gender="male"):
    meshes = []
    w_pelvis = 0.13 if gender == "male" else 0.15
    
    # 1. CRANIUM & MANDIBLE (Skull)
    pos_sk, norm_sk, ind_sk = create_ellipsoid(0.065, 0.075, 0.08, n_lat=16, n_lon=20, offset=(0.0, 1.66, 0.0))
    meshes.append(MeshData(
        "bone_cranium", pos_sk, norm_sk, ind_sk, MAT_BONE_IVORY,
        extras={"structure_id": "cranium", "name": "Cranium (Skull)", "system": "Skeletal System", "layer": "bones", "exploded_offset": [0.0, 0.25, 0.0]}
    ))
    mandible_path = [[-0.04, 1.57, 0.0], [-0.035, 1.54, 0.04], [0.0, 1.53, 0.06], [0.035, 1.54, 0.04], [0.04, 1.57, 0.0]]
    pos_man, norm_man, ind_man = create_tube(mandible_path, 0.012, n_radial=10)
    meshes.append(MeshData(
        "bone_mandible", pos_man, norm_man, ind_man, MAT_BONE_IVORY,
        extras={"structure_id": "mandible", "name": "Mandible (Lower Jaw)", "system": "Skeletal System", "layer": "bones", "exploded_offset": [0.0, 0.15, 0.15]}
    ))

    # 2. VERTEBRAL COLUMN (Spine)
    spine_path = [
        [0.0, 1.53, -0.02], [0.0, 1.45, -0.03], [0.0, 1.35, -0.04],
        [0.0, 1.22, -0.035], [0.0, 1.08, -0.025], [0.0, 0.94, -0.02], [0.0, 0.85, -0.03]
    ]
    pos_spn, norm_spn, ind_spn = create_tube(spine_path, 0.018, n_radial=12)
    meshes.append(MeshData(
        "bone_vertebral_column", pos_spn, norm_spn, ind_spn, MAT_BONE_IVORY,
        extras={"structure_id": "vertebrae", "name": "Vertebral Column (Spine)", "system": "Skeletal System", "layer": "bones", "exploded_offset": [0.0, 0.0, -0.25]}
    ))

    # 3. STERNUM & RIBCAGE (Thoracic Cage)
    pos_stn, norm_stn, ind_stn = create_cylinder(0.014, 0.01, 0.17, n_radial=12, offset=(0.0, 1.28, 0.065))
    meshes.append(MeshData(
        "bone_sternum", pos_stn, norm_stn, ind_stn, MAT_BONE_IVORY,
        extras={"structure_id": "sternum", "name": "Sternum (Breastbone)", "system": "Skeletal System", "layer": "bones", "exploded_offset": [0.0, 0.05, 0.3]}
    ))
    
    # Rib Arches (4 representative pairs of thoracic ribs)
    rib_levels = [1.36, 1.30, 1.24, 1.18]
    rib_widths = [0.11, 0.13, 0.135, 0.12]
    for i, (ry, rw) in enumerate(zip(rib_levels, rib_widths)):
        # Left Rib
        rib_l = [[0.0, ry - 0.02, -0.035], [-rw, ry - 0.01, -0.01], [-rw * 0.9, ry + 0.01, 0.035], [-0.015, ry, 0.065]]
        pos_rl, norm_rl, ind_rl = create_tube(rib_l, 0.006, n_radial=8)
        meshes.append(MeshData(
            f"bone_rib_l_{i+1}", pos_rl, norm_rl, ind_rl, MAT_BONE_IVORY,
            extras={"structure_id": "ribcage", "name": f"Left Rib {i+1}", "system": "Skeletal System", "layer": "bones", "exploded_offset": [-0.2, 0.0, 0.1]}
        ))
        # Right Rib
        rib_r = [[0.0, ry - 0.02, -0.035], [rw, ry - 0.01, -0.01], [rw * 0.9, ry + 0.01, 0.035], [0.015, ry, 0.065]]
        pos_rr, norm_rr, ind_rr = create_tube(rib_r, 0.006, n_radial=8)
        meshes.append(MeshData(
            f"bone_rib_r_{i+1}", pos_rr, norm_rr, ind_rr, MAT_BONE_IVORY,
            extras={"structure_id": "ribcage", "name": f"Right Rib {i+1}", "system": "Skeletal System", "layer": "bones", "exploded_offset": [0.2, 0.0, 0.1]}
        ))

    # 4. CLAVICLES & SCAPULAE (Shoulder Girdle)
    pos_clavl, norm_clavl, ind_clavl = create_cylinder(0.008, 0.008, 0.13, n_radial=10, offset=(-0.08, 1.43, 0.04))
    meshes.append(MeshData(
        "bone_clavicle_l", pos_clavl, norm_clavl, ind_clavl, MAT_BONE_IVORY,
        extras={"structure_id": "clavicle", "name": "Left Clavicle (Collarbone)", "system": "Skeletal System", "layer": "bones", "exploded_offset": [-0.15, 0.1, 0.2]}
    ))
    pos_clavr, norm_clavr, ind_clavr = create_cylinder(0.008, 0.008, 0.13, n_radial=10, offset=(0.08, 1.43, 0.04))
    meshes.append(MeshData(
        "bone_clavicle_r", pos_clavr, norm_clavr, ind_clavr, MAT_BONE_IVORY,
        extras={"structure_id": "clavicle", "name": "Right Clavicle (Collarbone)", "system": "Skeletal System", "layer": "bones", "exploded_offset": [0.15, 0.1, 0.2]}
    ))

    # 5. PELVIS (Pelvic Girdle & Ilium)
    pos_pel, norm_pel, ind_pel = create_ellipsoid(w_pelvis, 0.08, 0.065, n_lat=14, n_lon=18, offset=(0.0, 0.90, -0.01))
    meshes.append(MeshData(
        "bone_pelvis", pos_pel, norm_pel, ind_pel, MAT_BONE_IVORY,
        extras={"structure_id": "pelvis", "name": "Pelvis (Pelvic Girdle)", "system": "Skeletal System", "layer": "bones", "exploded_offset": [0.0, -0.15, -0.1]}
    ))

    # 6. LIMB BONES
    # Humerus Left & Right
    pos_huml, norm_huml, ind_huml = create_cylinder(0.014, 0.013, 0.22, n_radial=12, offset=(-0.19, 1.25, 0.0))
    meshes.append(MeshData(
        "bone_humerus_l", pos_huml, norm_huml, ind_huml, MAT_BONE_IVORY,
        extras={"structure_id": "humerus", "name": "Left Humerus", "system": "Skeletal System", "layer": "bones", "exploded_offset": [-0.3, 0.0, 0.0]}
    ))
    pos_humr, norm_humr, ind_humr = create_cylinder(0.014, 0.013, 0.22, n_radial=12, offset=(0.19, 1.25, 0.0))
    meshes.append(MeshData(
        "bone_humerus_r", pos_humr, norm_humr, ind_humr, MAT_BONE_IVORY,
        extras={"structure_id": "humerus", "name": "Right Humerus", "system": "Skeletal System", "layer": "bones", "exploded_offset": [0.3, 0.0, 0.0]}
    ))

    # Radius & Ulna Left & Right
    pos_radl, norm_radl, ind_radl = create_cylinder(0.011, 0.01, 0.20, n_radial=10, offset=(-0.24, 1.03, 0.01))
    meshes.append(MeshData(
        "bone_radius_ulna_l", pos_radl, norm_radl, ind_radl, MAT_BONE_IVORY,
        extras={"structure_id": "radius_ulna", "name": "Left Radius & Ulna", "system": "Skeletal System", "layer": "bones", "exploded_offset": [-0.35, -0.05, 0.0]}
    ))
    pos_radr, norm_radr, ind_radr = create_cylinder(0.011, 0.01, 0.20, n_radial=10, offset=(0.24, 1.03, 0.01))
    meshes.append(MeshData(
        "bone_radius_ulna_r", pos_radr, norm_radr, ind_radr, MAT_BONE_IVORY,
        extras={"structure_id": "radius_ulna", "name": "Right Radius & Ulna", "system": "Skeletal System", "layer": "bones", "exploded_offset": [0.35, -0.05, 0.0]}
    ))

    # Femur Left & Right (Thigh bone)
    pos_feml, norm_feml, ind_feml = create_cylinder(0.018, 0.016, 0.38, n_radial=12, offset=(-0.085, 0.69, 0.01))
    meshes.append(MeshData(
        "bone_femur_l", pos_feml, norm_feml, ind_feml, MAT_BONE_IVORY,
        extras={"structure_id": "femur", "name": "Left Femur (Thigh Bone)", "system": "Skeletal System", "layer": "bones", "exploded_offset": [-0.2, -0.1, 0.0]}
    ))
    pos_femr, norm_femr, ind_femr = create_cylinder(0.018, 0.016, 0.38, n_radial=12, offset=(0.085, 0.69, 0.01))
    meshes.append(MeshData(
        "bone_femur_r", pos_femr, norm_femr, ind_femr, MAT_BONE_IVORY,
        extras={"structure_id": "femur", "name": "Right Femur (Thigh Bone)", "system": "Skeletal System", "layer": "bones", "exploded_offset": [0.2, -0.1, 0.0]}
    ))

    # Patella Left & Right (Kneecap)
    pos_patl, norm_patl, ind_patl = create_ellipsoid(0.018, 0.022, 0.01, n_lat=10, n_lon=14, offset=(-0.08, 0.50, 0.045))
    meshes.append(MeshData(
        "bone_patella_l", pos_patl, norm_patl, ind_patl, MAT_BONE_IVORY,
        extras={"structure_id": "patella", "name": "Left Patella (Kneecap)", "system": "Skeletal System", "layer": "bones", "exploded_offset": [-0.15, -0.1, 0.2]}
    ))
    pos_patr, norm_patr, ind_patr = create_ellipsoid(0.018, 0.022, 0.01, n_lat=10, n_lon=14, offset=(0.08, 0.50, 0.045))
    meshes.append(MeshData(
        "bone_patella_r", pos_patr, norm_patr, ind_patr, MAT_BONE_IVORY,
        extras={"structure_id": "patella", "name": "Right Patella (Kneecap)", "system": "Skeletal System", "layer": "bones", "exploded_offset": [0.15, -0.1, 0.2]}
    ))

    # Tibia & Fibula Left & Right
    pos_tibl, norm_tibl, ind_tibl = create_cylinder(0.016, 0.014, 0.38, n_radial=12, offset=(-0.075, 0.29, 0.0))
    meshes.append(MeshData(
        "bone_tibia_l", pos_tibl, norm_tibl, ind_tibl, MAT_BONE_IVORY,
        extras={"structure_id": "tibia", "name": "Left Tibia & Fibula (Shin Bone)", "system": "Skeletal System", "layer": "bones", "exploded_offset": [-0.18, -0.15, 0.0]}
    ))
    pos_tibr, norm_tibr, ind_tibr = create_cylinder(0.016, 0.014, 0.38, n_radial=12, offset=(0.075, 0.29, 0.0))
    meshes.append(MeshData(
        "bone_tibia_r", pos_tibr, norm_tibr, ind_tibr, MAT_BONE_IVORY,
        extras={"structure_id": "tibia", "name": "Right Tibia & Fibula (Shin Bone)", "system": "Skeletal System", "layer": "bones", "exploded_offset": [0.18, -0.15, 0.0]}
    ))

    return meshes

# -------------------------------------------------------------
# SKIN ENVELOPE BUILDER (Integumentary System)
# -------------------------------------------------------------
def build_skin(gender="male"):
    meshes = []
    # Semi-transparent body envelope
    w_torso = 0.17 if gender == "male" else 0.15
    w_hips = 0.15 if gender == "male" else 0.17
    
    # Head & Neck skin
    pos_sh, norm_sh, ind_sh = create_ellipsoid(0.085, 0.11, 0.095, n_lat=16, n_lon=22, offset=(0.0, 1.63, 0.01))
    meshes.append(MeshData(
        "skin_head", pos_sh, norm_sh, ind_sh, MAT_SKIN_TRANSLUCENT,
        extras={"structure_id": "integumentary", "name": "Cranial & Facial Skin", "system": "Integumentary System", "layer": "skin", "exploded_offset": [0.0, 0.35, 0.0]}
    ))
    # Torso skin
    pos_st, norm_st, ind_st = create_ellipsoid(w_torso, 0.26, 0.10, n_lat=18, n_lon=24, offset=(0.0, 1.22, 0.01))
    meshes.append(MeshData(
        "skin_torso", pos_st, norm_st, ind_st, MAT_SKIN_TRANSLUCENT,
        extras={"structure_id": "integumentary", "name": "Thoracic & Abdominal Skin", "system": "Integumentary System", "layer": "skin", "exploded_offset": [0.0, 0.1, 0.35]}
    ))
    # Pelvis skin
    pos_sp, norm_sp, ind_sp = create_ellipsoid(w_hips, 0.12, 0.09, n_lat=16, n_lon=20, offset=(0.0, 0.90, 0.0))
    meshes.append(MeshData(
        "skin_pelvis", pos_sp, norm_sp, ind_sp, MAT_SKIN_TRANSLUCENT,
        extras={"structure_id": "integumentary", "name": "Pelvic Integument", "system": "Integumentary System", "layer": "skin", "exploded_offset": [0.0, -0.15, 0.3]}
    ))
    
    return meshes
