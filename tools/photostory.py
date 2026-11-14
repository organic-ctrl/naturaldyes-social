"""Photo-story reel: the main reel style for @naturaldye.sbpl.

Modelled on the reference reel the user liked: a hook over a full-bleed photo, an elegant title card,
fast one-word "chapters" (a framed photo over a blurred, tinted copy of itself, a serif word and a gold
sub-line), then a dark end card with a photo strip and a CTA. Soft generated music underneath.

  python3 tools/photostory.py SPEC.json OUT.mp4

SPEC.json:
{
  "hook":    {"line1": "One white cloth.", "line2": "One indigo vat.", "line3": "What happens next?", "image": IMG},
  "title":   {"big1": "NATURAL", "big2": "COLOURS", "italic": "From plants, not petroleum",
              "info": ["Natural dye extracts", "Made in Jaipur"]},          # info: 0-3 short lines; last one is gold
  "chapters": [ {"image": IMG, "title": "Fold.", "sub": "Pleats become a resist"}, ... 4-7 of these ],
  "end":     {"line1": "Traditional knowledge.", "line2": "Modern extracts.",
              "name": "Sodhani Biotech", "role": "Natural dyes & dye extracts · Jaipur",
              "cta": "DM us for samples"}
}
IMG is either a path to a real photo (preferred: anything in photos/) or a generated swatch:
  {"swatch": "sunburst|arashi|chevron|itajime|kumo|spiral|ombre", "color": "#1f3a6e", "seed": 3}
"""
import json, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

sys.path.insert(0, os.path.dirname(__file__))
import swatches  # noqa: E402

W, H, FPS = 1080, 1920, 30
FD = os.path.join(os.path.dirname(__file__), "fonts")
LORA_B, LORA_SB, LORA_I = (os.path.join(FD, f) for f in ("Lora-Bold.ttf", "Lora-SemiBold.ttf", "Lora-Italic.ttf"))
POP, POP_SB, POP_B = (os.path.join(FD, f) for f in ("Poppins-Regular.ttf", "Poppins-SemiBold.ttf", "Poppins-Bold.ttf"))
GOLD, WHITE, NAVY = (232, 170, 60), (246, 242, 234), (13, 21, 38)
BRAND = "SODHANI BIOTECH"
_f = {}


def font(p, s):
    if (p, s) not in _f:
        _f[(p, s)] = ImageFont.truetype(p, s)
    return _f[(p, s)]


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def load(img_spec, seed_base=0):
    if isinstance(img_spec, dict):
        return swatches.make(img_spec["swatch"], img_spec["color"], img_spec.get("seed", seed_base)).convert("RGB")
    return ImageOps.exif_transpose(Image.open(img_spec)).convert("RGB")


def cover(img, w, h):
    return ImageOps.fit(img, (w, h), Image.LANCZOS)


def blurred_bg(img, darken=0.45):
    bg = cover(img, W // 4, H // 4).filter(ImageFilter.GaussianBlur(10)).resize((W, H), Image.BICUBIC)
    lum = np.asarray(bg.convert("L"), float).mean() / 255
    darken = min(0.75, darken + 0.7 * max(0.0, lum - 0.40))  # light colours (yellows) need more shade for text
    return Image.blend(bg, Image.new("RGB", (W, H), (0, 0, 0)), darken)


def centered(d, y, text, f, fill, alpha=1.0, base=None):
    if alpha < 1 and base is not None:
        fill = tuple(int(b + (c - b) * alpha) for b, c in zip(base, fill))
    x = (W - d.textlength(text, font=f)) / 2
    d.text((x, y), text, font=f, fill=fill)


def text_fade(canvas, draw_fn, alpha, dy=0):
    """Draw text on a transparent layer and composite with alpha (and a small rise)."""
    if alpha <= 0:
        return canvas
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer), dy)
    if alpha < 1:
        a = layer.getchannel("A").point(lambda v: int(v * alpha))
        layer.putalpha(a)
    out = canvas.convert("RGBA")
    out.alpha_composite(layer)
    return out.convert("RGB")


def brand(d):
    f = font(POP_SB, 26)
    d.text((W - 70 - d.textlength(BRAND, font=f), 70), BRAND, font=f, fill=WHITE)


