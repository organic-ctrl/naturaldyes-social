"""Generated 'photo-like' backgrounds for posts, used when there's no real photo.

Real photos in photos/ always come first. These are stand-ins that look like natural-dye material:

  fabric  {"scene": "fabric",  "color": "#c99a2e", "seed": 1}    draped plain-dyed cloth with soft folds
  stack   {"scene": "stack",   "colors": ["#d9c13a", "#8a8f3a", ...], "seed": 1}   folded fabrics stacked up
  powder  {"scene": "powder",  "color": "#5a1424", "seed": 1}    dye-extract powder in a white bowl
  ecoprint{"scene": "ecoprint", "seed": 1}                       cream cloth with leaf & flower prints
  liquid  {"scene": "liquid",  "color": "#e8361a", "seed": 1}    glowing dye bath with particles
  swatch  {"swatch": "sunburst", "color": "#1f3a6e", "seed": 1}  shibori patterns (see swatches.py)

  python3 tools/scenes.py SPEC_JSON OUT.jpg [W H]
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

sys.path.insert(0, os.path.dirname(__file__))
import swatches  # noqa: E402


def rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=float)


def noise(rng, w, h, scale):
    s = rng.random((max(2, h // scale), max(2, w // scale)))
    return np.asarray(Image.fromarray((s * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), float) / 255


def grain(arr, rng, amt=5):
    return np.clip(arr + rng.normal(0, amt, arr.shape[:2])[..., None], 0, 255)


def fabric(color, seed, W=1080, H=1350):
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:H, 0:W].astype(float)
    n = noise(rng, W, H, 120)
    folds = 0.0
    for k in range(4):
        fx = rng.uniform(0.004, 0.012)
        ph = rng.uniform(0, 6.28)
        folds += np.sin(x * fx + ph + y * rng.uniform(-0.0015, 0.0015) + n * 0.6) / (k + 1)
    light = 0.80 + 0.20 * np.tanh(folds * 1.5) + 0.03 * (noise(rng, W, H, 60) - 0.5)
    light *= 1 - 0.18 * ((x / W - 0.5) ** 2 + (y / H - 0.5) ** 2)
    weave = (np.sin(x * 2.2) * np.sin(y * 2.2)) * 3
    img = rgb(color) * light[..., None] + weave[..., None]
    return Image.fromarray(grain(img, rng, 4).astype(np.uint8))


def stack(colors, seed, W=1080, H=1350):
    rng = np.random.default_rng(seed)
    img = Image.new("RGB", (W, H), (236, 233, 226))
    bg = np.asarray(img, float) * (0.92 + 0.08 * noise(rng, W, H, 200))[..., None]
    img = Image.fromarray(bg.astype(np.uint8))
    d = ImageDraw.Draw(img)
    n = len(colors)
    slab = int(min(220, (H - 200) / n))
    top = H - 120 - slab * n
    for i, c in enumerate(colors):
        y0 = top + i * slab
        x1 = int(W * rng.uniform(0.52, 0.62))
        base = rgb(c)
        for yy in range(slab):
            t = yy / slab
            shade = 0.72 + 0.38 * math.sin(math.pi * (0.15 + 0.75 * t))
            col = tuple(int(v) for v in np.clip(base * shade, 0, 255))
            bulge = int(28 * math.sin(math.pi * t))
            d.line([(-10, y0 + yy), (x1 + bulge, y0 + yy)], fill=col)
    arr = np.asarray(img, float)
    y, x = np.mgrid[0:H, 0:W].astype(float)
    arr = arr + ((np.sin(x * 1.3 + y * 0.4) * 2))[..., None]
    out = Image.fromarray(grain(arr, rng, 3).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    return out


def powder(color, seed, W=1080, H=1350):
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:H, 0:W].astype(float)
    wood = 55 + 18 * np.sin(y * 0.02 + 6 * noise(rng, W, H, 60)) + 10 * noise(rng, W, H, 8)
    img = np.stack([wood * 1.0, wood * 0.82, wood * 0.68], -1)
    cx, cy, R = W * 0.45, H * 0.62, W * 0.48
    r = np.hypot((x - cx), (y - cy) * 1.25)
    bowl = r < R
    img[bowl] = (238 - 30 * (r[bowl] / R) ** 4)[:, None]
    pr = np.hypot((x - cx), (y - cy - 20) * 1.35)
    edge = R * 0.72 * (0.85 + 0.15 * noise(rng, W, H, 40))
    pile = pr < edge
    c = rgb(color)
    h = np.clip(1 - pr / edge, 0, 1)
    shade = 0.55 + 0.6 * h ** 0.6 + 0.25 * (noise(rng, W, H, 3) - 0.5)
    img[pile] = (c[None, :] * shade[pile][:, None])
    specks = (rng.random((H, W)) > 0.9985) & bowl & ~pile
    img[specks] = c * 0.6
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7))
    return Image.fromarray(grain(np.asarray(out, float), rng, 3).astype(np.uint8))


def leaf(d, cx, cy, L, ang, col, rng):
    pts = []
    for s in np.linspace(0, 1, 18):
        w = math.sin(math.pi * s) * L * 0.09
        pts.append((s * L, w))
    pts += [(s, -w) for s, w in reversed(pts)]
    ca, sa = math.cos(ang), math.sin(ang)
    for k in range(-5, 6):  # fern leaflets
        s = 0.5 + k * 0.08
        px, py = s * L, 0
        for side in (1, -1):
            lx = [(px, py), (px + L * 0.12, side * L * 0.16), (px + L * 0.05, side * L * 0.02)]
            d.polygon([(cx + a * ca - b * sa, cy + a * sa + b * ca) for a, b in lx], fill=col)
    d.line([(cx, cy), (cx + L * ca, cy + L * sa)], fill=col, width=4)


def ecoprint(seed, W=1080, H=1350):
    rng = np.random.default_rng(seed)
    base = fabric("#e9dcc3", seed, W, H)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(9):
        leaf(d, rng.uniform(0, W), rng.uniform(0, H), rng.uniform(220, 380), rng.uniform(0, 6.28),
             (190, 160, 40, 150), rng)
    for _ in range(6):
        cx, cy, R = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(70, 130)
        for p in range(12):
            a = p / 12 * 6.28
            px, py = cx + math.cos(a) * R * 0.55, cy + math.sin(a) * R * 0.55
            d.ellipse([px - R * 0.45, py - R * 0.45, px + R * 0.45, py + R * 0.45], fill=(205, 95, 25, 120))
        d.ellipse([cx - R * 0.3, cy - R * 0.3, cx + R * 0.3, cy + R * 0.3], fill=(170, 120, 60, 110))
    layer = layer.filter(ImageFilter.GaussianBlur(3))
    out = base.convert("RGBA")
    out.alpha_composite(layer)
    return out.convert("RGB")


def liquid(color, seed, W=1080, H=1350):
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:H, 0:W].astype(float)
    c = rgb(color)
    glow = 0.65 + 0.45 * np.exp(-(((x - W * 0.55) / W) ** 2 + ((y - H * 0.45) / H) ** 2) * 4)
    img = c * glow[..., None]
    dark = np.clip((y / H - 0.78) * 5, 0, 1)
    img = img * (1 - 0.65 * dark[..., None])
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im, "RGBA")
    for _ in range(70):
        px, py = rng.uniform(0, W), rng.choice([rng.uniform(0, H * 0.25), rng.uniform(H * 0.75, H), rng.uniform(0, H)])
        s = rng.uniform(8, 45)
        d.rounded_rectangle([px, py, px + s * rng.uniform(0.6, 1.4), py + s], 8, fill=(40, 10, 15, int(rng.uniform(60, 170))))
    im = im.filter(ImageFilter.GaussianBlur(2.5))
    return Image.fromarray(grain(np.asarray(im, float), rng, 3).astype(np.uint8))


def make(spec, W=1080, H=1350, seed_base=0):
    """spec: dict scene/swatch, or a file path (real photo)."""
    if isinstance(spec, str):
        return ImageOps.fit(ImageOps.exif_transpose(Image.open(spec)).convert("RGB"), (W, H), Image.LANCZOS)
    seed = spec.get("seed", seed_base)
    if "swatch" in spec:
        return ImageOps.fit(swatches.make(spec["swatch"], spec["color"], seed), (W, H), Image.LANCZOS)
    s = spec["scene"]
    if s == "fabric":
        return fabric(spec["color"], seed, W, H)
    if s == "stack":
        return stack(spec["colors"], seed, W, H)
    if s == "powder":
        return powder(spec["color"], seed, W, H)
    if s == "ecoprint":
        return ecoprint(seed, W, H)
    if s == "liquid":
        return liquid(spec["color"], seed, W, H)
    raise SystemExit("unknown scene " + s)


if __name__ == "__main__":
    W, H = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (1080, 1350)
    make(json.loads(sys.argv[1]), W, H).save(sys.argv[2], quality=92)
