"""Make Instagram media for @naturaldye.sbpl (Sodhani Biotech).

Usage:
  python3 tools/make_media.py post  OUT.jpg "KICKER" "TITLE" "BODY"
  python3 tools/make_media.py story OUT.jpg "KICKER" "TITLE" "BODY"
  python3 tools/make_media.py reel  OUT.mp4 "HOOK" "POINT 1" "POINT 2" "CTA"

post  = 1080x1350 JPEG (4:5 feed)
story = 1080x1920 JPEG (9:16)
reel  = 1080x1920 MP4, ~14 s, H.264 + silent AAC, 4 animated slides
"""
import os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/"
SERIF_B = FONT + "DejaVuSerif-Bold.ttf"
SANS = FONT + "DejaVuSans.ttf"
SANS_B = FONT + "DejaVuSans-Bold.ttf"
CREAM, INK, BROWN, GREEN = "#f4ecdf", "#2b2118", "#8a5a2b", "#4f7a3a"
SWATCH = ["#1f3a68", "#a8322d", "#d9a21b", "#6b4a2b", "#4f7a3a", "#c46a2f"]


def wrap(d, text, font, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def card(W, H, kicker, title, body, band=330, accent_idx=None):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    if accent_idx is None:
        sw = W / len(SWATCH)
        for i, c in enumerate(SWATCH):
            d.rectangle([int(i * sw), 0, int((i + 1) * sw), band], fill=c)
    else:
        d.rectangle([0, 0, W, band], fill=SWATCH[accent_idx % len(SWATCH)])
    y = band + 70
    d.text((90, y), kicker.upper(), font=ImageFont.truetype(SANS_B, 34), fill=BROWN)
    y += 60
    f2 = ImageFont.truetype(SERIF_B, 78 if H < 1600 else 88)
    for l in wrap(d, title, f2, W - 180):
        d.text((90, y), l, font=f2, fill=INK)
        y += f2.size + 18
    y += 30
    d.rectangle([90, y, 250, y + 8], fill=GREEN)
    y += 50
    f3 = ImageFont.truetype(SANS, 40 if H < 1600 else 46)
    for l in wrap(d, body, f3, W - 180):
        d.text((90, y), l, font=f3, fill="#3d3328")
        y += f3.size + 18
    d.rectangle([0, H - 150, W, H], fill=INK)
    d.text((90, H - 115), "SODHANI BIOTECH · JAIPUR", font=ImageFont.truetype(SANS_B, 34), fill=CREAM)
    d.text((90, H - 68), "Natural dyes & dye extracts  |  @naturaldye.sbpl",
           font=ImageFont.truetype(SANS, 30), fill="#d9c9b0")
    return img


def reel(out, slides):
    W, H = 1080, 1920
    kickers = ["Natural dyes", "Did you know?", "Here's how", "Sodhani Biotech"]
    tmp = tempfile.mkdtemp()
    paths = []
    for i, text in enumerate(slides):
        img = card(W, H, kickers[min(i, 3)], text, "", band=700, accent_idx=i * 2)
        p = os.path.join(tmp, f"s{i}.png")
        img.save(p)
        paths.append(p)
    dur, fade = 3.5, 0.5
    inputs = []
    for p in paths:
        inputs += ["-loop", "1", "-t", str(dur), "-i", p]
    n = len(paths)
    filt = ""
    for i in range(n):
        filt += f"[{i}:v]scale={W}:{H},fps=30,format=yuv420p,setsar=1[v{i}];"
    last = "v0"
    off = dur - fade
    for i in range(1, n):
        filt += f"[{last}][v{i}]xfade=transition=fade:duration={fade}:offset={off:.2f}[x{i}];"
        last = f"x{i}"
        off += dur - fade
    filt = filt.rstrip(";")
    total = dur * n - fade * (n - 1)
    cmd = ["ffmpeg", "-y", *inputs, "-f", "lavfi", "-t", f"{total:.2f}", "-i",
           "anullsrc=r=44100:cl=stereo", "-filter_complex", filt, "-map", f"[{last}]",
           "-map", f"{n}:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True, capture_output=True)


if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    if mode == "post":
        card(1080, 1350, *sys.argv[3:6]).save(out, "JPEG", quality=90)
    elif mode == "story":
        card(1080, 1920, *sys.argv[3:6], band=600).save(out, "JPEG", quality=90)
    elif mode == "reel":
        reel(out, sys.argv[3:7])
    else:
        sys.exit("mode must be post, story or reel")
    print(out)
