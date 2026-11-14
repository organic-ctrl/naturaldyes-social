"""Story-highlight covers (1080x1920). Instagram shows the centre as a circle, so the icon sits in the middle.

  python3 tools/highlights.py OUT_DIR
"""
import math, os, sys
from PIL import Image, ImageDraw

W, H = 1080, 1920
CX, CY = W // 2, H // 2
WHITE = (250, 246, 238)
LW = 22

COVERS = [  # (file, label, background = a product shade, slightly deepened)
    ("01-products", "Products", "#3c58ac"),      # Esstebio Indigo Blue
    ("02-extracts", "Extracts", "#c11172"),      # Wine Red 3001
    ("03-mordants", "Mordants", "#868885"),      # Cedar Grey
    ("04-shades", "Shade Card", "#f57818"),      # Candy Orange Deep
    ("05-sustainability", "Sustainable", "#5a9a57"),  # Olive Green
    ("06-process", "Process", "#be775a"),        # Michigan Brown
    ("07-reviews", "Reviews", "#c9a227"),        # Mallow Gold / onion yellow
    ("08-contact", "Contact", "#2b2118"),        # brand ink
]


def ring(d, r, w=LW):
    d.ellipse([CX - r, CY - r, CX + r, CY + r], outline=WHITE, width=w)


def icon(d, name):
    s = 150
    if name == "01-products":  # jar
        d.rounded_rectangle([CX - s, CY - s + 60, CX + s, CY + s + 40], 40, outline=WHITE, width=LW)
        d.rounded_rectangle([CX - s + 40, CY - s, CX + s - 40, CY - s + 60], 14, outline=WHITE, width=LW)
        d.line([(CX - s + 60, CY + 40), (CX + s - 60, CY + 40)], fill=WHITE, width=LW)
    elif name == "02-extracts":  # drop
        pts = []
        for k in range(0, 361, 6):
            a = math.radians(k)
            r = s * 0.95
            x = CX + r * math.sin(a) * (1 - 0.0 * math.cos(a))
            y = CY + 50 - r * math.cos(a) * 0.9
            if 150 < k < 210:
                continue
            pts.append((x, y))
        d.line([(CX, CY - s - 90)] + [(CX + s * 0.95 * math.sin(math.radians(k)), CY + 50 + s * 0.95 * math.cos(math.radians(k)))
                                      for k in range(-120, 121, 4)] + [(CX, CY - s - 90)], fill=WHITE, width=LW, joint="curve")
    elif name == "03-mordants":  # flask
        d.line([(CX - 50, CY - s - 30), (CX - 50, CY - 40), (CX - s - 20, CY + s + 20), (CX + s + 20, CY + s + 20),
                (CX + 50, CY - 40), (CX + 50, CY - s - 30)], fill=WHITE, width=LW, joint="curve")
        d.line([(CX - 80, CY - s - 30), (CX + 80, CY - s - 30)], fill=WHITE, width=LW)
        d.line([(CX - 120, CY + 90), (CX + 120, CY + 90)], fill=WHITE, width=LW)
    elif name == "04-shades":  # swatch fan
        for k, ang in enumerate((-40, -20, 0, 20, 40)):
            a = math.radians(ang)
            x2, y2 = CX + math.sin(a) * 260, CY + 160 - math.cos(a) * 260
            d.line([(CX, CY + 160), (x2, y2)], fill=WHITE, width=46 if k == 2 else 34)
        d.ellipse([CX - 30, CY + 130, CX + 30, CY + 190], fill=WHITE)
    elif name == "05-sustainability":  # leaf with stem and veins
        L = 380
        pts = []
        for k in range(0, 41):
            t = k / 40
            pts.append((t * L, math.sin(math.pi * t) ** 0.8 * 120))
        pts += [(x, -y) for x, y in reversed(pts)]
        a = math.radians(-45)
        ox, oy = CX - 150, CY + 150
        tr = lambda x, y: (ox + x * math.cos(a) - y * math.sin(a), oy + x * math.sin(a) + y * math.cos(a))  # noqa: E731
        d.line([tr(x, y) for x, y in pts], fill=WHITE, width=LW, joint="curve")
        d.line([tr(-50, 0), tr(L * 0.85, 0)], fill=WHITE, width=LW)
        for t in (0.3, 0.5, 0.7):
            d.line([tr(t * L, 0), tr(t * L + 60, 70)], fill=WHITE, width=12)
            d.line([tr(t * L, 0), tr(t * L + 60, -70)], fill=WHITE, width=12)
    elif name == "06-process":  # cycle arrows
        d.arc([CX - s, CY - s, CX + s, CY + s], 200, 340, fill=WHITE, width=LW)
        d.arc([CX - s, CY - s, CX + s, CY + s], 20, 160, fill=WHITE, width=LW)
        for ang in (340, 160):
            a = math.radians(ang)
            x, y = CX + s * math.cos(a), CY + s * math.sin(a)
            d.polygon([(x - 45, y - 10), (x + 45, y - 10), (x, y + 55)] if ang == 340 else
                      [(x - 45, y + 10), (x + 45, y + 10), (x, y - 55)], fill=WHITE)
    elif name == "07-reviews":  # star
        pts = []
        for k in range(10):
            r = 190 if k % 2 == 0 else 80
            a = math.radians(-90 + k * 36)
            pts.append((CX + r * math.cos(a), CY + 10 + r * math.sin(a)))
        d.line(pts + [pts[0]], fill=WHITE, width=LW, joint="curve")
    elif name == "08-contact":  # envelope
        d.rounded_rectangle([CX - 190, CY - 120, CX + 190, CY + 130], 20, outline=WHITE, width=LW)
        d.line([(CX - 180, CY - 110), (CX, CY + 20), (CX + 180, CY - 110)], fill=WHITE, width=LW, joint="curve")


def main(out):
    os.makedirs(out, exist_ok=True)
    for name, _, bg in COVERS:
        im = Image.new("RGB", (W, H), bg)
        d = ImageDraw.Draw(im)
        ring(d, 330, 8)
        icon(d, name)
        im.save(os.path.join(out, name + ".jpg"), quality=92)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1])
