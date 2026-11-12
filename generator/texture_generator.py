"""
HumanNova Ultra-Realistic PBR Texture Generator — v2.0
Generates 1024×1024 medically authentic procedural textures:
  - Diffuse maps with detailed tissue-specific patterns
  - Normal maps with deep, anatomically correct surface detail
  - Occlusion/Roughness/Metallic (ORM) packed maps
Tissue types: muscle, bone, organ visceral, brain, vessel wall, tendon
"""

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# ---------------------------------------------------------------------------
# UTILITY
# ---------------------------------------------------------------------------

def _fbm(x_arr, y_arr, octaves=6, persistence=0.5, lacunarity=2.0, base_freq=1.0):
    """Approximate fractal Brownian motion using summed sine/cosine harmonics."""
    total = np.zeros_like(x_arr, dtype=np.float32)
    amp = 1.0
    freq = base_freq
    max_val = 0.0
    for _ in range(octaves):
        total += amp * (
            np.sin(freq * x_arr * 2 * math.pi) *
            np.cos(freq * y_arr * 2 * math.pi + 0.37) +
            0.5 * np.cos(freq * (x_arr + y_arr) * 2 * math.pi + 1.1)
        )
        max_val += amp
        amp *= persistence
        freq *= lacunarity
    return total / max_val   # range roughly [-1, 1]


def _height_to_normal(hmap, strength=5.0):
    """Convert a float32 height map (H,W) to an RGBA normal-map image."""
    dy, dx = np.gradient(hmap)
    nx = -dx * strength
    ny = -dy * strength
    nz = np.ones_like(nx)
    nlen = np.sqrt(nx*nx + ny*ny + nz*nz)
    nx /= nlen; ny /= nlen; nz /= nlen
    r = ((nx * 0.5 + 0.5) * 255).clip(0, 255).astype(np.uint8)
    g = ((ny * 0.5 + 0.5) * 255).clip(0, 255).astype(np.uint8)
    b = ((nz * 0.5 + 0.5) * 255).clip(0, 255).astype(np.uint8)
    a = np.full_like(r, 255)
    return Image.fromarray(np.stack([r, g, b, a], axis=-1), "RGBA")


def _make_grid(width, height):
    xs = np.linspace(0.0, 1.0, width, dtype=np.float32)
    ys = np.linspace(0.0, 1.0, height, dtype=np.float32)
    X, Y = np.meshgrid(xs, ys)
    return X, Y


# ---------------------------------------------------------------------------
# 1. MUSCLE — deep striated fibers + endomysium threads
# ---------------------------------------------------------------------------

