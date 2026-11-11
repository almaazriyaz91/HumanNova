"""
HumanNova 3D Geometry Utilities — Realistic Anatomical Engine
High-precision procedural mesh generators with smooth normals, UV mapping,
and binary glTF 2.0 packing with embedded PBR textures.
"""

import io
import json
import struct
import numpy as np

class MeshData:
    def __init__(self, name, positions, normals, indices, texcoords=None, material_idx=0, extras=None):
        self.name = name
        self.positions = np.array(positions, dtype=np.float32)
        self.normals = np.array(normals, dtype=np.float32)
        if texcoords is not None:
            self.texcoords = np.array(texcoords, dtype=np.float32)
        else:
            # Default spherical UV mapping
            p = self.positions
            u = 0.5 + np.arctan2(p[:, 2], p[:, 0]) / (2 * np.pi)
            v = 0.5 - np.arcsin(np.clip(p[:, 1] / np.maximum(np.linalg.norm(p, axis=1), 1e-5), -1.0, 1.0)) / np.pi
            self.texcoords = np.stack([u, v], axis=-1).astype(np.float32)

        self.indices = np.array(indices, dtype=np.uint32 if len(positions) > 65535 else np.uint16)
        self.material_idx = material_idx
        self.extras = extras or {}

def compute_smooth_normals(positions, indices):
    """Compute area-weighted vertex normals for a triangle mesh."""
    pos = np.array(positions, dtype=np.float32)
    ind = np.array(indices, dtype=np.int32).reshape(-1, 3)
    
    normals = np.zeros_like(pos)
    v0 = pos[ind[:, 0]]
    v1 = pos[ind[:, 1]]
    v2 = pos[ind[:, 2]]
    
    face_normals = np.cross(v1 - v0, v2 - v0)
    for i in range(3):
        np.add.at(normals, ind[:, i], face_normals)
        
    lens = np.linalg.norm(normals, axis=1, keepdims=True)
    normals = normals / np.maximum(lens, 1e-6)
    return normals

def create_ellipsoid(rx, ry, rz, n_lat=24, n_lon=32, offset=(0, 0, 0), deform_fn=None):
    """Generate a high-density ellipsoid with smooth UV mapping and optional anatomical deformer."""
    lat_angles = np.linspace(-np.pi / 2, np.pi / 2, n_lat)
    lon_angles = np.linspace(0, 2 * np.pi, n_lon, endpoint=True)
    
    positions = []
    texcoords = []
    
    for i, lat in enumerate(lat_angles):
        cos_lat = np.cos(lat)
        sin_lat = np.sin(lat)
        v = (lat + np.pi / 2) / np.pi
        for j, lon in enumerate(lon_angles):
            cos_lon = np.cos(lon)
            sin_lon = np.sin(lon)
            u = lon / (2 * np.pi)
            
            x = rx * cos_lat * cos_lon
            y = ry * sin_lat
            z = rz * cos_lat * sin_lon
            
            if deform_fn:
                x, y, z = deform_fn(x, y, z, lat, lon)
                
            positions.append([x + offset[0], y + offset[1], z + offset[2]])
            texcoords.append([u, v])
            
    indices = []
    for i in range(n_lat - 1):
        for j in range(n_lon - 1):
            p0 = i * n_lon + j
            p1 = i * n_lon + (j + 1)
            p2 = (i + 1) * n_lon + (j + 1)
            p3 = (i + 1) * n_lon + j
            indices.extend([p0, p1, p2, p0, p2, p3])
            
    positions = np.array(positions, dtype=np.float32)
    indices = np.array(indices, dtype=np.uint32)
    normals = compute_smooth_normals(positions, indices)
    return positions, normals, np.array(texcoords, dtype=np.float32), indices

