"""Collage-build reel (7-12 s, 1080x1920): naturally dyed fabric pieces pop in one by one until they fill a shape.

Style taken from a reference reel the user sent (27 Nov): bare scene -> cut fabric pieces appear one at a time ->
the shape is full of colour -> calm branded end card. One short line of text, tiny colour labels.
THE SHAPE / CONCEPT MUST CHANGE EVERY TIME (the user: "not a tree every day, something new daily").

  python3 tools/collage.py SPEC.json OUT.mp4

SPEC = {
  "shape": "tree | leaf | kurta | pot | lotus | drop | heart | mandala | sun | butterfly | word",
  "word": "JAIPUR",                      # only for shape "word" (1-2 short lines, "\\n" splits)
  "background": "sky | paper | dusk | wall | indigo | sand",
  "text": ["A TREE OF", "WASTE-BORN COLOUR"],   # 1-3 short caps lines, shown during the first half
  "colors": [{"name": "Wine Red 3001", "color": "#c11172"}, ...],   # our product shades (data/products.json)
  "pieces": 28,                          # 14-40
  "order": "bottom | top | center | random",
  "seed": 7,
  "end": {"line1": "Colour from waste.", "line2": "Made in Jaipur.", "cta": "DM us for samples"}
}
Pieces come in colour blocks (all of colour 1, then colour 2 ...); each colour's name shows as a tiny italic label
while its block is being built. 3-6 colours work best.
Music is generated (photostory.music), so there is no licensing issue.
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

sys.path.insert(0, os.path.dirname(__file__))
import swatches  # noqa: E402
import scenes  # noqa: E402
from photostory import music  # noqa: E402

W, H, FPS = 1080, 1920, 30
FD = os.path.join(os.path.dirname(__file__), "fonts")
P = lambda f: os.path.join(FD, f)  # noqa: E731
POP_SB, POP_B, LORA_I, PF, PF_I, POP = (P("Poppins-SemiBold.ttf"), P("Poppins-Bold.ttf"), P("Lora-Italic.ttf"),
                                         P("Playfair-Medium.ttf"), P("Playfair-Italic.ttf"), P("Poppins-Regular.ttf"))
INK, GOLD, PAPER = (52, 38, 26), (196, 146, 52), (244, 239, 228)
_f = {}


def font(p, s):
    if (p, s) not in _f:
        _f[(p, s)] = ImageFont.truetype(p, s)
    return _f[(p, s)]


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def noise(rng, w, h, scale):
    small = rng.random((max(2, h // scale), max(2, w // scale)))
    return np.asarray(Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), float) / 255


# ------------------------------------------------------------------ backgrounds
def background(kind, rng):
    y = np.linspace(0, 1, H)[:, None, None]
    grads = {"sky": ((38, 96, 196), (92, 150, 226)), "dusk": ((44, 38, 72), (214, 128, 96)),
             "indigo": ((18, 28, 58), (40, 60, 110)), "wall": ((214, 196, 170), (190, 168, 140)),
             "sand": ((236, 220, 192), (214, 188, 150)), "paper": (PAPER, (236, 229, 214))}
    a, b = grads.get(kind, grads["paper"])
    arr = np.array(a, float) * (1 - y) + np.array(b, float) * y
    arr = np.broadcast_to(arr, (H, W, 3)).copy()
    arr *= (0.94 + 0.06 * noise(rng, W, H, 160))[..., None]
    arr += rng.normal(0, 3 if kind in ("paper", "sand", "wall") else 1.5, (H, W))[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def is_dark(kind):
    return kind in ("sky", "dusk", "indigo")


# ------------------------------------------------------------------ shapes (mask, optional line-art overlay)
CX, CY = W // 2, 960


def poly(d, pts):
    d.polygon([(int(x), int(y)) for x, y in pts], fill=255)


def param(fn, n=400):
    return [fn(t) for t in np.linspace(0, 2 * math.pi, n)]


def tree(rng):
    mask = Image.new("L", (W, H), 0)
    art = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md, ad = ImageDraw.Draw(mask), ImageDraw.Draw(art)
    col = (58, 40, 30, 255)

    def branch(x, y, ang, ln, wd, depth):
        x2, y2 = x + ln * math.cos(ang), y - ln * math.sin(ang)
        ad.line([(x, y), (x2, y2)], fill=col, width=max(2, int(wd)))
        if depth >= 2:
            r = 150 - 12 * depth
            md.ellipse([x2 - r, y2 - r, x2 + r, y2 + r], fill=255)
        if depth < 6:
            for da in (rng.uniform(0.32, 0.5), -rng.uniform(0.32, 0.5)):
                branch(x2, y2, ang + da, ln * rng.uniform(0.74, 0.82), wd * 0.68, depth + 1)
    ad.polygon([(CX - 50, H), (CX + 50, H), (CX + 24, 1280), (CX - 24, 1280)], fill=col)
    branch(CX, 1290, math.pi / 2, 210, 40, 0)
    mask = mask.filter(ImageFilter.GaussianBlur(25)).point(lambda v: 255 if v > 120 else 0)
    trunk = Image.new("L", (W, H), 0)
    ImageDraw.Draw(trunk).polygon([(CX - 46, H), (CX + 46, H), (CX + 22, 1260), (CX - 22, 1260)], fill=255)
    mask = ImageChops.subtract(mask, trunk.filter(ImageFilter.MaxFilter(9)))
    return mask, art, True


def simple(points):
    m = Image.new("L", (W, H), 0)
    poly(ImageDraw.Draw(m), points)
    return m


def leaf(rng):
    pts = []
    for t in np.linspace(0, math.pi, 200):
        pts.append((CX + 330 * math.sin(t) * (1 - 0.25 * math.cos(t)), CY + 520 * math.cos(t)))
    for t in np.linspace(math.pi, 0, 200):
        pts.append((CX - 330 * math.sin(t) * (1 - 0.25 * math.cos(t)), CY + 520 * math.cos(t)))
    m = simple(pts)
    ImageDraw.Draw(m).line([(CX, CY - 520), (CX, CY + 620)], fill=0, width=10)
    return m, None, False


def kurta(rng):
    p = [(CX - 90, 470), (CX - 260, 520), (CX - 470, 860), (CX - 380, 920), (CX - 270, 760), (CX - 290, 1500),
         (CX + 290, 1500), (CX + 270, 760), (CX + 380, 920), (CX + 470, 860), (CX + 260, 520), (CX + 90, 470),
         (CX, 600)]
    return simple(p), None, False


def pot(rng):
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([CX - 420, 640, CX + 420, 1480], fill=255)
    d.rectangle([CX - 170, 520, CX + 170, 720], fill=255)
    d.ellipse([CX - 230, 470, CX + 230, 570], fill=255)
    return m, None, False


def lotus(rng):
    m = Image.new("L", (W, H), 0)
    for ang, ln, wd in [(0, 760, 250), (26, 700, 230), (-26, 700, 230), (52, 580, 200), (-52, 580, 200),
                        (78, 440, 160), (-78, 440, 160)]:
        a = math.radians(ang)
        side = [(wd * math.sin(math.pi * s) ** 0.8 * (1 - 0.3 * s), ln * s) for s in np.linspace(0, 1, 60)]
        pts = [(u, v) for u, v in side] + [(-u, v) for u, v in reversed(side)]
        pts = [(CX + u * math.cos(a) + v * math.sin(a), 1420 - (v * math.cos(a) - u * math.sin(a))) for u, v in pts]
        poly(ImageDraw.Draw(m), pts)
    return m, None, False


def drop(rng):
    return simple(param(lambda t: (CX + 430 * math.sin(t) * math.sin(t / 2) ** 1.2,
                                   CY + 80 - 560 * math.cos(t)))), None, False


def heart(rng):
    return simple(param(lambda t: (CX + 28 * 16 * math.sin(t) ** 3,
                                   CY - 28 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t)
                                              - math.cos(4 * t))))), None, False


def mandala(rng):
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([CX - 170, CY - 170, CX + 170, CY + 170], fill=255)
    for k in range(12):
        a = 2 * math.pi * k / 12
        x, y = CX + 330 * math.cos(a), CY + 330 * math.sin(a)
        d.ellipse([x - 120, y - 120, x + 120, y + 120], fill=255)
    for k in range(18):
        a = 2 * math.pi * (k + 0.5) / 18
        x, y = CX + 480 * math.cos(a), CY + 480 * math.sin(a)
        d.ellipse([x - 55, y - 55, x + 55, y + 55], fill=255)
    return m, None, False


def sun(rng):
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([CX - 300, CY - 300, CX + 300, CY + 300], fill=255)
    for k in range(14):
        a, da = 2 * math.pi * k / 14, 0.13
        poly(d, [(CX + 330 * math.cos(a - da), CY + 330 * math.sin(a - da)),
                 (CX + 520 * math.cos(a), CY + 520 * math.sin(a)),
                 (CX + 330 * math.cos(a + da), CY + 330 * math.sin(a + da))])
    return m, None, False


def ellipse_pts(cx, cy, rx, ry, ang):
    a = math.radians(ang)
    return [(cx + rx * math.cos(t) * math.cos(a) - ry * math.sin(t) * math.sin(a),
             cy + rx * math.cos(t) * math.sin(a) + ry * math.sin(t) * math.cos(a))
            for t in np.linspace(0, 2 * math.pi, 120)]


def butterfly(rng):
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    for s in (-1, 1):
        poly(d, ellipse_pts(CX + s * 230, CY - 200, 290, 210, -s * 35))
        poly(d, ellipse_pts(CX + s * 190, CY + 230, 200, 150, s * 40))
    d.rectangle([CX - 14, CY - 420, CX + 14, CY + 480], fill=0)
    return m, None, False


def word(rng, text):
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    lines = text.upper().split("\n")[:2]
    size = 520
    while size > 120 and max(d.textlength(l, font=font(POP_B, size)) for l in lines) > W - 100:
        size -= 10
    lh = int(size * 1.05)
    for i, l in enumerate(lines):
        d.text(((W - d.textlength(l, font=font(POP_B, size))) / 2, i * lh), l, font=font(POP_B, size), fill=255)
    bb = m.getbbox()
    t = m.crop(bb)
    tw = W - 110
    th = min(1000, int(t.size[1] * tw / t.size[0] * 2.0))     # tall poster lettering
    t = t.resize((tw, th), Image.LANCZOS)
    m = Image.new("L", (W, H), 0)
    m.paste(t, ((W - tw) // 2, CY - th // 2))
    return m, None, False


SHAPES = {"tree": tree, "leaf": leaf, "kurta": kurta, "pot": pot, "lotus": lotus, "drop": drop, "heart": heart,
          "mandala": mandala, "sun": sun, "butterfly": butterfly}


# ------------------------------------------------------------------ pieces
def make_pieces(mask, n, colors, order, rng):
    m = np.asarray(mask) > 127
    ys, xs = np.nonzero(m)
    idx = rng.choice(len(xs), n, replace=False)
    pts = np.stack([xs[idx], ys[idx]], 1).astype(float)
    sc = 4
    gy, gx = np.mgrid[0:H // sc, 0:W // sc]
    jitter = noise(rng, W // sc, H // sc, 12) * 25        # wobbly, hand-cut edges
    dist = ((gx[..., None] * sc + jitter[..., None] - pts[:, 0]) ** 2 + (gy[..., None] * sc - pts[:, 1]) ** 2)
    lab = Image.fromarray(dist.argmin(-1).astype(np.uint8)).resize((W, H), Image.NEAREST)
    lab = np.asarray(lab)
    keys = {"bottom": -pts[:, 1], "top": pts[:, 1], "center": np.hypot(pts[:, 0] - CX, pts[:, 1] - CY),
            "random": rng.random(n)}
    seq = np.argsort(keys.get(order, keys["random"]) + rng.normal(0, 60 if order != "random" else 0, n))
    pats = ["sunburst", "arashi", "chevron", "itajime", "kumo", "spiral", "ombre", None, None]
    out = []
    for j, k in enumerate(seq):
        pm = (lab == k) & m
        if pm.sum() < 150:
            continue
        a = Image.fromarray((pm * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(5))
        bb = a.getbbox()
        if not bb:
            continue
        x0, y0, x1, y1 = bb[0] - 8, bb[1] - 8, bb[2] + 8, bb[3] + 8
        a = a.crop((x0, y0, x1, y1))
        w, h = a.size
        ci = min(len(colors) - 1, j * len(colors) // n)   # colours in blocks, so each label stays ~1 s
        c = colors[ci]["color"]
        pat = pats[rng.integers(0, len(pats))]
        if pat:
            tex = swatches.make(pat, c, int(rng.integers(0, 9999))).resize((max(w, h),) * 2).crop((0, 0, w, h))
        else:
            tex = scenes.fabric(c, int(rng.integers(0, 9999)), w, h)
        edge = a.filter(ImageFilter.MaxFilter(5))
        piece = Image.new("RGBA", (w, h), (34, 26, 20, 0))
        piece.putalpha(edge)
        body = tex.convert("RGBA")
        body.putalpha(a)
        piece.alpha_composite(body)
        out.append({"img": piece, "pos": (x0, y0), "ci": ci})
    return out


# ------------------------------------------------------------------ text + cards
def shadow_text(img, lines, y, dark_bg):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    f = font(POP_SB, 50)
    fill = (255, 255, 255, 255) if dark_bg else (*INK, 255)
    for i, l in enumerate(lines):
        x = (W - d.textlength(l, font=f)) / 2
        if dark_bg:
            d.text((x + 2, y + i * 66 + 3), l, font=f, fill=(0, 0, 0, 110))
        d.text((x, y + i * 66), l, font=f, fill=fill)
    return lay


def label(name, dark_bg):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    f = font(LORA_I, 38)
    x = (W - d.textlength(name, font=f)) / 2
    fill = (255, 255, 255, 235) if dark_bg else (*INK, 235)
    if dark_bg:
        d.text((x + 2, 1702), name, font=f, fill=(0, 0, 0, 120))
    d.text((x, 1700), name, font=f, fill=fill)
    return lay


def end_card(e, colors, rng):
    im = background("paper", rng)
    d = ImageDraw.Draw(im)
    for (x, y, s) in [(150, 260, 1), (W - 170, 330, -1), (180, H - 300, 1), (W - 150, H - 250, -1)]:
        d.line([(x, y - 120), (x + 30 * s, y + 120)], fill=(96, 120, 70), width=4)
        for k in range(4):
            yy = y - 90 + k * 60
            c = rgb(colors[(k + x) % len(colors)]["color"])
            d.ellipse([x + 8 * s * k - 26 + 34 * s, yy - 16, x + 8 * s * k + 26 + 34 * s, yy + 16], fill=c)
            d.ellipse([x + 8 * s * k - 26 - 10 * s, yy + 4, x + 8 * s * k + 26 - 10 * s, yy + 30], fill=(120, 146, 88))
    for i, (txt, f, col) in enumerate([(e.get("line1", ""), font(PF, 70), INK), (e.get("line2", ""), font(PF_I, 70), GOLD)]):
        d.text(((W - d.textlength(txt, font=f)) / 2, 700 + i * 96), txt, font=f, fill=col)
    d.line([(W / 2 - 50, 940), (W / 2 + 50, 940)], fill=GOLD, width=3)
    for txt, f, y, col in [("Sodhani Biotech", font(POP_SB, 52), 990, INK),
                           ("Natural dyes & dye extracts · Jaipur", font(POP, 32), 1065, (110, 96, 80)),
                           (e.get("cta", "DM us for samples"), font(POP_SB, 42), 1170, (168, 96, 40)),
                           ("@naturaldye.sbpl", font(POP, 30), 1240, (110, 96, 80))]:
        d.text(((W - d.textlength(txt, font=f)) / 2, y), txt, font=f, fill=col)
    return im


# ------------------------------------------------------------------ render
def render(spec, out):
    rng = np.random.default_rng(spec.get("seed", 1))
    kind = spec.get("background", "paper")
    dark = is_dark(kind)
    bg = background(kind, rng)
    shape = spec.get("shape", "leaf")
    mask, art, art_over = word(rng, spec.get("word", "COLOUR")) if shape == "word" else SHAPES[shape](rng)
    if art is not None:
        bg = bg.convert("RGBA")
        bg.alpha_composite(art)
        bg = bg.convert("RGB")
    colors = spec["colors"]
    pieces = make_pieces(mask, int(spec.get("pieces", 28)), colors, spec.get("order", "random"), rng)
    text = spec.get("text", [])
    intro, gap, anim, hold, endd = 0.7, min(0.2, 5.5 / max(1, len(pieces))), 6, 1.6, 2.6
    build = len(pieces) * gap + anim / FPS
    total = intro + build + hold + endd
    endimg = end_card(spec.get("end", {}), colors, rng)
    txt_layer = shadow_text(bg, text, 230, dark) if text else None
    audio = out + ".wav"
    music(audio, total, seed=spec.get("seed", 1))
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", audio, "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    settled = bg.convert("RGBA")
    placed, seen, cur_label, last = 0, set(), None, None
    nframes = int(total * FPS)
    t_end = intro + build + hold
    for fi in range(nframes):
        t = fi / FPS
        while placed < len(pieces) and t >= intro + placed * gap + anim / FPS:
            pc = pieces[placed]
            settled.alpha_composite(pc["img"], pc["pos"])
            placed += 1
        fr = settled.copy()
        k = placed
        while k < len(pieces) and t >= intro + k * gap:
            pc = pieces[k]
            u = min(1.0, (t - intro - k * gap) * FPS / anim)
            s = 1.18 - 0.18 * (1 - (1 - u) ** 3)
            im = pc["img"]
            w, h = im.size
            im2 = im.resize((max(1, int(w * s)), max(1, int(h * s))))
            a = np.asarray(im2.getchannel("A"), float) * u
            im2.putalpha(Image.fromarray(a.astype(np.uint8)))
            fr.alpha_composite(im2, (int(pc["pos"][0] - (im2.size[0] - w) / 2), int(pc["pos"][1] - (im2.size[1] - h) / 2)))
            if pc["ci"] not in seen:
                seen.add(pc["ci"])
                cur_label = colors[pc["ci"]]["name"]
            k += 1
        if txt_layer is not None and t < intro + build * 0.55:
            fr.alpha_composite(txt_layer)
        if cur_label and t < t_end:
            fr.alpha_composite(label(cur_label, dark))
        fr = fr.convert("RGB")
        if t >= t_end:
            fr = Image.blend(fr, endimg, min(1.0, (t - t_end) / 0.4))
        p.stdin.write(fr.tobytes())
        last = fr
    p.stdin.close()
    rc = p.wait()
    os.remove(audio)
    if rc:
        sys.exit("ffmpeg failed")
    print(f"{out}  ({total:.1f}s, collage '{shape}', {len(pieces)} pieces)")


if __name__ == "__main__":
    render(json.load(open(sys.argv[1])), sys.argv[2])
