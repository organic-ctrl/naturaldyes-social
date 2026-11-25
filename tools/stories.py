"""Second daily story for @naturaldye.sbpl: a different TYPE every day (1080x1920 JPEG).

  python3 tools/stories.py SPEC.json OUT.jpg

SPEC = {"type": ..., ...}. Types and fields:
  news        {"topic": "dye" | "food", "headline", "summary", "source": "Outlet · 20 Nov 2026", "ask"}
              "Natural Dye News" / "Natural Food Colour News" bulletin. REAL news only, paraphrased, source named.
  didyouknow  {"fact", "detail", "color"}            big question mark on a colour field + one fact
  mythfact    {"myth", "fact"}                         red MYTH half over a green FACT half
  spotlight   {"name", "source", "latin", "color", "note"}   one product on a big swatch of its shade hex
  thisorthat  {"question", "a": {"name", "color"}, "b": {"name", "color"}}   two colour halves, "reply with your pick"
  stat        {"big": "95%", "label", "detail", "color"}     one big company number
"""
import json, os, sys, datetime
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FD = os.path.join(os.path.dirname(__file__), "fonts")
P = lambda f: os.path.join(FD, f)  # noqa: E731
PF, PF_I, POP, POP_SB, POP_B = P("Playfair-Medium.ttf"), P("Playfair-Italic.ttf"), P("Poppins-Regular.ttf"), \
    P("Poppins-SemiBold.ttf"), P("Poppins-Bold.ttf")
CREAM, INK, GOLD, RED, GREEN = (246, 238, 225), (40, 31, 23), (214, 164, 64), (168, 50, 45), (79, 122, 58)
HANDLE = "@naturaldye.sbpl"
_f = {}


def font(p, s):
    if (p, s) not in _f:
        _f[(p, s)] = ImageFont.truetype(p, s)
    return _f[(p, s)]


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def light(c):
    return sum(c) / 3 > 150


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


def para(d, x, y, text, f, fill, maxw, gap=1.3, center=False):
    for l in wrap(d, text, f, maxw):
        xx = x + (maxw - d.textlength(l, font=f)) / 2 if center else x
        d.text((xx, y), l, font=f, fill=fill)
        y += int(f.size * gap)
    return y


def fit(d, text, path, start, maxw, maxlines, min_size=40):
    s = start
    while s > min_size and len(wrap(d, text, font(path, s), maxw)) > maxlines:
        s -= 4
    return font(path, s)


def footer(d, fg=(250, 245, 235), sub=(217, 201, 176)):
    d.text((90, H - 130), "SODHANI BIOTECH · JAIPUR", font=font(POP_SB, 32), fill=fg)
    d.text((90, H - 84), f"Natural dyes & dye extracts  |  {HANDLE}", font=font(POP, 28), fill=sub)


def pill(d, x, y, text, bg, fg, f):
    w = d.textlength(text, font=f)
    d.rounded_rectangle([x, y, x + w + 56, y + f.size + 34], 40, fill=bg)
    d.text((x + 28, y + 12), text, font=f, fill=fg)
    return y + f.size + 34