def create_sculpted_tube(path_points, radii_list, n_radial=20, close_ends=True, longitudinal_uv=True):
    """
    Sweeps a circular/elliptical cross-section along a 3D path with per-segment radii and longitudinal UVs.
    """
    path = np.array(path_points, dtype=np.float32)
    n_pts = len(path)
    if np.isscalar(radii_list):
        r_list = [radii_list] * n_pts
    else:
        r_list = radii_list
        
    positions = []
    texcoords = []
    angles = np.linspace(0, 2 * np.pi, n_radial, endpoint=True)
    
    # Compute Frenet tangent frames
    tangents = []
    for i in range(n_pts):
        if i == 0:
            t = path[1] - path[0]
        elif i == n_pts - 1:
            t = path[-1] - path[-2]
        else:
            t = path[i+1] - path[i-1]
        lens = np.linalg.norm(t)
        tangents.append(t / max(lens, 1e-6))
        
    t0 = tangents[0]
    up = np.array([0, 1, 0], dtype=np.float32)
    if abs(np.dot(t0, up)) > 0.9:
        up = np.array([1, 0, 0], dtype=np.float32)
    n0 = np.cross(t0, up)
    n0 /= np.linalg.norm(n0)
    b0 = np.cross(t0, n0)
    
    normals_frame = [n0]
    binormals_frame = [b0]
    
    for i in range(1, n_pts):
        t_prev = tangents[i-1]
        t_curr = tangents[i]
        axis = np.cross(t_prev, t_curr)
        axis_len = np.linalg.norm(axis)
        if axis_len > 1e-5:
            axis /= axis_len
            angle = np.arccos(np.clip(np.dot(t_prev, t_curr), -1.0, 1.0))
            v = normals_frame[-1]
            n_next = v * np.cos(angle) + np.cross(axis, v) * np.sin(angle) + axis * np.dot(axis, v) * (1 - np.cos(angle))
            n_next /= np.linalg.norm(n_next)
        else:
            n_next = normals_frame[-1]
        b_next = np.cross(t_curr, n_next)
        b_next /= np.linalg.norm(b_next)
        normals_frame.append(n_next)
        binormals_frame.append(b_next)
        
    for i in range(n_pts):
        c = path[i]
        r = r_list[i]
        # Support elliptical cross-section (rx, rz)
        if hasattr(r, '__len__'):
            rx, rz = r[0], r[1]
        else:
            rx, rz = r, r
            
        n = normals_frame[i]
        b = binormals_frame[i]
        v = i / (n_pts - 1)
        
        for j, ang in enumerate(angles):
            u = j / (n_radial - 1)
            cos_a = np.cos(ang)
            sin_a = np.sin(ang)
            pt = c + rx * cos_a * n + rz * sin_a * b
            positions.append(pt)
            texcoords.append([u, v])
            
    indices = []
    for i in range(n_pts - 1):
        for j in range(n_radial - 1):
            p0 = i * n_radial + j
            p1 = i * n_radial + (j + 1)
            p2 = (i + 1) * n_radial + (j + 1)
            p3 = (i + 1) * n_radial + j
            indices.extend([p0, p1, p2, p0, p2, p3])
            
    if close_ends:
        # Start cap
        sc_idx = len(positions)
        positions.append(path[0])
        texcoords.append([0.5, 0.0])
        for j in range(n_radial - 1):
            indices.extend([sc_idx, j + 1, j])
            
        # End cap
        ec_idx = len(positions)
        positions.append(path[-1])
        texcoords.append([0.5, 1.0])
        end_start = (n_pts - 1) * n_radial
        for j in range(n_radial - 1):
            indices.extend([ec_idx, end_start + j, end_start + j + 1])
            
    positions = np.array(positions, dtype=np.float32)
    indices = np.array(indices, dtype=np.uint32)
    normals = compute_smooth_normals(positions, indices)
    return positions, normals, np.array(texcoords, dtype=np.float32), indices

def create_muscle_belly(p_origin, p_insertion, belly_radii=(0.045, 0.035), tendon_ratio=0.18, n_radial=20, n_sections=16, curve_bend=(0, 0, 0)):
    """
    Generates an anatomically sculpted muscle with realistic spindle shape (fusiform or bipennate),
    tapered tendon origin/insertion, natural belly bulge, and aligned muscle fiber UVs.
    """
    p0 = np.array(p_origin, dtype=np.float32)
    p1 = np.array(p_insertion, dtype=np.float32)
    t_vals = np.linspace(0, 1, n_sections)
    
    path = []
    radii_list = []
    rx, rz = belly_radii
    bend = np.array(curve_bend, dtype=np.float32)
    
    for t in t_vals:
        # Parabolic anatomical belly curvature
        pt = (1 - t) * p0 + t * p1 + 4.0 * t * (1 - t) * bend
        path.append(pt)
        
        # Fusiform muscle profile: narrow at tendons, bulging at belly center
        if t < tendon_ratio:
            scale = 0.22 + 0.78 * (t / tendon_ratio)
        elif t > (1.0 - tendon_ratio):
            scale = 0.22 + 0.78 * ((1.0 - t) / tendon_ratio)
        else:
            mid_t = (t - tendon_ratio) / (1.0 - 2.0 * tendon_ratio)
            scale = 1.0 + 0.20 * np.sin(mid_t * np.pi)
            
        radii_list.append([rx * scale, rz * scale])
        
    return create_sculpted_tube(path, radii_list, n_radial=n_radial, close_ends=True)