# ---------------------------------------------------------------- scenes
def scene_hook(h, img):
    full = cover(img, W, H)
    lum = np.asarray(full.convert("L"), float).mean() / 255
    top = int(170 + 70 * max(0.0, lum - 0.40))
    grad = Image.linear_gradient("L").resize((W, H)).point(lambda v: int(top * (1 - v / 255) ** 1.6))
    shade = Image.new("RGB", (W, H), (0, 0, 0))
    base = Image.composite(shade, full, grad)

    def frame(t):
        z = 1.0 + 0.05 * t
        zw, zh = int(W * z), int(H * z)
        im = base.resize((zw, zh), Image.BICUBIC).crop(((zw - W) // 2, (zh - H) // 2, (zw - W) // 2 + W, (zh - H) // 2 + H))
        d = ImageDraw.Draw(im)
        brand(d)

        def txt(dd, dy):
            centered(dd, 230 + dy, h["line1"], font(LORA_SB, 76), WHITE)
            centered(dd, 330 + dy, h["line2"], font(LORA_SB, 76), GOLD)
            if h.get("line3"):
                centered(dd, 450 + dy, h["line3"], font(POP, 44), WHITE)
        a = ease(t * 3)
        return text_fade(im, lambda dd, dy: txt(dd, int(20 * (1 - a))), a)
    return frame


def scene_title(tt, img):
    bg = blurred_bg(img, 0.35)

    def frame(t):
        im = bg.copy()
        d = ImageDraw.Draw(im)
        brand(d)
        lw = int(90 * ease(t * 3))
        d.rectangle([W // 2 - lw // 2, 700, W // 2 + lw // 2, 706], fill=GOLD)

        def txt(dd, dy):
            centered(dd, 760 + dy, tt["big1"], font(POP_B, 104), WHITE)
            centered(dd, 880 + dy, tt["big2"], font(POP_B, 104), GOLD)
            centered(dd, 1030 + dy, tt.get("italic", ""), font(LORA_I, 56), WHITE)
            info = tt.get("info", [])
            for i, line in enumerate(info):
                centered(dd, 1160 + i * 56 + dy, line, font(POP, 38), GOLD if i == len(info) - 1 else WHITE)
        a = ease((t - 0.1) * 3)
        return text_fade(im, lambda dd, dy: txt(dd, int(20 * (1 - a))), a)
    return frame


def scene_chapter(ch, img):
    bg = blurred_bg(img, 0.30)
    side = 700
    photo = cover(img, side, side)
    framed = Image.new("RGB", (side + 24, side + 24), (240, 236, 228))
    framed.paste(photo, (12, 12))
    shadow = Image.new("RGBA", (side + 120, side + 120), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rectangle([60, 70, side + 84, side + 94], fill=(0, 0, 0, 150))
    shadow = shadow.filter(ImageFilter.GaussianBlur(25))
    base = bg.convert("RGBA")
    px, py = (W - framed.width) // 2, 420
    base.alpha_composite(shadow, (px - 60, py - 60))
    base = base.convert("RGB")

    def frame(t):
        im = base.copy()
        s = 0.96 + 0.04 * ease(t * 2)
        fw = int(framed.width * s)
        fr = framed.resize((fw, fw), Image.BICUBIC)
        im.paste(fr, ((W - fw) // 2, py + (framed.width - fw) // 2))
        d = ImageDraw.Draw(im)
        brand(d)

        def txt(dd, dy):
            centered(dd, 1260 + dy, ch["title"], font(LORA_SB, 96), WHITE)
            centered(dd, 1390 + dy, ch.get("sub", ""), font(POP, 40), GOLD)
        a = ease((t - 0.15) * 3.5)
        return text_fade(im, lambda dd, dy: txt(dd, int(16 * (1 - a))), a)
    return frame


def scene_end(e, imgs):
    tile = 150
    strip = [cover(i, tile, tile) for i in imgs[:6]]

    def frame(t):
        im = Image.new("RGB", (W, H), NAVY)
        n = len(strip)
        gap = 18
        total = n * tile + (n - 1) * gap
        x0 = (W - total) // 2
        for i, s in enumerate(strip):
            a = ease(t * 4 - i * 0.25)
            if a > 0:
                tl = Image.blend(Image.new("RGB", s.size, NAVY), s, a)
                im.paste(tl, (x0 + i * (tile + gap), 560 + int(20 * (1 - a))))
        d = ImageDraw.Draw(im)
        brand(d)

        def txt(dd, dy):
            centered(dd, 820 + dy, e["line1"], font(LORA_SB, 66), WHITE)
            centered(dd, 905 + dy, e["line2"], font(LORA_SB, 66), GOLD)
            dd.rectangle([W // 2 - 45, 1030 + dy, W // 2 + 45, 1035 + dy], fill=GOLD)
            centered(dd, 1080 + dy, e["name"], font(POP_SB, 52), WHITE)
            centered(dd, 1155 + dy, e["role"], font(POP, 34), WHITE)
            centered(dd, 1290 + dy, e["cta"], font(POP_SB, 40), GOLD)
            centered(dd, 1350 + dy, "@naturaldye.sbpl", font(POP, 34), WHITE)
        a = ease((t - 0.2) * 2.5)
        return text_fade(im, lambda dd, dy: txt(dd, int(20 * (1 - a))), a)
    return frame


# ---------------------------------------------------------------- music
def music(path, seconds, seed=0):
    """Soft, original ambient pad + plucks (generated, so no licensing issues)."""
    sr = 44100
    n = int(sr * seconds)
    t = np.arange(n) / sr
    rng = np.random.default_rng(seed)
    roots = [57, 53, 60, 55]  # A, F, C, G  (vi-IV-I-V in C)
    chord_len = 2.0
    out = np.zeros(n)
    for i in range(int(seconds / chord_len) + 1):
        root = roots[i % 4]
        s0 = int(i * chord_len * sr)
        seg = min(n - s0, int((chord_len + 1.0) * sr))
        if seg <= 0:
            break
        tt = np.arange(seg) / sr
        env = np.minimum(1, tt / 0.6) * np.exp(-np.maximum(0, tt - chord_len) * 3)
        for iv in (0, 7, 12, 16 if root in (60, 55) else 15):
            f = 440 * 2 ** ((root + iv - 69) / 12)
            out[s0:s0 + seg] += 0.05 * env * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt))
        for k in range(4):  # plucks
            p0 = s0 + int(k * 0.5 * sr)
            if p0 >= n:
                break
            pl = min(n - p0, int(0.6 * sr))
            pt = np.arange(pl) / sr
            note = root + 12 + [0, 7, 12, 16 if root in (60, 55) else 15][rng.integers(0, 4)]
            f = 440 * 2 ** ((note - 69) / 12)
            out[p0:p0 + pl] += 0.06 * np.exp(-pt * 6) * np.sin(2 * np.pi * f * pt)
    fade = np.minimum(1, np.minimum(t / 0.5, (seconds - t) / 1.2))
    out = out * np.clip(fade, 0, 1)
    out = out / (np.max(np.abs(out)) + 1e-9) * 0.6
    st = np.stack([out, np.roll(out, 300)], axis=1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


# ---------------------------------------------------------------- render
def render(spec, out):
    chapters = spec["chapters"]
    ch_imgs = [load(c["image"], i) for i, c in enumerate(chapters)]
    hook_img = load(spec["hook"]["image"], 99) if "image" in spec["hook"] else ch_imgs[0]
    scenes = [(3.2, scene_hook(spec["hook"], hook_img)),
              (3.0, scene_title(spec["title"], ch_imgs[min(1, len(ch_imgs) - 1)]))]
    scenes += [(1.6, scene_chapter(c, im)) for c, im in zip(chapters, ch_imgs)]
    scenes += [(4.2, scene_end(spec["end"], ch_imgs))]
    total = sum(d for d, _ in scenes)
    xf = int(0.25 * FPS)
    audio = out + ".wav"
    music(audio, total, seed=len(chapters))
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", audio, "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    prev_last = None
    for dur, fn in scenes:
        n = int(dur * FPS)
        for i in range(n):
            fr = fn(i / max(1, n - 1))
            if prev_last is not None and i < xf:
                fr = Image.blend(prev_last, fr, (i + 1) / xf)
            p.stdin.write(fr.tobytes())
            last = fr
        prev_last = last
    p.stdin.close()
    rc = p.wait()
    os.remove(audio)
    if rc:
        sys.exit("ffmpeg failed")
    print(f"{out}  ({total:.1f}s, photostory, {len(chapters)} chapters)")


if __name__ == "__main__":
    render(json.load(open(sys.argv[1])), sys.argv[2])
