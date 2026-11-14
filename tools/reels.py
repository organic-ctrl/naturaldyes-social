"""Animated reel styles for @naturaldye.sbpl (Sodhani Biotech).

Usage:  python3 tools/reels.py SPEC.json OUT.mp4

SPEC.json is {"style": "...", ...}. Styles and their fields:

  pour     {"title", "dyes": [{"name", "source", "color"} x2-4], "cta"}
           Colour flows up over a white fabric swatch, one dye at a time.
  quiz     {"question", "color", "options": [a, b, c], "answer", "fact", "cta"}
           "Guess the plant" card, 3-2-1 countdown, answer reveal.
  mythfact {"pairs": [{"myth", "fact"} x1-3], "cta"}
           Red MYTH card flips into a green FACT card.
  top3     {"title", "items": [three strings, shown as 3, 2, 1], "cta"}
           Big-number countdown list.
  compare  {"title", "left": "Natural dyes", "right": "Synthetic dyes",
            "rows": [[left, right] x3-5], "cta"}
           Split screen that builds row by row.
  steps    {"title", "steps": [3-5 strings], "cta"}
           Process / mini-workshop: numbered steps with a progress bar.
  news     {"headline", "summary", "source", "cta"}
           "Natural dye news" bulletin. Only real news, with its source named.

All reels are 1080x1920, 30 fps, H.264 with a silent AAC track (add music in the app if wanted).
"""
import json, math, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
F = "/usr/share/fonts/truetype/dejavu/"
SERIF_B, SANS, SANS_B = F + "DejaVuSerif-Bold.ttf", F + "DejaVuSans.ttf", F + "DejaVuSans-Bold.ttf"
CREAM, INK, BROWN, GREEN, RED = "#f4ecdf", "#2b2118", "#8a5a2b", "#4f7a3a", "#a8322d"
PALETTE = ["#1f3a68", "#a8322d", "#d9a21b", "#6b4a2b", "#4f7a3a", "#c46a2f"]
_fonts = {}


def font(path, size):
    k = (path, size)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(path, size)
    return _fonts[k]


def ease(t):  # ease-out cubic, clamped
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    a, b = rgb(a) if isinstance(a, str) else a, rgb(b) if isinstance(b, str) else b
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(d, x, y, text, f, fill, maxw=W - 180, gap=14, align="left", alpha=1.0, bg=CREAM):
    col = mix(bg, fill, alpha) if alpha < 1 else fill
    for line in wrap(d, text, f, maxw):
        lx = x if align == "left" else (W - d.textlength(line, font=f)) / 2
        d.text((lx, y), line, font=f, fill=col)
        y += f.size + gap
    return y


def footer(d, bg=INK):
    d.rectangle([0, H - 150, W, H], fill=bg)
    d.text((90, H - 115), "SODHANI BIOTECH · JAIPUR", font=font(SANS_B, 34), fill=CREAM)
    d.text((90, H - 68), "Natural dyes & dye extracts  |  @naturaldye.sbpl", font=font(SANS, 30), fill="#d9c9b0")


def base(color=CREAM):
    img = Image.new("RGB", (W, H), color)
    return img, ImageDraw.Draw(img)


def cta_frame(t, cta):
    img, d = base(INK)
    a = ease(t * 2)
    y = 760 - 40 * (1 - a)
    text_block(d, 0, y, cta, font(SERIF_B, 84), CREAM, align="center", alpha=a, bg=INK, maxw=W - 160)
    sw = W / len(PALETTE)
    for i, c in enumerate(PALETTE):
        h = int(60 * ease(t * 3 - i * 0.12))
        d.rectangle([int(i * sw), 1350 - h, int((i + 1) * sw), 1350], fill=c)
    d.text((W / 2 - d.textlength("@naturaldye.sbpl", font=font(SANS_B, 44)) / 2, 1420),
           "@naturaldye.sbpl", font=font(SANS_B, 44), fill="#d9c9b0")
    return img


# ---------------------------------------------------------------- styles
def style_pour(s):
    scenes = []
    def intro(t):
        img, d = base()
        a = ease(t * 2)
        text_block(d, 90, 700 + 40 * (1 - a), "Natural dyes".upper(), font(SANS_B, 38), BROWN, alpha=a)
        text_block(d, 90, 770 + 40 * (1 - a), s["title"], font(SERIF_B, 92), INK, alpha=a)
        footer(d)
        return img
    scenes.append((2.2, intro))
    for dye in s["dyes"]:
        def pour(t, dye=dye):
            img, d = base()
            x0, y0, x1, y1 = 140, 330, W - 140, 1230
            d.rectangle([x0, y0, x1, y1], fill="#ffffff", outline="#e2d6c3", width=4)
            lvl = y1 - (y1 - y0) * ease(t * 1.4)
            pts = [(x0, y1)]
            for x in range(x0, x1 + 1, 12):
                pts.append((x, lvl + 18 * math.sin(x / 70 + t * 9) * (1 - ease(t * 1.4))))
            pts.append((x1, y1))
            d.polygon(pts, fill=dye["color"])
            # weave texture
            for yy in range(y0, y1, 22):
                d.line([(x0, yy), (x1, yy)], fill=mix(dye["color"], "#ffffff", 0.0) if yy > lvl else "#f1ece4", width=1)
            a = ease((t - 0.45) * 3)
            text_block(d, 90, 1290 + 30 * (1 - a), dye["name"], font(SERIF_B, 84), INK, alpha=a)
            text_block(d, 90, 1400 + 30 * (1 - a), dye["source"], font(SANS, 42), "#3d3328", alpha=a)
            footer(d)
            return img
        scenes.append((3.0, pour))
    scenes.append((2.6, lambda t: cta_frame(t, s["cta"])))
    return scenes


