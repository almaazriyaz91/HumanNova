"""
HumanNova Blender Native Anatomical 3D Model Generator
Run directly inside Blender (Scripting tab or `blender --background --python blender_anatomy_generator.py`).
Creates collections for Bones, Muscles, Veins, Organs, and Skin, builds procedural anatomical meshes,
assigns Principled BSDF materials, and exports to standard GLTF/GLB formats.
"""

import math
import os

try:
    import bpy
    import bmesh
    HAS_BPY = True
except ImportError:
    HAS_BPY = False

def create_blender_material(name, color, roughness=0.4, metallic=0.05, alpha=1.0):
    if not HAS_BPY:
        return None
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
        if alpha < 1.0:
            mat.blend_method = 'BLEND'
            bsdf.inputs['Alpha'].default_value = alpha
    return mat

def create_blender_scene(gender="male"):
    if not HAS_BPY:
        print("Note: bpy module only available when running within Blender environment.")
        print("For standalone python generation, use generator/generate_anatomy_models.py.")
        return

    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Materials
    mat_muscle = create_blender_material("Muscle_Crimson", (0.68, 0.17, 0.14, 1.0), roughness=0.5)
    mat_tendon = create_blender_material("Tendon_Pearl", (0.94, 0.92, 0.88, 1.0), roughness=0.35)
    mat_bone = create_blender_material("Bone_Ivory", (0.91, 0.88, 0.80, 1.0), roughness=0.6)
    mat_artery = create_blender_material("Artery_Red", (0.85, 0.12, 0.12, 1.0), roughness=0.3)
    mat_vein = create_blender_material("Vein_Blue", (0.12, 0.45, 0.88, 1.0), roughness=0.3)
    mat_heart = create_blender_material("Organ_Heart", (0.72, 0.08, 0.18, 1.0), roughness=0.4)
    mat_lung = create_blender_material("Organ_Lung", (0.88, 0.45, 0.42, 1.0), roughness=0.6)
    mat_liver = create_blender_material("Organ_Liver", (0.46, 0.14, 0.18, 1.0), roughness=0.45)
    mat_brain = create_blender_material("Organ_Brain", (0.92, 0.68, 0.72, 1.0), roughness=0.55)
    mat_uterus = create_blender_material("Organ_Uterus", (0.96, 0.48, 0.62, 1.0), roughness=0.4)
    mat_skin = create_blender_material("Skin_Translucent", (0.92, 0.78, 0.70, 0.25), roughness=0.4, alpha=0.25)

    collections = {
        "Bones": bpy.data.collections.new("Bones"),
        "Muscles": bpy.data.collections.new("Muscles"),
        "Veins": bpy.data.collections.new("Veins"),
        "Organs": bpy.data.collections.new("Organs"),
        "Skin": bpy.data.collections.new("Skin")
    }
    for c in collections.values():
        bpy.context.scene.collection.children.link(c)

    def add_mesh_obj(name, col_name, mat, prim_type="uv_sphere", location=(0,0,0), scale=(1,1,1)):
        col = collections[col_name]
        if prim_type == "uv_sphere":
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=location)
        elif prim_type == "cylinder":
            bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=1.0, location=location)
        
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = scale
        if mat:
            obj.data.materials.append(mat)
            
        # Move to correct collection
        for c in obj.users_collection:
            c.objects.unlink(obj)
        col.objects.link(obj)
        
        # Add smooth shading and subdivision
        bpy.ops.object.shade_smooth()
        mod = obj.modifiers.new(name="Subsurf", type='SUBSURF')
        mod.levels = 1
        return obj

    # 1. ORGANS
    add_mesh_obj("organ_brain_hemisphere_l", "Organs", mat_brain, location=(-0.024, 0.01, 1.66), scale=(0.045, 0.065, 0.055))
    add_mesh_obj("organ_brain_hemisphere_r", "Organs", mat_brain, location=(0.024, 0.01, 1.66), scale=(0.045, 0.065, 0.055))
    add_mesh_obj("organ_heart", "Organs", mat_heart, location=(-0.025, 0.045, 1.28), scale=(0.045, 0.04, 0.055))
    add_mesh_obj("organ_lung_left", "Organs", mat_lung, location=(-0.085, 0.02, 1.29), scale=(0.048, 0.055, 0.09))
    add_mesh_obj("organ_lung_right", "Organs", mat_lung, location=(0.085, 0.02, 1.29), scale=(0.054, 0.06, 0.095))
    add_mesh_obj("organ_liver", "Organs", mat_liver, location=(0.05, 0.04, 1.16), scale=(0.095, 0.065, 0.06))
    add_mesh_obj("organ_stomach", "Organs", mat_liver, location=(-0.05, 0.04, 1.14), scale=(0.06, 0.045, 0.05))

    if gender == "female":
        add_mesh_obj("organ_uterus", "Organs", mat_uterus, location=(0.0, 0.025, 0.91), scale=(0.022, 0.018, 0.032))
        add_mesh_obj("female_breast_l", "Muscles", mat_muscle, location=(-0.095, 0.11, 1.28), scale=(0.052, 0.045, 0.052))
        add_mesh_obj("female_breast_r", "Muscles", mat_muscle, location=(0.095, 0.11, 1.28), scale=(0.052, 0.045, 0.052))

    # 2. MUSCLES
    add_mesh_obj("muscle_pectoralis_major_l", "Muscles", mat_muscle, location=(-0.09, 0.06, 1.35), scale=(0.07, 0.035, 0.055))
    add_mesh_obj("muscle_pectoralis_major_r", "Muscles", mat_muscle, location=(0.09, 0.06, 1.35), scale=(0.07, 0.035, 0.055))
    add_mesh_obj("muscle_deltoid_l", "Muscles", mat_muscle, location=(-0.20, 0.0, 1.38), scale=(0.045, 0.045, 0.07))
    add_mesh_obj("muscle_deltoid_r", "Muscles", mat_muscle, location=(0.20, 0.0, 1.38), scale=(0.045, 0.045, 0.07))
    add_mesh_obj("muscle_biceps_brachii_l", "Muscles", mat_muscle, location=(-0.22, 0.01, 1.24), scale=(0.032, 0.028, 0.09))
    add_mesh_obj("muscle_biceps_brachii_r", "Muscles", mat_muscle, location=(0.22, 0.01, 1.24), scale=(0.032, 0.028, 0.09))
    add_mesh_obj("muscle_rectus_femoris_l", "Muscles", mat_muscle, location=(-0.085, 0.04, 0.71), scale=(0.04, 0.035, 0.17))
    add_mesh_obj("muscle_rectus_femoris_r", "Muscles", mat_muscle, location=(0.085, 0.04, 0.71), scale=(0.04, 0.035, 0.17))
    add_mesh_obj("tendon_patellar_l", "Muscles", mat_tendon, location=(-0.075, 0.05, 0.47), scale=(0.015, 0.012, 0.06))
    add_mesh_obj("tendon_patellar_r", "Muscles", mat_tendon, location=(0.075, 0.05, 0.47), scale=(0.015, 0.012, 0.06))

    # 3. BONES
    add_mesh_obj("bone_cranium", "Bones", mat_bone, location=(0.0, 0.0, 1.66), scale=(0.065, 0.08, 0.075))
    add_mesh_obj("bone_vertebral_column", "Bones", mat_bone, location=(0.0, -0.03, 1.20), scale=(0.02, 0.02, 0.35))
    add_mesh_obj("bone_pelvis", "Bones", mat_bone, location=(0.0, -0.01, 0.90), scale=(0.14, 0.065, 0.08))

    # 4. SKIN
    add_mesh_obj("skin_envelope", "Skin", mat_skin, location=(0.0, 0.0, 1.25), scale=(0.18, 0.12, 0.50))

    print(f"Blender scene populated for {gender} anatomy.")

def export_blender_glb(filepath):
    if not HAS_BPY:
        return
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format='GLB',
        use_selection=False,
        export_apply=True,
        export_materials='EXPORT',
        export_extras=True
    )
    print(f"Exported Blender GLB to {filepath}")

if __name__ == '__main__':
    if HAS_BPY:
        create_blender_scene("male")
        export_blender_glb("male_blender_export.glb")
    else:
        print("HumanNova Blender Generator loaded in standalone environment.")