# ---------------------------------------------------------------- types
def t_news(s):
    food = s.get("topic") == "food"
    accent = (196, 106, 47) if food else (60, 88, 172)
    im = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(im)
    for i, c in enumerate([(31, 58, 104), (168, 50, 45), (217, 162, 27), (107, 74, 43), (79, 122, 58), (196, 106, 47)]):
        d.rectangle([i * W // 6, 0, (i + 1) * W // 6, 22], fill=c)
    y = pill(d, 90, 170, "NATURAL FOOD COLOUR NEWS" if food else "NATURAL DYE NEWS", accent, (255, 255, 255),
             font(POP_SB, 34))
    d.text((90, y + 30), datetime.date.today().strftime("%d %b %Y").upper() if not s.get("date") else s["date"],
           font=font(POP, 30), fill=(190, 175, 150))
    f = fit(d, s["headline"], PF, 92, W - 180, 6, 56)
    y = para(d, 90, y + 120, s["headline"], f, (252, 246, 236), W - 180, 1.22)
    d.rectangle([90, y + 30, 250, y + 38], fill=GOLD)
    y = para(d, 90, y + 90, s["summary"], font(POP, 42), (225, 214, 196), W - 180, 1.45)
    para(d, 90, y + 40, "Source: " + s["source"], font(PF_I, 36), GOLD, W - 180, 1.3)
    ask = s.get("ask", "What do you think? Reply in DMs")
    box_y = H - 420
    d.rounded_rectangle([90, box_y, W - 90, box_y + 170], 30, fill=(252, 246, 236))
    f2 = fit(d, ask, POP_SB, 44, W - 280, 2, 32)
    para(d, 140, box_y + (170 - len(wrap(d, ask, f2, W - 280)) * int(f2.size * 1.3)) / 2, ask, f2, INK, W - 280,
         center=True)
    footer(d)
    return im


def t_didyouknow(s):
    c = rgb(s.get("color", "#4f7a3a"))
    im = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 900], fill=c)
    fg = INK if light(c) else (255, 255, 255)
    d.text((W // 2, 450), "?", font=font(PF, 620), fill=fg, anchor="mm")
    y = pill(d, 90, 960, "DID YOU KNOW?", INK, CREAM, font(POP_SB, 34))
    f = fit(d, s["fact"], PF, 76, W - 180, 5, 50)
    y = para(d, 90, y + 50, s["fact"], f, INK, W - 180, 1.25)
    para(d, 90, y + 40, s.get("detail", ""), font(POP, 38), (80, 66, 52), W - 180, 1.45)
    d.rectangle([0, H - 180, W, H], fill=INK)
    footer(d)
    return im


def t_mythfact(s):
    im = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(im)
    half = (H - 180) // 2
    d.rectangle([0, 0, W, half], fill=(236, 214, 206))
    d.rectangle([0, half, W, H - 180], fill=(214, 228, 204))
    for y0, label, col, txt in ((0, "MYTH", RED, s["myth"]), (half, "FACT", GREEN, s["fact"])):
        d.text((90, y0 + 110), label, font=font(POP_B, 120), fill=col)
        f = fit(d, txt, PF, 64, W - 180, 6, 42)
        para(d, 90, y0 + 300, txt, f, INK, W - 180, 1.3)
    d.rectangle([0, H - 180, W, H], fill=INK)
    footer(d)
    return im


def t_spotlight(s):
    c = rgb(s["color"])
    im = Image.new("RGB", (W, H), c)
    d = ImageDraw.Draw(im)
    # soft vertical gradient to depth
    for y in range(H):
        a = y / H * 0.35
        d.line([(0, y), (W, y)], fill=tuple(int(v * (1 - a)) for v in c))
    d.rounded_rectangle([70, 820, W - 70, H - 230], 40, fill=(252, 246, 236))
    pill(d, 90, 170, "PRODUCT SPOTLIGHT", INK, CREAM, font(POP_SB, 34))
    f = fit(d, s["name"], PF, 96, W - 260, 2, 56)
    y = para(d, 130, 890, s["name"], f, INK, W - 260, 1.15)
    d.rectangle([130, y + 20, 290, y + 28], fill=GOLD)
    y += 70
    d.text((130, y), s.get("source", ""), font=font(POP_SB, 42), fill=(80, 66, 52))
    d.text((130, y + 64), s.get("latin", ""), font=font(PF_I, 42), fill=(120, 100, 80))
    para(d, 130, y + 160, s.get("note", ""), font(POP, 38), (80, 66, 52), W - 260, 1.45)
    d.rectangle([0, H - 180, W, H], fill=INK)
    footer(d)
    return im


def t_thisorthat(s):
    im = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(im)
    top = 520
    for k, opt in enumerate((s["a"], s["b"])):
        c = rgb(opt["color"])
        x0 = k * W // 2
        d.rectangle([x0, top, x0 + W // 2, H - 380], fill=c)
        fg = INK if light(c) else (255, 255, 255)
        mw = W // 2 - 220
        f = fit(d, opt["name"], PF, 64, mw, 3, 40)
        lines = wrap(d, opt["name"], f, mw)
        y = (top + H - 380) // 2 - 130 - len(lines) * f.size * 1.3
        para(d, x0 + 110, y, opt["name"], f, fg, mw, 1.3, center=True)
    d.ellipse([W // 2 - 80, (top + H - 380) // 2 - 80, W // 2 + 80, (top + H - 380) // 2 + 80], fill=CREAM)
    d.text((W // 2, (top + H - 380) // 2), "or", font=font(PF_I, 70), fill=INK, anchor="mm")
    pill(d, 90, 150, "THIS OR THAT", INK, CREAM, font(POP_SB, 34))
    f = fit(d, s["question"], PF, 70, W - 180, 3, 44)
    para(d, 90, 270, s["question"], f, INK, W - 180, 1.2)
    para(d, 90, H - 330, "Reply to this story with your pick", font(POP_SB, 40), INK, W - 180, center=True)
    d.rectangle([0, H - 180, W, H], fill=INK)
    footer(d)
    return im


def t_stat(s):
    c = rgb(s.get("color", "#2f6f86"))
    im = Image.new("RGB", (W, H), c)
    d = ImageDraw.Draw(im)
    fg = INK if light(c) else (255, 255, 255)
    pill(d, 90, 170, "BY THE NUMBERS", INK if not light(c) else (255, 255, 255), CREAM if not light(c) else INK,
         font(POP_SB, 34))
    f = fit(d, s["big"], POP_B, 330, W - 180, 1, 120)
    d.text((W // 2, 760), s["big"], font=f, fill=fg, anchor="mm")
    y = para(d, 90, 1000, s["label"], font(PF, 72), fg, W - 180, 1.2, center=True)
    para(d, 120, y + 50, s.get("detail", ""), font(POP, 40), fg, W - 240, 1.45, center=True)
    d.rectangle([0, H - 180, W, H], fill=INK)
    footer(d)
    return im


TYPES = {"news": t_news, "didyouknow": t_didyouknow, "mythfact": t_mythfact, "spotlight": t_spotlight,
         "thisorthat": t_thisorthat, "stat": t_stat}

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    TYPES[spec["type"]](spec).save(out, "JPEG", quality=90)
    print(out)