def save_glb_with_textures(meshes, materials, textures_dict, output_path):
    """
    Packs meshes, materials, and embedded PNG textures (diffuse, normal) into a binary glTF 2.0 (.glb) file.
    """
    if textures_dict is None:
        textures_dict = {}

    bin_chunks = []
    accessors = []
    buffer_views = []
    nodes = []
    gltf_meshes = []
    gltf_images = []
    gltf_textures = []
    
    curr_byte_offset = 0
    
    def pad4(data, pad_char=b'\x00'):
        rem = len(data) % 4
        return data + pad_char * (4 - rem) if rem else data

    # 1. PACK TEXTURE IMAGES FIRST
    tex_indices = {}
    for tex_key, pil_img in textures_dict.items():
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG", optimize=True)
        img_bytes = buf.getvalue()
        img_len = len(img_bytes)
        
        bv_idx = len(buffer_views)
        buffer_views.append({
            "buffer": 0,
            "byteOffset": curr_byte_offset,
            "byteLength": img_len
        })
        curr_byte_offset += len(pad4(img_bytes))
        bin_chunks.append(pad4(img_bytes))
        
        img_idx = len(gltf_images)
        gltf_images.append({
            "bufferView": bv_idx,
            "mimeType": "image/png"
        })
        
        t_idx = len(gltf_textures)
        gltf_textures.append({
            "sampler": 0,
            "source": img_idx
        })
        tex_indices[tex_key] = t_idx

    # Update materials with texture references
    gltf_materials = []
    for mat in materials:
        m_copy = json.loads(json.dumps(mat))
        m_name = m_copy.get("name", "")
        
        if "Muscle" in m_name:
            if "tex_muscle" in tex_indices:
                m_copy["pbrMetallicRoughness"]["baseColorTexture"] = {"index": tex_indices["tex_muscle"]}
            if "norm_muscle" in tex_indices:
                m_copy["normalTexture"] = {"index": tex_indices["norm_muscle"], "scale": 1.2}
        elif "Tendon" in m_name:
            if "tex_tendon" in tex_indices:
                m_copy["pbrMetallicRoughness"]["baseColorTexture"] = {"index": tex_indices["tex_tendon"]}
        elif "Bone" in m_name:
            if "tex_bone" in tex_indices:
                m_copy["pbrMetallicRoughness"]["baseColorTexture"] = {"index": tex_indices["tex_bone"]}
        elif "Brain" in m_name:
            if "tex_brain" in tex_indices:
                m_copy["pbrMetallicRoughness"]["baseColorTexture"] = {"index": tex_indices["tex_brain"]}
        elif "Organ" in m_name:
            if "tex_organ" in tex_indices:
                m_copy["pbrMetallicRoughness"]["baseColorTexture"] = {"index": tex_indices["tex_organ"]}
                
        gltf_materials.append(m_copy)

    # 2. PACK MESH GEOMETRIES
    for i, m in enumerate(meshes):
        # Positions
        pos_bytes = m.positions.tobytes()
        pos_min = m.positions.min(axis=0).tolist()
        pos_max = m.positions.max(axis=0).tolist()
        bv_pos_idx = len(buffer_views)
        buffer_views.append({
            "buffer": 0,
            "byteOffset": curr_byte_offset,
            "byteLength": len(pos_bytes),
            "target": 34962
        })
        curr_byte_offset += len(pad4(pos_bytes))
        bin_chunks.append(pad4(pos_bytes))
        
        # Normals
        norm_bytes = m.normals.tobytes()
        norm_min = m.normals.min(axis=0).tolist()
        norm_max = m.normals.max(axis=0).tolist()
        bv_norm_idx = len(buffer_views)
        buffer_views.append({
            "buffer": 0,
            "byteOffset": curr_byte_offset,
            "byteLength": len(norm_bytes),
            "target": 34962
        })
        curr_byte_offset += len(pad4(norm_bytes))
        bin_chunks.append(pad4(norm_bytes))

        # Texcoords
        uv_bytes = m.texcoords.tobytes()
        uv_min = m.texcoords.min(axis=0).tolist()
        uv_max = m.texcoords.max(axis=0).tolist()
        bv_uv_idx = len(buffer_views)
        buffer_views.append({
            "buffer": 0,
            "byteOffset": curr_byte_offset,
            "byteLength": len(uv_bytes),
            "target": 34962
        })
        curr_byte_offset += len(pad4(uv_bytes))
        bin_chunks.append(pad4(uv_bytes))
        
        # Indices
        ind_bytes = m.indices.tobytes()
        ind_min = [int(m.indices.min())]
        ind_max = [int(m.indices.max())]
        ind_comp_type = 5125 if m.indices.dtype == np.uint32 else 5123
        bv_ind_idx = len(buffer_views)
        buffer_views.append({
            "buffer": 0,
            "byteOffset": curr_byte_offset,
            "byteLength": len(ind_bytes),
            "target": 34963
        })
        curr_byte_offset += len(pad4(ind_bytes))
        bin_chunks.append(pad4(ind_bytes))
        
        # Accessors
        acc_pos = len(accessors)
        accessors.append({"bufferView": bv_pos_idx, "byteOffset": 0, "componentType": 5126, "count": len(m.positions), "type": "VEC3", "min": pos_min, "max": pos_max})
        
        acc_norm = len(accessors)
        accessors.append({"bufferView": bv_norm_idx, "byteOffset": 0, "componentType": 5126, "count": len(m.normals), "type": "VEC3", "min": norm_min, "max": norm_max})

        acc_uv = len(accessors)
        accessors.append({"bufferView": bv_uv_idx, "byteOffset": 0, "componentType": 5126, "count": len(m.texcoords), "type": "VEC2", "min": uv_min, "max": uv_max})

        acc_ind = len(accessors)
        accessors.append({"bufferView": bv_ind_idx, "byteOffset": 0, "componentType": ind_comp_type, "count": len(m.indices), "type": "SCALAR", "min": ind_min, "max": ind_max})
        
        # Mesh
        mesh_idx = len(gltf_meshes)
        gltf_meshes.append({
            "name": m.name,
            "primitives": [{
                "attributes": {
                    "POSITION": acc_pos,
                    "NORMAL": acc_norm,
                    "TEXCOORD_0": acc_uv
                },
                "indices": acc_ind,
                "material": m.material_idx
            }]
        })
        
        node_def = {"name": m.name, "mesh": mesh_idx}
        if m.extras:
            node_def["extras"] = m.extras
        nodes.append(node_def)
        
    full_bin = b"".join(bin_chunks)
    
    gltf_dict = {
        "asset": {
            "version": "2.0",
            "generator": "HumanNova Realistic 3D Anatomy Engine"
        },
        "scene": 0,
        "scenes": [{
            "name": "HumanNova Anatomical Atlas",
            "nodes": list(range(len(nodes)))
        }],
        "nodes": nodes,
        "meshes": gltf_meshes,
        "materials": gltf_materials,
        "textures": gltf_textures,
        "images": gltf_images,
        "samplers": [{
            "magFilter": 9729, # LINEAR
            "minFilter": 9987, # LINEAR_MIPMAP_LINEAR
            "wrapS": 10497,    # REPEAT
            "wrapT": 10497     # REPEAT
        }],
        "accessors": accessors,
        "bufferViews": buffer_views,
        "buffers": [{"byteLength": len(full_bin)}]
    }
    
    json_bytes = json.dumps(gltf_dict, separators=(',', ':')).encode('utf-8')
    rem_j = len(json_bytes) % 4
    if rem_j != 0:
        json_bytes += b' ' * (4 - rem_j)
        
    total_length = 12 + 8 + len(json_bytes) + 8 + len(full_bin)
    
    header = struct.pack('<4sII', b'glTF', 2, total_length)
    chunk0_hdr = struct.pack('<I4s', len(json_bytes), b'JSON')
    chunk1_hdr = struct.pack('<I4s', len(full_bin), b'BIN\x00')
    
    with open(output_path, 'wb') as f:
        f.write(header)
        f.write(chunk0_hdr)
        f.write(json_bytes)
        f.write(chunk1_hdr)
        f.write(full_bin)
        
    print(f"Generated realistic GLB: {output_path} ({len(meshes)} meshes, {total_length/1024:.1f} KB)")

def save_glb_scene(meshes, materials, output_path, textures_dict=None):
    """Convenience wrapper for save_glb_with_textures."""
    return save_glb_with_textures(meshes, materials, textures_dict, output_path)

