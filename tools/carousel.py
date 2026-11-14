"""Carousel posts (2–10 slides, 1080x1350) in the editorial style of the user's reference posts.

  python3 tools/carousel.py SPEC.json OUT_DIR      -> OUT_DIR/01.jpg, 02.jpg, ...

SPEC = {"slides": [ {slide}, ... ]}. Every slide may have "image": a real photo path (preferred, from photos/)
or a generated scene, e.g. {"scene": "fabric", "color": "#1f3a6e", "seed": 3} (see scenes.py).

Slide types:
  series     {"name": "INDIGO", "script": "Natural", "bold": "Dye", "series": "Story Series", "image"}
             Script word + bold word + small line + one huge name. A cover.
  question   {"text": "How is indigo made?", "image"}
             Caps question in a frosted rounded box. A cover.
  education  {"kicker": "COLOUR EDUCATION", "line1": "The Indian", "accent": "Colour Story", "line2": "No One Is Telling",
              "quote": "...", "dots": ["#..."], "swipe": "Swipe to explore 5 colours"}
             Cream card, soft colour blobs, serif headline with an italic coloured word. A cover.
  spotlight  {"name": "Pomegranate", "local": "Anar", "latin": "Punica granatum", "image"}
             Ingredient / dye spotlight: big serif name bottom-left, gold rule, italic local name, Latin name.
  statement  {"big": "100% NATURAL DYE", "caption_bold": "MARIGOLD", "caption": "- a flower ...", "image"}
             Huge translucent words and a dark caption box.
  labels     {"title": "Mango Leaf Natural Dye", "labels": ["Cotton", "Silk", ...], "colors": ["#...", ...]}
             Stacked fabrics with a white label on each (fibre / mordant comparisons). Up to 6.
  boxed      {"lines": ["The Color", "of Place:"], "small": ["Colors from", "forest"], "image"}
             Text in black highlight boxes over a photo.
  point      {"num": "01", "title": "Renewable", "body": "Plant sources grow back every season.", "color": "#4f7a3a", "image"}
             A content slide: number, serif title, two-line body, image panel on top.
  palette    {"title", "items": [{"name", "sub", "color"} x up to 9]}   product swatch grid
  stats      {"kicker", "stats": [{"big": "80%", "label", "sub"} x1-3], "color", "note"}   big-number proof slide
  end        {"line1": "Colour from nature.", "line2": "Made in Jaipur.", "cta": "DM us for samples"}
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import scenes  # noqa: E402

W, H = 1080, 1350
FD = os.path.join(os.path.dirname(__file__), "fonts")
P = lambda f: os.path.join(FD, f)  # noqa: E731
SCRIPT, PF, PF_I = P("GreatVibes-Regular.ttf"), P("Playfair-Medium.ttf"), P("Playfair-Italic.ttf")
LORA_SB, LORA_I = P("Lora-SemiBold.ttf"), P("Lora-Italic.ttf")
POP, POP_SB, POP_B = P("Poppins-Regular.ttf"), P("Poppins-SemiBold.ttf"), P("Poppins-Bold.ttf")
CREAM, INK, GOLD, RUST = (252, 245, 236), (52, 38, 26), (214, 164, 64), (184, 92, 56)
WHITE = (250, 247, 240)
HANDLE = "@naturaldye.sbpl"
_f = {}


def font(p, s):
    if (p, s) not in _f:
        _f[(p, s)] = ImageFont.truetype(p, s)
    return _f[(p, s)]


def fit_font(d, text, path, start, maxw, min_size=24):
    s = start
    while s > min_size and d.textlength(text, font=font(path, s)) > maxw:
        s -= 4
    return font(path, s)


def wrap(d, text, f, maxw):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            if cur:
                out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out


def ctext(d, y, text, f, fill, x0=0, x1=W):
    d.text((x0 + (x1 - x0 - d.textlength(text, font=f)) / 2, y), text, font=f, fill=fill)


def img_of(slide, i, size=(W, H)):
    spec = slide.get("image") or {"scene": "fabric", "color": "#8a6a3a", "seed": i}
    return scenes.make(spec, *size, seed_base=i)


def darken(im, a):
    return Image.blend(im, Image.new("RGB", im.size, (0, 0, 0)), a)


def overlay(base, draw_fn):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    out = base.convert("RGBA")
    out.alpha_composite(layer)
    return out.convert("RGB")


def counter(d, i, n, color=(255, 255, 255)):
    f = font(POP, 26)
    d.text((W - 60 - d.textlength(HANDLE, font=f), H - 70), HANDLE, font=f, fill=color)
    d.text((60, H - 70), f"{i + 1} / {n}", font=f, fill=color)


# ------------------------------------------------------------------ slide types
def s_series(s, i, n):
    im = darken(img_of(s, i), 0.25)

    def draw(d):
        f1 = font(SCRIPT, 230)
        d.text((10, 250), s.get("script", "Natural"), font=f1, fill=(255, 255, 255, 245))
        d.text((110, 470), s.get("bold", "Dye"), font=font(POP_SB, 210), fill=(255, 255, 255, 245))
        d.text((115, 720), s.get("series", "Story Series"), font=font(POP, 76), fill=(255, 255, 255, 245))
        f4 = fit_font(d, s["name"], POP_B, 200, W - 120)
        d.text((60, 820), s["name"], font=f4, fill=(255, 255, 255, 250))
    im = overlay(im, draw)
    counter(ImageDraw.Draw(im), i, n)
    return im


def s_question(s, i, n):
    im = img_of(s, i)

    def draw(d):
        f = font(POP_SB, 64)
        lines = wrap(d, s["text"].upper(), f, W - 300)
        h = len(lines) * 92 + 120
        y0 = (H - h) // 2
        d.rounded_rectangle([130, y0, W - 130, y0 + h], 40, fill=(255, 255, 255, 170))
        for k, l in enumerate(lines):
            ctext(d, y0 + 60 + k * 92, l, f, (110, 52, 20, 255))
    im = overlay(im, draw)
    counter(ImageDraw.Draw(im), i, n, (90, 60, 40))
    return im


def s_education(s, i, n):
    rng = np.random.default_rng(i + 11)
    im = Image.new("RGB", (W, H), CREAM)
    blobs = Image.new("RGB", (W, H), CREAM)
    bd = ImageDraw.Draw(blobs)
    for col, (x, y) in zip([(245, 200, 190), (210, 232, 210), (250, 220, 200), (205, 222, 240)],
                           [(80, 120), (980, 300), (200, 1150), (950, 1150)]):
        r = rng.uniform(220, 320)
        bd.ellipse([x - r, y - r, x + r, y + r], fill=col)
    im = blobs.filter(ImageFilter.GaussianBlur(120))
    d = ImageDraw.Draw(im)
    for (x, y, dx, dy) in [(48, 48, 1, 1), (W - 48, 48, -1, 1), (48, H - 48, 1, -1), (W - 48, H - 48, -1, -1)]:
        d.line([(x, y), (x + 36 * dx, y)], fill=INK, width=3)
        d.line([(x, y), (x, y + 36 * dy)], fill=INK, width=3)
    k = " ".join(s.get("kicker", "SODHANI BIOTECH · COLOUR EDUCATION"))
    ctext(d, 280, k, fit_font(d, k, POP, 28, W - 160), (150, 120, 90))
    ctext(d, 360, s["line1"], fit_font(d, s["line1"], PF, 110, W - 160), INK)
    ctext(d, 490, s["accent"], fit_font(d, s["accent"], PF_I, 110, W - 160), RUST)
    ctext(d, 620, s.get("line2", ""), fit_font(d, s.get("line2", "x"), PF, 110, W - 160), INK)
    d.line([(W / 2 - 50, 790), (W / 2 + 50, 790)], fill=GOLD, width=3)
    y = 840
    for l in wrap(d, s.get("quote", ""), font(PF_I, 44), W - 260):
        ctext(d, y, l, font(PF_I, 44), (90, 70, 50))
        y += 64
    dots = s.get("dots", ["#7f97c9", "#d4a42a", "#c75b4a", "#b5733b", "#5f8f4f"])
    x0 = W / 2 - (len(dots) * 50) / 2 + 25
    for k2, c in enumerate(dots):
        d.ellipse([x0 + k2 * 50 - 14, y + 40, x0 + k2 * 50 + 14, y + 68], fill=c)
    if s.get("swipe"):
        sw = " ".join(s["swipe"].upper()) + "  »"
        ctext(d, y + 120, sw, fit_font(d, sw, POP, 26, W - 200), (150, 120, 90))
    counter(d, i, n, (150, 120, 90))
    return im


def s_spotlight(s, i, n):
    im = img_of(s, i)
    grad = Image.linear_gradient("L").resize((W, H)).point(lambda v: int(220 * (v / 255) ** 2.2))
    im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, grad)
    d = ImageDraw.Draw(im)
    f = fit_font(d, s["name"], PF, 120, W - 160)
    d.text((90, H - 420), s["name"], font=f, fill=WHITE)
    d.line([(95, H - 270), (185, H - 270)], fill=GOLD, width=4)
    d.text((90, H - 240), s.get("local", ""), font=font(PF_I, 60), fill=WHITE)
    d.text((92, H - 155), s.get("latin", ""), font=font(PF_I, 36), fill=(225, 220, 210))
    counter(d, i, n)
    return im


def s_statement(s, i, n):
    im = img_of(s, i)

    def draw(d):
        words = s["big"].split()
        half = (len(words) + 1) // 2 if len(words) > 1 else 1
        l1, l2 = " ".join(words[:half]), " ".join(words[half:])
        f1 = fit_font(d, l1, POP_B, 230, W - 140)
        d.text((70, 230), l1, font=f1, fill=(255, 255, 255, 215))
        if l2:
            f2 = fit_font(d, l2, POP_B, 150, W - 140)
            d.text((70, 230 + f1.size), l2, font=f2, fill=(255, 255, 255, 215))
        fb, fr = font(POP_SB, 52), font(POP, 52)
        text = s.get("caption", "")
        lines = wrap(d, s.get("caption_bold", "") + " " + text, fr, W - 260)
        y0 = 770
        d.rectangle([80, y0, W - 80, y0 + len(lines) * 72 + 50], fill=(44, 36, 34, 240))
        for k, l in enumerate(lines):
            if k == 0 and s.get("caption_bold") and l.startswith(s["caption_bold"]):
                d.text((110, y0 + 25), s["caption_bold"], font=fb, fill=WHITE)
                d.text((110 + d.textlength(s["caption_bold"] + " ", font=fb), y0 + 25),
                       l[len(s["caption_bold"]) + 1:], font=fr, fill=WHITE)
            else:
                d.text((110, y0 + 25 + k * 72), l, font=fr, fill=WHITE)
    im = overlay(im, draw)
    counter(ImageDraw.Draw(im), i, n)
    return im


def s_labels(s, i, n):
    cols = s.get("colors", ["#d9c13a", "#c9a32e", "#b8902a", "#7f7f2c", "#6b6a2a"])[:6]
    im = scenes.make({"scene": "stack", "colors": cols, "seed": i})
    d = ImageDraw.Draw(im)
    tf = fit_font(d, s.get("title", ""), LORA_SB, 70, W - 200)
    tw = d.textlength(s.get("title", ""), font=tf)
    d.rectangle([60, 80, 60 + tw + 60, 80 + tf.size + 50], fill=(255, 255, 255))
    d.text((90, 100), s.get("title", ""), font=tf, fill=(20, 20, 20))
    nn = len(cols)
    slab = int(min(220, (H - 200) / nn))
    top = H - 120 - slab * nn
    lf = font(LORA_SB, 44)
    for k, lab in enumerate(s.get("labels", [])[:nn]):
        y = top + k * slab + slab // 2 - 30
        x = int(W * 0.40)
        lw = d.textlength(lab, font=lf)
        d.rectangle([x, y, x + lw + 40, y + 64], fill=(255, 255, 255))
        d.text((x + 20, y + 6), lab, font=lf, fill=(20, 20, 20))
    counter(d, i, n, (90, 80, 70))
    return im


def s_boxed(s, i, n):
    im = img_of(s, i)
    d = ImageDraw.Draw(im)
    f = font(LORA_SB, 84)
    y = 160
    for l in s.get("lines", []):
        w = d.textlength(l, font=f)
        x = W - 120 - w
        d.rectangle([x - 18, y - 6, x + w + 18, y + 100], fill=(0, 0, 0))
        d.text((x, y), l, font=f, fill=WHITE)
        y += 106
    f2 = font(LORA_SB, 52)
    y = max(y + 160, 900)
    for l in s.get("small", []):
        w = d.textlength(l, font=f2)
        x = W - 120 - w
        d.rectangle([x - 14, y - 4, x + w + 14, y + 66], fill=(0, 0, 0))
        d.text((x, y), l, font=f2, fill=WHITE)
        y += 70
    counter(d, i, n)
    return im


def s_point(s, i, n):
    im = Image.new("RGB", (W, H), CREAM)
    panel = img_of(s, i, (W, 700))
    im.paste(panel, (0, 0))
    d = ImageDraw.Draw(im)
    col = s.get("color", "#b85c38")
    d.text((90, 760), s.get("num", f"{i:02d}"), font=font(PF_I, 90), fill=col)
    y = 880
    for l in wrap(d, s["title"], font(PF, 76), W - 180):
        d.text((90, y), l, font=font(PF, 76), fill=INK)
        y += 92
    y += 20
    for l in wrap(d, s.get("body", ""), font(POP, 40), W - 180):
        d.text((90, y), l, font=font(POP, 40), fill=(95, 80, 65))
        y += 58
    counter(d, i, n, (150, 120, 90))
    return im


def s_end(s, i, n):
    im = Image.new("RGB", (W, H), (24, 30, 40))
    d = ImageDraw.Draw(im)
    pal = ["#1f3a6e", "#a3262f", "#d39b1c", "#6b4a2b", "#5f8f4f", "#c46a2f"]
    for k, c in enumerate(pal):
        d.ellipse([W / 2 - 165 + k * 66 - 20, 380, W / 2 - 165 + k * 66 + 20, 420], fill=c)
    ctext(d, 520, s.get("line1", "Colour from nature."), font(PF, 78), WHITE)
    ctext(d, 620, s.get("line2", "Made in Jaipur."), font(PF_I, 78), GOLD)
    d.line([(W / 2 - 45, 770), (W / 2 + 45, 770)], fill=GOLD, width=3)
    ctext(d, 820, "Sodhani Biotech", font(POP_SB, 54), WHITE)
    ctext(d, 900, "Natural dyes & dye extracts", font(POP, 36), (210, 205, 195))
    ctext(d, 1010, s.get("cta", "DM us for samples"), font(POP_SB, 44), GOLD)
    if s.get("contact"):
        ctext(d, 1080, s["contact"], fit_font(d, s["contact"], POP, 34, W - 160), (210, 205, 195))
    counter(d, i, n, (210, 205, 195))
    return im


def s_palette(s, i, n):
    """{"title": "Our Extracts (1/3)", "items": [{"name": "Mallow Gold", "sub": "Pomegranate peel", "color": "#abb45b"}, ... up to 9]}"""
    im = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(im)
    ctext(d, 90, s.get("title", ""), fit_font(d, s.get("title", "x"), PF, 76, W - 160), INK)
    d.line([(W / 2 - 50, 205), (W / 2 + 50, 205)], fill=GOLD, width=3)
    items = s["items"][:9]
    cols = 3
    cw, ch = (W - 120) / cols, 330
    for k, it in enumerate(items):
        cx = 60 + cw * (k % cols) + cw / 2
        cy = 260 + ch * (k // cols)
        r = 95
        d.ellipse([cx - r - 10, cy + 10, cx + r + 10, cy + 2 * r + 30], fill=(255, 255, 255))
        d.ellipse([cx - r, cy + 20, cx + r, cy + 2 * r + 20], fill=it["color"])
        nf = fit_font(d, it["name"], POP_SB, 32, cw - 20, 18)
        ctext(d, cy + 2 * r + 45, it["name"], nf, INK, cx - cw / 2, cx + cw / 2)
        sf = fit_font(d, it.get("sub", ""), POP, 26, cw - 20, 16)
        ctext(d, cy + 2 * r + 88, it.get("sub", ""), sf, (130, 105, 80), cx - cw / 2, cx + cw / 2)
    counter(d, i, n, (150, 120, 90))
    return im


def s_stats(s, i, n):
    """{"kicker": "PROOF", "stats": [{"big": "80%", "label": "lesser ETP cost", "sub": "..."}, ... 1-3], "color": "#4f7a3a", "note": "source line"}"""
    col = s.get("color", "#4f7a3a")
    im = Image.new("RGB", (W, H), col)
    d = ImageDraw.Draw(im)
    if s.get("kicker"):
        k = " ".join(s["kicker"].upper())
        ctext(d, 110, k, fit_font(d, k, POP_SB, 30, W - 160), (255, 255, 255))
    stats = s["stats"][:3]
    big = 300 if len(stats) == 1 else (190 if len(stats) == 2 else 150)
    block = (H - 360) / len(stats)
    for k, st in enumerate(stats):
        y = 220 + k * block + (block - big - 160) / 2
        bf = fit_font(d, st["big"], POP_B, big, W - 140)
        ctext(d, y, st["big"], bf, WHITE)
        ctext(d, y + bf.size + 10, st["label"], fit_font(d, st["label"], PF_I, 64, W - 160), (255, 236, 200))
        if st.get("sub"):
            sf = font(POP, 34)
            for j, l in enumerate(wrap(d, st["sub"], sf, W - 220)[:2]):
                ctext(d, y + bf.size + 100 + j * 46, l, sf, (240, 235, 225))
    if s.get("note"):
        ctext(d, H - 140, s["note"], fit_font(d, s["note"], POP, 26, W - 160), (230, 225, 215))
    counter(d, i, n, (240, 235, 225))
    return im


TYPES = {"series": s_series, "question": s_question, "education": s_education, "spotlight": s_spotlight,
         "statement": s_statement, "labels": s_labels, "boxed": s_boxed, "point": s_point, "end": s_end,
         "palette": s_palette, "stats": s_stats}


def render(spec, out_dir):
    slides = spec["slides"]
    if not 2 <= len(slides) <= 10:
        sys.exit("Instagram carousels need 2–10 slides")
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for i, s in enumerate(slides):
        im = TYPES[s["type"]](s, i, len(slides))
        p = os.path.join(out_dir, f"{i + 1:02d}.jpg")
        im.save(p, "JPEG", quality=90)
        paths.append(p)
    print("\n".join(paths))


if __name__ == "__main__":
    render(json.load(open(sys.argv[1])), sys.argv[2])
