"""Procedural shibori / tie-dye fabric swatches in natural-dye colours.

Used by photostory reels when there is no real photo for a scene. Real photos in photos/ are always preferred.

  python3 tools/swatches.py PATTERN COLOR OUT.jpg [seed]
  PATTERN: sunburst | arashi | chevron | itajime | kumo | spiral | ombre
  COLOR:   a hex colour (indigo #1f3a6e, madder #a3262f, pomegranate #b8892a,
           catechu #6b4a2b, lac #7a1f3d, marigold #d39b1c, olive #7a7a2a ...)
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

S = 900
CLOTH = np.array([243, 239, 230], dtype=float)


def hex2(c):
    c = c.lstrip("#")
    return np.array([int(c[i:i + 2], 16) for i in (0, 2, 4)], dtype=float)


def smooth_noise(rng, scale, size=S):
    small = rng.random((max(2, size // scale), max(2, size // scale)))
    img = Image.fromarray((small * 255).astype(np.uint8)).resize((size, size), Image.BICUBIC)
    return np.asarray(img, dtype=float) / 255.0


def pattern(name, rng):
    y, x = np.mgrid[0:S, 0:S].astype(float)
    cx = cy = S / 2
    dx, dy = x - cx, y - cy
    r = np.hypot(dx, dy)
    th = np.arctan2(dy, dx)
    n1 = smooth_noise(rng, 60)
    n2 = smooth_noise(rng, 12)
    if name == "sunburst":
        v = np.sin(th * 18 + n1 * 3) * 0.5 + 0.5
        v = np.where(r < 60 + 40 * n1, 0.0, v)
        v = v * np.clip(r / 120, 0, 1)
        v = 0.25 + 0.75 * (v > 0.45 + 0.15 * n2)
        v = np.where(np.abs(np.sin(r / 55 + n1 * 2)) < 0.12, v * 0.3, v)
    elif name == "spiral":
        v = np.sin(th * 3 + r / 38 + n1 * 2.5)
        v = (v > -0.1 + 0.3 * (n2 - 0.5)).astype(float)
        v = np.where(r < 40, 0.2, v)
    elif name == "arashi":
        u = (x + y) / 1.414
        v = np.sin(u / 9 + n1 * 6 + np.sin(y / 60) * 1.5)
        v = (v > 0.1 + 0.5 * (n2 - 0.5)).astype(float)
    elif name == "chevron":
        u = np.abs(x - cx) * 0.9 + y
        v = np.sin(u / 14 + n1 * 4)
        v = (v > 0.05 + 0.5 * (n2 - 0.5)).astype(float)
        v = np.where(np.abs(x - cx) < 6 + 6 * n1, 0.35, v)
    elif name == "itajime":
        cell = S / 2
        fx = np.abs(((x % cell) / cell) - 0.5) * 2
        fy = np.abs(((y % cell) / cell) - 0.5) * 2
        d = np.maximum(fx, fy)
        v = np.sin(d * 22 + n1 * 3)
        v = (v > 0.2 * (n2 - 0.5) * 2).astype(float)
        v = np.where(np.minimum(np.abs(x % cell - cell / 2), np.abs(y % cell - cell / 2)) < 10 + 10 * n1,
                     0.15, v)
    elif name == "kumo":
        v = np.ones((S, S))
        for gx in range(3):
            for gy in range(3):
                px, py = (gx + 0.5) * S / 3 + rng.normal(0, 15), (gy + 0.5) * S / 3 + rng.normal(0, 15)
                rr = np.hypot(x - px, y - py)
                ring = (rr < 55 + 25 * n1) & (rr > 20)
                v = np.where(ring, 0.05 + 0.2 * n2, v)
                v = np.where(rr <= 20, 0.7, v)
    elif name == "ombre":
        v = np.clip(y / S + 0.08 * np.sin(x / 70 + n1 * 3) + 0.05 * np.sin(x / 23), 0, 1) ** 1.4
    else:
        raise SystemExit("unknown pattern " + name)
    return np.clip(v, 0, 1)


def make(pat, color, seed=0):
    rng = np.random.default_rng(seed)
    v = pattern(pat, rng)
    v = np.asarray(Image.fromarray((v * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.2)),
                   dtype=float) / 255.0
    depth = 0.75 + 0.25 * smooth_noise(rng, 90)          # uneven dye uptake
    v = v * depth
    col = hex2(color)
    img = CLOTH * (1 - v[..., None]) + col * v[..., None]
    # weave texture
    yy, xx = np.mgrid[0:S, 0:S]
    weave = (np.sin(xx * 1.9) * np.sin(yy * 1.9)) * 4 + rng.normal(0, 3, (S, S))
    img = img + weave[..., None]
    img = np.clip(img, 0, 255).astype(np.uint8)
    return Image.fromarray(img)


if __name__ == "__main__":
    pat, color, out = sys.argv[1:4]
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    make(pat, color, seed).save(out, quality=92)
    print(out)