def create_muscle_striation_texture(width=1024, height=1024):
    """
    Deep fiber striations (longitudinal + cross-striations), dark crimson with
    endomysium white threads and micro-noise.
    """
    X, Y = _make_grid(width, height)
    np.random.seed(42)

    # Primary longitudinal fibers (along Y axis)
    fiber_freq = 48.0
    fiber_wave = np.sin(Y * fiber_freq * 2 * math.pi) * 0.5 + \
                 np.sin(Y * fiber_freq * 1.3 * 2 * math.pi + 0.5) * 0.25
    # Cross-striations (along X, narrower)
    cross_wave  = np.sin(X * 180 * 2 * math.pi) * 0.12

    # Fractal noise for organic variation
    noise = _fbm(X, Y, octaves=5, persistence=0.55, lacunarity=2.1, base_freq=2.5)

    combined = (fiber_wave + cross_wave + noise * 0.35)
    combined = (combined - combined.min()) / (combined.max() - combined.min())

    # Base color: deep crimson (#941c18)  to dark-red highlights
    r_base, g_base, b_base = 148, 28, 24
    r_high, g_high, b_high = 210, 55, 42

    r = (r_base + combined * (r_high - r_base)).clip(0, 255).astype(np.uint8)
    g = (g_base + combined * (g_high - g_base)).clip(0, 255).astype(np.uint8)
    b = (b_base + combined * (b_high - b_base)).clip(0, 255).astype(np.uint8)
    a = np.full((height, width), 255, dtype=np.uint8)
    img = Image.fromarray(np.stack([r, g, b, a], axis=-1), "RGBA")

    # Overlay endomysium threads (fine cream lines)
    draw = ImageDraw.Draw(img)
    rng = np.random.default_rng(7)
    for _ in range(140):
        sy = rng.integers(0, height)
        length = rng.integers(80, width // 2)
        sx = rng.integers(0, width - length)
        alpha = rng.integers(55, 155)
        dy_ = rng.integers(-3, 4)
        draw.line([(sx, sy), (sx + length, sy + dy_)],
                  fill=(240, 230, 215, alpha), width=1)

    img = img.filter(ImageFilter.GaussianBlur(radius=0.6))
    return img


def create_muscle_normal_map(width=1024, height=1024):
    X, Y = _make_grid(width, height)
    # Height from fiber striations + cross-bands + noise
    h = (np.sin(Y * 48 * 2 * math.pi) * 0.6 +
         np.sin(Y * 90 * 2 * math.pi) * 0.25 +
         np.sin(X * 180 * 2 * math.pi) * 0.15 +
         _fbm(X, Y, octaves=5, persistence=0.5, base_freq=3.0) * 0.4)
    return _height_to_normal(h, strength=6.0)


def create_muscle_orm(width=1024, height=1024):
    """ORM: R=occlusion (AO), G=roughness, B=metallic"""
    X, Y = _make_grid(width, height)
    noise = _fbm(X, Y, octaves=4, persistence=0.5, base_freq=2.0)
    ao      = ((noise * 0.5 + 0.65) * 255).clip(0, 255).astype(np.uint8)
    roughness = np.full((height, width), int(0.72 * 255), dtype=np.uint8)
    metallic  = np.zeros((height, width), dtype=np.uint8)
    a = np.full((height, width), 255, dtype=np.uint8)
    return Image.fromarray(np.stack([ao, roughness, metallic, a], axis=-1), "RGBA")


# ---------------------------------------------------------------------------
# 2. BONE — Haversian system: osteon rings + periosteum grain
# ---------------------------------------------------------------------------

def create_bone_texture(width=1024, height=1024):
    X, Y = _make_grid(width, height)
    np.random.seed(101)
    rng = np.random.default_rng(101)

    # Base warm ivory
    base = np.ones((height, width, 4), dtype=np.uint8)
    base[:, :, 0] = 230; base[:, :, 1] = 222; base[:, :, 2] = 205; base[:, :, 3] = 255
    img = Image.fromarray(base, "RGBA")
    draw = ImageDraw.Draw(img)

    # Haversian osteon rings (concentric circles at random centers)
    for _ in range(380):
        cx = rng.integers(0, width)
        cy = rng.integers(0, height)
        for ring in range(1, rng.integers(3, 8)):
            r = ring * rng.integers(5, 11)
            shade = rng.integers(195, 220)
            draw.ellipse(
                [cx - r, cy - r, cx + r, cy + r],
                outline=(shade, shade - 10, shade - 25, 180),
                width=1
            )
        # Central canal (Haversian canal)
        cr = rng.integers(2, 5)
        draw.ellipse([cx-cr, cy-cr, cx+cr, cy+cr],
                     fill=(160, 148, 128, 200))

    # Periosteum surface grain (subtle directional streaks)
    for _ in range(90):
        sy = rng.integers(0, height)
        sx = rng.integers(0, width)
        length = rng.integers(60, 200)
        shade = rng.integers(200, 225)
        draw.line([(sx, sy), (sx + length, sy + rng.integers(-2, 3))],
                  fill=(shade, shade - 8, shade - 20, 100), width=1)

    # Noise grain overlay from array
    noise = _fbm(X, Y, octaves=4, persistence=0.6, base_freq=4.0)
    noise_norm = ((noise + 1) * 0.5 * 20).astype(np.uint8)   # 0-20 range
    arr = np.array(img)
    arr[:, :, 0] = np.clip(arr[:, :, 0].astype(np.int16) + noise_norm - 10, 0, 255).astype(np.uint8)
    arr[:, :, 1] = np.clip(arr[:, :, 1].astype(np.int16) + noise_norm - 10, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr, "RGBA")
    img = img.filter(ImageFilter.GaussianBlur(radius=0.9))
    return img


def create_bone_normal_map(width=1024, height=1024):
    X, Y = _make_grid(width, height)
    # Concentric ring structure as height
    rng = np.random.default_rng(55)
    h = np.zeros((height, width), dtype=np.float32)
    xs = np.linspace(0, 1, width)
    ys = np.linspace(0, 1, height)
    for _ in range(80):
        cx = rng.random()
        cy = rng.random()
        Xr = X - cx; Yr = Y - cy
        dist = np.sqrt(Xr*Xr + Yr*Yr)
        h += np.sin(dist * 180 + rng.random() * 6) * 0.08
    h += _fbm(X, Y, octaves=3, persistence=0.5, base_freq=2.0) * 0.2
    return _height_to_normal(h, strength=4.0)


def create_bone_orm(width=1024, height=1024):
    X, Y = _make_grid(width, height)
    noise = _fbm(X, Y, octaves=3, persistence=0.5, base_freq=2.0)
    ao = ((noise * 0.5 + 0.72) * 255).clip(0, 255).astype(np.uint8)
    roughness = np.full((height, width), int(0.65 * 255), dtype=np.uint8)
    metallic  = np.zeros((height, width), dtype=np.uint8)
    a = np.full((height, width), 255, dtype=np.uint8)
    return Image.fromarray(np.stack([ao, roughness, metallic, a], axis=-1), "RGBA")


# ---------------------------------------------------------------------------
# 3. ORGAN VISCERAL — wet capillary-branching surface + cell patterning
# ---------------------------------------------------------------------------

def create_organ_texture(width=1024, height=1024):
    X, Y = _make_grid(width, height)
    rng = np.random.default_rng(13)

    # Cellular mottling: Voronoi-like via min-dist to random centers
    n_centers = 180
    cx = rng.random(n_centers).astype(np.float32)
    cy = rng.random(n_centers).astype(np.float32)
    min_dist = np.full((height, width), 1e6, dtype=np.float32)
    for i in range(n_centers):
        d = np.sqrt((X - cx[i])**2 + (Y - cy[i])**2)
        min_dist = np.minimum(min_dist, d)
    # Normalize and color
    min_dist = (min_dist - min_dist.min()) / (min_dist.max() - min_dist.min())
    noise = _fbm(X, Y, octaves=5, persistence=0.6, base_freq=3.0) * 0.3
    combined = (min_dist * 0.7 + noise * 0.3)
    combined = (combined - combined.min()) / (combined.max() - combined.min())

    # Visceral crimson-to-pink
    r = (155 + combined * 55).clip(0, 255).astype(np.uint8)
    g = (35  + combined * 25).clip(0, 255).astype(np.uint8)
    b = (40  + combined * 20).clip(0, 255).astype(np.uint8)
    a = np.full((height, width), 255, dtype=np.uint8)
    img = Image.fromarray(np.stack([r, g, b, a], axis=-1), "RGBA")

    # Capillary branching lines
    draw = ImageDraw.Draw(img)
    for _ in range(60):
        sx = rng.integers(0, width)
        sy = rng.integers(0, height)
        # Branch recursion depth 3
        def draw_branch(x, y, angle, length, depth):
            if depth == 0 or length < 3:
                return
            ex = int(x + length * math.cos(angle))
            ey = int(y + length * math.sin(angle))
            draw.line([(int(x), int(y)), (ex, ey)],
                      fill=(90, 15, 20, rng.integers(80, 180)), width=1)
            spread = rng.uniform(0.3, 0.7)
            draw_branch(ex, ey, angle + spread, length * 0.65, depth - 1)
            draw_branch(ex, ey, angle - spread, length * 0.55, depth - 1)
        draw_branch(sx, sy, rng.uniform(0, 2*math.pi), rng.integers(15, 50), 3)

    img = img.filter(ImageFilter.GaussianBlur(radius=1.2))
    return img


def create_organ_normal_map(width=1024, height=1024):
    X, Y = _make_grid(width, height)
    h = (_fbm(X, Y, octaves=6, persistence=0.6, base_freq=3.0) * 0.6 +
         np.sin(X * 40 * 2 * math.pi) * 0.1 +
         np.sin(Y * 35 * 2 * math.pi) * 0.1)
    return _height_to_normal(h, strength=3.5)


def create_organ_orm(width=1024, height=1024):
    X, Y = _make_grid(width, height)
    noise = _fbm(X, Y, octaves=4, persistence=0.55, base_freq=2.5)
    ao = ((noise * 0.5 + 0.68) * 255).clip(0, 255).astype(np.uint8)
    roughness = np.full((height, width), int(0.38 * 255), dtype=np.uint8)  # wet = low roughness
    metallic  = np.zeros((height, width), dtype=np.uint8)
    a = np.full((height, width), 255, dtype=np.uint8)
    return Image.fromarray(np.stack([ao, roughness, metallic, a], axis=-1), "RGBA")


# ---------------------------------------------------------------------------
# 4. BRAIN — gyri/sulci convolution patterns
# ---------------------------------------------------------------------------

def create_brain_texture(width=1024, height=1024):
    X, Y = _make_grid(width, height)
    rng = np.random.default_rng(99)

    # Gyri: sinusoidal convolutions at multiple scales + fractal noise
    gyri = (np.sin(X * 7 * 2 * math.pi + Y * 3 * 2 * math.pi) * 0.5 +
            np.sin(X * 11 * 2 * math.pi - Y * 5 * 2 * math.pi + 0.8) * 0.3 +
            np.sin(X * 4 * 2 * math.pi + Y * 9 * 2 * math.pi + 1.5) * 0.2)
    noise = _fbm(X, Y, octaves=6, persistence=0.6, base_freq=4.0) * 0.4
    combined = (gyri + noise)
    combined = (combined - combined.min()) / (combined.max() - combined.min())

    # Pinkish-beige brain tissue
    r = (200 + combined * 40).clip(0, 255).astype(np.uint8)
    g = (155 + combined * 30).clip(0, 255).astype(np.uint8)
    b = (155 + combined * 20).clip(0, 255).astype(np.uint8)
    a = np.full((height, width), 255, dtype=np.uint8)
    img = Image.fromarray(np.stack([r, g, b, a], axis=-1), "RGBA")

    # Deep sulci lines
    draw = ImageDraw.Draw(img)
    for i in range(28):
        points = []
        bx = rng.random() * width
        for y_step in range(0, height, 10):
            x_ = bx + math.sin(y_step * 0.04 + i * 1.1) * 55 + math.cos(y_step * 0.09 + i) * 25
            points.append((x_, y_step))
        if len(points) >= 2:
            draw.line(points, fill=(110, 65, 72, 200), width=rng.integers(3, 7))

    img = img.filter(ImageFilter.GaussianBlur(radius=2.5))
    return img


def create_brain_normal_map(width=1024, height=1024):
    X, Y = _make_grid(width, height)
    h = (np.sin(X * 7 * 2 * math.pi + Y * 3 * 2 * math.pi) * 0.7 +
         np.sin(X * 11 * 2 * math.pi - Y * 5 * 2 * math.pi) * 0.4 +
         _fbm(X, Y, octaves=5, persistence=0.6, base_freq=3.5) * 0.3)
    return _height_to_normal(h, strength=7.0)


def create_brain_orm(width=1024, height=1024):
    X, Y = _make_grid(width, height)
    noise = _fbm(X, Y, octaves=4, persistence=0.5, base_freq=3.0)
    ao = ((noise * 0.5 + 0.60) * 255).clip(0, 255).astype(np.uint8)
    roughness = np.full((height, width), int(0.55 * 255), dtype=np.uint8)
    metallic  = np.zeros((height, width), dtype=np.uint8)
    a = np.full((height, width), 255, dtype=np.uint8)
    return Image.fromarray(np.stack([ao, roughness, metallic, a], axis=-1), "RGBA")


# ---------------------------------------------------------------------------
# 5. VESSEL WALL — smooth elastic arterial wall with subtle layering
# ---------------------------------------------------------------------------

def create_vessel_texture(width=1024, height=1024):
    X, Y = _make_grid(width, height)
    # Elastic laminae: subtle horizontal banding
    band = np.sin(Y * 30 * 2 * math.pi) * 0.3 + np.sin(Y * 70 * 2 * math.pi) * 0.1
    noise = _fbm(X, Y, octaves=4, persistence=0.45, base_freq=2.0) * 0.25
    combined = (band + noise)
    combined = (combined - combined.min()) / (combined.max() - combined.min())

    # Bright arterial red
    r = (200 + combined * 40).clip(0, 255).astype(np.uint8)
    g = (25  + combined * 20).clip(0, 255).astype(np.uint8)
    b = (25  + combined * 15).clip(0, 255).astype(np.uint8)
    a = np.full((height, width), 255, dtype=np.uint8)
    img = Image.fromarray(np.stack([r, g, b, a], axis=-1), "RGBA")
    img = img.filter(ImageFilter.GaussianBlur(radius=0.8))
    return img


def create_vessel_normal_map(width=1024, height=1024):
    X, Y = _make_grid(width, height)
    h = (np.sin(Y * 30 * 2 * math.pi) * 0.5 +
         np.sin(Y * 70 * 2 * math.pi) * 0.2 +
         _fbm(X, Y, octaves=3, persistence=0.4, base_freq=2.0) * 0.2)
    return _height_to_normal(h, strength=3.0)


def create_vessel_orm(width=1024, height=1024):
    X, Y = _make_grid(width, height)
    ao = np.full((height, width), int(0.9 * 255), dtype=np.uint8)
    roughness = np.full((height, width), int(0.30 * 255), dtype=np.uint8)  # smooth, shiny
    metallic  = np.zeros((height, width), dtype=np.uint8)
    a = np.full((height, width), 255, dtype=np.uint8)
    return Image.fromarray(np.stack([ao, roughness, metallic, a], axis=-1), "RGBA")


# ---------------------------------------------------------------------------
# 6. TENDON — parallel collagen fibrils, pearl-cream
# ---------------------------------------------------------------------------

def create_tendon_texture(width=1024, height=1024):
    X, Y = _make_grid(width, height)
    np.random.seed(55)
    rng = np.random.default_rng(55)

    # Tight parallel longitudinal fibrils
    fibril = (np.sin(Y * 90 * 2 * math.pi) * 0.5 +
              np.sin(Y * 150 * 2 * math.pi) * 0.2 +
              np.sin(Y * 30 * 2 * math.pi + X * 5) * 0.15)
    noise = _fbm(X, Y, octaves=4, persistence=0.45, base_freq=2.5) * 0.15
    combined = (fibril + noise)
    combined = (combined - combined.min()) / (combined.max() - combined.min())

    r = (225 + combined * 20).clip(0, 255).astype(np.uint8)
    g = (218 + combined * 15).clip(0, 255).astype(np.uint8)
    b = (205 + combined * 10).clip(0, 255).astype(np.uint8)
    a = np.full((height, width), 255, dtype=np.uint8)
    img = Image.fromarray(np.stack([r, g, b, a], axis=-1), "RGBA")
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    return img


def create_tendon_normal_map(width=1024, height=1024):
    X, Y = _make_grid(width, height)
    h = (np.sin(Y * 90 * 2 * math.pi) * 0.6 +
         np.sin(Y * 150 * 2 * math.pi) * 0.25 +
         _fbm(X, Y, octaves=3, persistence=0.4, base_freq=2.0) * 0.15)
    return _height_to_normal(h, strength=4.0)


def create_tendon_orm(width=1024, height=1024):
    ao = np.full((1024, 1024), int(0.92 * 255), dtype=np.uint8)
    roughness = np.full((1024, 1024), int(0.32 * 255), dtype=np.uint8)
    metallic  = np.zeros((1024, 1024), dtype=np.uint8)
    a = np.full((1024, 1024), 255, dtype=np.uint8)
    return Image.fromarray(np.stack([ao, roughness, metallic, a], axis=-1), "RGBA")


# ---------------------------------------------------------------------------
# MASTER EXPORT
# ---------------------------------------------------------------------------

def generate_all_textures():
    """
    Generate all PBR textures (1024×1024) as a dict of PIL Image objects
    ready for embedding into GLB binary containers.
    Keys: tex_*, norm_*, orm_*
    """
    print("  Generating muscle textures...")
    tex_muscle   = create_muscle_striation_texture(1024, 1024)
    norm_muscle  = create_muscle_normal_map(1024, 1024)
    orm_muscle   = create_muscle_orm(1024, 1024)

    print("  Generating bone textures...")
    tex_bone     = create_bone_texture(1024, 1024)
    norm_bone    = create_bone_normal_map(1024, 1024)
    orm_bone     = create_bone_orm(1024, 1024)

    print("  Generating organ textures...")
    tex_organ    = create_organ_texture(1024, 1024)
    norm_organ   = create_organ_normal_map(1024, 1024)
    orm_organ    = create_organ_orm(1024, 1024)

    print("  Generating brain textures...")
    tex_brain    = create_brain_texture(1024, 1024)
    norm_brain   = create_brain_normal_map(1024, 1024)
    orm_brain    = create_brain_orm(1024, 1024)

    print("  Generating vessel textures...")
    tex_vessel   = create_vessel_texture(1024, 1024)
    norm_vessel  = create_vessel_normal_map(1024, 1024)
    orm_vessel   = create_vessel_orm(1024, 1024)

    print("  Generating tendon textures...")
    tex_tendon   = create_tendon_texture(1024, 1024)
    norm_tendon  = create_tendon_normal_map(1024, 1024)
    orm_tendon   = create_tendon_orm(1024, 1024)

    return {
        "tex_muscle":  tex_muscle,
        "norm_muscle": norm_muscle,
        "orm_muscle":  orm_muscle,
        "tex_bone":    tex_bone,
        "norm_bone":   norm_bone,
        "orm_bone":    orm_bone,
        "tex_organ":   tex_organ,
        "norm_organ":  norm_organ,
        "orm_organ":   orm_organ,
        "tex_brain":   tex_brain,
        "norm_brain":  norm_brain,
        "orm_brain":   orm_brain,
        "tex_vessel":  tex_vessel,
        "norm_vessel": norm_vessel,
        "orm_vessel":  orm_vessel,
        "tex_tendon":  tex_tendon,
        "norm_tendon": norm_tendon,
        "orm_tendon":  orm_tendon,
    }