def style_quiz(s):
    def q(t):
        img, d = base()
        text_block(d, 90, 170, "GUESS THE PLANT", font(SANS_B, 44), BROWN)
        y = text_block(d, 90, 240, s["question"], font(SERIF_B, 76), INK)
        r = int(260 * ease(t * 2))
        cx, cy = W // 2, 900
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=s["color"])
        f = font(SANS_B, 48)
        for i, o in enumerate(s["options"]):
            a = ease((t - 0.3 - i * 0.15) * 3)
            yy = 1250 + i * 100
            d.rounded_rectangle([90, yy, W - 90, yy + 80], 40, fill=mix(CREAM, "#e6d8c2", a))
            d.text((130, yy + 14), f"{'ABC'[i]}.  {o}", font=f, fill=mix(CREAM, INK, a))
        footer(d)
        return img
    def count(t):
        img, d = base(s["color"])
        n = 3 - min(2, int(t * 3))
        local = (t * 3) % 1
        size = int(420 - 120 * local)
        f = font(SERIF_B, size)
        txt = str(n)
        d.text(((W - d.textlength(txt, font=f)) / 2, H / 2 - size * 0.6), txt, font=f, fill=CREAM)
        d.text((W / 2 - d.textlength("Comment your guess!", font=font(SANS_B, 46)) / 2, 1450),
               "Comment your guess!", font=font(SANS_B, 46), fill=CREAM)
        return img
    def reveal(t):
        img, d = base()
        a = ease(t * 2.5)
        d.rectangle([0, 0, W, int(700 * a)], fill=s["color"])
        text_block(d, 90, 780, "ANSWER", font(SANS_B, 44), BROWN, alpha=a)
        y = text_block(d, 90, 850, s["answer"], font(SERIF_B, 96), INK, alpha=a)
        b = ease((t - 0.35) * 3)
        text_block(d, 90, y + 40, s["fact"], font(SANS, 44), "#3d3328", alpha=b)
        footer(d)
        return img
    return [(3.6, q), (3.0, count), (4.0, reveal), (2.4, lambda t: cta_frame(t, s["cta"]))]


def style_mythfact(s):
    scenes = []
    for p in s["pairs"]:
        def flip(t, p=p):
            img, d = base()
            if t < 0.45:
                col, label, txt = RED, "MYTH", p["myth"]
                k = 1.0 if t < 0.35 else 1 - (t - 0.35) / 0.1
            else:
                col, label, txt = GREEN, "FACT", p["fact"]
                k = min(1.0, (t - 0.45) / 0.1)
            cw = int((W - 140) * max(0.02, k))
            x0 = (W - cw) // 2
            d.rounded_rectangle([x0, 300, x0 + cw, 1550], 40, fill=col)
            if k > 0.85:
                f = font(SANS_B, 120)
                d.text(((W - d.textlength(label, font=f)) / 2, 400), label, font=f, fill=CREAM)
                text_block(d, 0, 640, txt, font(SERIF_B, 70), CREAM, align="center", maxw=W - 260, bg=col)
            return img
        scenes.append((5.0, flip))
    scenes.append((2.4, lambda t: cta_frame(t, s["cta"])))
    return scenes


def style_top3(s):
    def title(t):
        img, d = base(INK)
        a = ease(t * 2)
        text_block(d, 0, 760 + 40 * (1 - a), s["title"], font(SERIF_B, 92), CREAM, align="center",
                   alpha=a, bg=INK, maxw=W - 160)
        return img
    scenes = [(2.4, title)]
    for i, item in enumerate(s["items"]):
        n = 3 - i
        col = PALETTE[(i * 2) % len(PALETTE)]
        def card(t, n=n, item=item, col=col):
            img, d = base()
            x = int(-700 + 790 * ease(t * 2.2))
            f = font(SERIF_B, 520)
            d.text((x, 160), str(n), font=f, fill=col)
            a = ease((t - 0.25) * 2.5)
            text_block(d, 90, 900 + 30 * (1 - a), item, font(SERIF_B, 76), INK, alpha=a)
            d.rectangle([0, H - 170, int(W * ease(t)), H - 150], fill=col)
            footer(d)
            return img
        scenes.append((3.2, card))
    scenes.append((2.4, lambda t: cta_frame(t, s["cta"])))
    return scenes


def style_compare(s):
    rows = s["rows"]
    dur = 2.0 + 1.6 * len(rows)
    def comp(t):
        img, d = base()
        text_block(d, 0, 140, s["title"], font(SERIF_B, 70), INK, align="center", maxw=W - 160)
        d.rectangle([0, 400, W // 2 - 4, 520], fill=GREEN)
        d.rectangle([W // 2 + 4, 400, W, 520], fill="#6e6e6e")
        f = font(SANS_B, 44)
        for txt, cx in ((s["left"], W / 4), (s["right"], 3 * W / 4)):
            d.text((cx - d.textlength(txt, font=f) / 2, 435), txt, font=f, fill=CREAM)
        elapsed = t * dur
        y = 560
        for i, (l, r) in enumerate(rows):
            a = ease((elapsed - 1.0 - i * 1.6) * 1.5)
            if a <= 0:
                break
            fr = font(SANS, 46)
            yl = text_block(d, 50, y, "✓ " + l, fr, GREEN, maxw=W // 2 - 90, alpha=a, gap=8)
            yr = text_block(d, W // 2 + 40, y, "✗ " + r, fr, "#6e6e6e", maxw=W // 2 - 90, alpha=a, gap=8)
            y = max(yl, yr) + 34
            d.line([(50, y - 17), (W - 50, y - 17)], fill="#e2d6c3", width=2)
        d.line([(W // 2, 520), (W // 2, max(560, y))], fill="#e2d6c3", width=3)
        footer(d)
        return img
    return [(dur, comp), (2.4, lambda t: cta_frame(t, s["cta"]))]


def style_steps(s):
    steps = s["steps"]
    def intro(t):
        img, d = base(GREEN)
        a = ease(t * 2)
        text_block(d, 0, 640, "MINI WORKSHOP", font(SANS_B, 44), CREAM, align="center", alpha=a, bg=GREEN)
        text_block(d, 0, 720 + 30 * (1 - a), s["title"], font(SERIF_B, 90), CREAM, align="center",
                   alpha=a, bg=GREEN, maxw=W - 160)
        return img
    scenes = [(2.4, intro)]
    for i, st in enumerate(steps):
        def card(t, i=i, st=st):
            img, d = base()
            col = PALETTE[i % len(PALETTE)]
            r = int(150 * ease(t * 3))
            d.ellipse([W // 2 - r, 520 - r, W // 2 + r, 520 + r], fill=col)
            f = font(SERIF_B, 170)
            if r > 100:
                d.text((W / 2 - d.textlength(str(i + 1), font=f) / 2, 410), str(i + 1), font=f, fill=CREAM)
            a = ease((t - 0.2) * 2.5)
            text_block(d, 0, 800, f"STEP {i + 1} OF {len(steps)}", font(SANS_B, 40), BROWN, align="center", alpha=a)
            text_block(d, 0, 870 + 30 * (1 - a), st, font(SERIF_B, 76), INK, align="center", alpha=a, maxw=W - 180)
            prog = (i + ease(t)) / len(steps)
            d.rectangle([90, 1620, W - 90, 1640], fill="#e6d8c2")
            d.rectangle([90, 1620, 90 + int((W - 180) * prog), 1640], fill=GREEN)
            footer(d)
            return img
        scenes.append((2.8, card))
    scenes.append((2.4, lambda t: cta_frame(t, s["cta"])))
    return scenes


def style_news(s):
    def bulletin(t):
        img, d = base()
        d.rectangle([0, 0, W, 260], fill=RED)
        f = font(SANS_B, 56)
        lab = "NATURAL DYE NEWS"
        d.text(((W - d.textlength(lab, font=f)) / 2, 100), lab, font=f, fill=CREAM)
        if int(t * 8) % 2 == 0:
            d.ellipse([90, 112, 130, 152], fill=CREAM)
        a = ease((t - 0.05) * 4)
        y = text_block(d, 90, 380 + 30 * (1 - a), s["headline"], font(SERIF_B, 80), INK, alpha=a)
        b = ease((t - 0.3) * 3)
        y = text_block(d, 90, y + 40, s["summary"], font(SANS, 46), "#3d3328", alpha=b)
        c = ease((t - 0.6) * 3)
        text_block(d, 90, y + 40, "Source: " + s["source"], font(SANS_B, 36), BROWN, alpha=c)
        footer(d)
        return img
    return [(9.0, bulletin), (2.4, lambda t: cta_frame(t, s["cta"]))]


STYLES = {"pour": style_pour, "quiz": style_quiz, "mythfact": style_mythfact, "top3": style_top3,
          "compare": style_compare, "steps": style_steps, "news": style_news}


def render(spec, out):
    scenes = STYLES[spec["style"]](spec)
    total = sum(dur for dur, _ in scenes)
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-f", "lavfi", "-t", f"{total:.2f}", "-i",
           "anullsrc=r=44100:cl=stereo", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for dur, fn in scenes:
        n = int(dur * FPS)
        for i in range(n):
            p.stdin.write(fn(i / max(1, n - 1)).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        sys.exit("ffmpeg failed")
    print(f"{out}  ({total:.1f}s, style={spec['style']})")


if __name__ == "__main__":
    render(json.load(open(sys.argv[1])), sys.argv[2])
