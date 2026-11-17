#!/usr/bin/env python3
"""Render a comic strip (1080x1350, Instagram 4:5) from a JSON script.

Usage: python3 comic.py script.json out.jpg

Script format:
{
  "title": "optional small title",
  "panels": [                      # 3 panels = stacked rows, 4 panels = 2x2 grid
    {"bg": "room|park|office|night|plain",
     "chars": [{"name": "Benny", "x": 0.3, "pose": "stand", "face": "neutral", "flip": false}],
     "lines": [{"who": "Benny", "text": "..."}],          # speech bubbles, in order
     "caption": "optional narration box"}
  ]
}
names: Benny, Lula, Uncle Gjon, Mimi, Tito
poses: stand, wave, shrug, point, hips, jump, facepalm
faces: neutral, happy, angry, shock, sleepy, smug
"""
import json, sys, textwrap, random
from PIL import Image, ImageDraw
from characters import draw_character, font, INK

W, H = 1080, 1350
S = 2  # supersample
PAPER = (252, 250, 245)
BGS = {
    "plain": [(250, 246, 236)],
    "room": [(244, 232, 214), (226, 206, 178)],
    "park": [(212, 236, 250), (160, 210, 130)],
    "office": [(228, 234, 240), (196, 204, 214)],
    "night": [(46, 52, 92), (70, 70, 110)],
    "beach": [(200, 232, 250), (244, 222, 170)],
}
HANDLE = "@dailypost_dose"


def panel_bg(d, box, kind, rng):
    x0, y0, x1, y1 = box
    cols = BGS.get(kind, BGS["plain"])
    d.rectangle(box, fill=cols[0])
    if len(cols) > 1:
        gy = y0 + (y1 - y0) * 0.78
        d.rectangle([x0, gy, x1, y1], fill=cols[1])
        d.line([(x0, gy), (x1, gy)], fill=INK, width=3 * S)
    if kind == "night":
        for _ in range(12):
            sx, sy = rng.uniform(x0, x1), rng.uniform(y0, y0 + (y1 - y0) * 0.5)
            d.ellipse([sx - 3 * S, sy - 3 * S, sx + 3 * S, sy + 3 * S], fill=(250, 240, 180))
    if kind == "park":
        sx, sy = x1 - 70 * S, y0 + 60 * S
        d.ellipse([sx - 28 * S, sy - 28 * S, sx + 28 * S, sy + 28 * S], fill=(255, 214, 90))
    if kind == "office":
        wx = x0 + (x1 - x0) * 0.62
        d.rectangle([wx, y0 + 40 * S, wx + 120 * S, y0 + 130 * S], fill=(190, 222, 245), outline=INK, width=3 * S)


def bubble(d, text, anchor, box, fsize, prefer_y, placed):
    ax, ay = anchor
    x0, y0, x1, y1 = box
    f = font(fsize)
    maxw = (x1 - x0) * 0.62
    chars = max(8, int(maxw / (fsize * 0.55)))
    lines = textwrap.wrap(text, chars)
    lh = int(fsize * 1.2)
    tw = max(d.textlength(l, font=f) for l in lines)
    bw, bh = tw + 34 * S, lh * len(lines) + 26 * S
    bx = min(max(ax - bw / 2, x0 + 12 * S), x1 - bw - 12 * S)
    by = max(prefer_y, y0 + 12 * S)
    moved = True
    while moved:
        moved = False
        for (px0, py0, px1, py1) in placed:
            if bx < px1 + 8 * S and bx + bw > px0 - 8 * S and by < py1 + 8 * S and by + bh > py0 - 8 * S:
                by = py1 + 10 * S
                moved = True
    placed.append((bx, by, bx + bw, by + bh))
    # tail
    tx = min(max(ax, bx + 30 * S), bx + bw - 30 * S)
    d.polygon([(tx - 14 * S, by + bh - 4 * S), (tx + 14 * S, by + bh - 4 * S), (ax, ay - 8 * S)], fill="white", outline=INK)
    d.line([(tx - 14 * S, by + bh - 2 * S), (ax, ay - 8 * S), (tx + 14 * S, by + bh - 2 * S)], fill=INK, width=3 * S)
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=22 * S, fill="white", outline=INK, width=3 * S)
    d.polygon([(tx - 11 * S, by + bh - 4 * S), (tx + 11 * S, by + bh - 4 * S), (tx, by + bh + 4 * S)], fill="white")
    for i, l in enumerate(lines):
        d.text((bx + (bw - d.textlength(l, font=f)) / 2, by + 12 * S + i * lh), l, font=f, fill=INK)
    return by + bh


def render(script, out):
    rng = random.Random(json.dumps(script))
    img = Image.new("RGB", (W * S, H * S), PAPER)
    d = ImageDraw.Draw(img)
    panels = script["panels"]
    m, gap = 30 * S, 22 * S
    top = m
    if script.get("title"):
        f = font(44 * S)
        t = script["title"]
        d.text(((W * S - d.textlength(t, font=f)) / 2, 18 * S), t, font=f, fill=INK)
        top = 92 * S
    foot = 60 * S
    usable_h = H * S - top - foot
    boxes = []
    if len(panels) == 4:
        pw = (W * S - 2 * m - gap) / 2
        ph = (usable_h - gap) / 2
        for i in range(4):
            r, c = divmod(i, 2)
            x0 = m + c * (pw + gap); y0 = top + r * (ph + gap)
            boxes.append((x0, y0, x0 + pw, y0 + ph))
    else:
        n = len(panels)
        ph = (usable_h - gap * (n - 1)) / n
        for i in range(n):
            y0 = top + i * (ph + gap)
            boxes.append((m, y0, W * S - m, y0 + ph))

    for p, box in zip(panels, boxes):
        x0, y0, x1, y1 = box
        panel_bg(d, box, p.get("bg", "plain"), rng)
        ph = y1 - y0
        ground = y1 - ph * 0.08
        ch_h = ph * (0.5 if len(panels) == 4 else 0.52)
        heads = {}
        for c in p.get("chars", []):
            cx = x0 + (x1 - x0) * c.get("x", 0.5)
            heads[c["name"]] = draw_character(img, cx, ground, c["name"], height=ch_h, pose=c.get("pose", "stand"),
                                              face=c.get("face", "neutral"), flip=c.get("flip", False), seed=int(cx))
        d = ImageDraw.Draw(img)
        prefer = y0 + 12 * S
        placed = []
        cap = p.get("caption")
        if cap:
            f = font(int(24 * S))
            tw = d.textlength(cap, font=f)
            d.rectangle([x0, y0, x0 + tw + 30 * S, y0 + 44 * S], fill=(255, 230, 120), outline=INK, width=3 * S)
            d.text((x0 + 15 * S, y0 + 6 * S), cap, font=f, fill=INK)
            placed.append((x0, y0, x0 + tw + 30 * S, y0 + 44 * S))
        fsize = int((26 if len(panels) == 4 else 30) * S)
        for ln in p.get("lines", []):
            hx, hy = heads.get(ln["who"], ((x0 + x1) / 2, y0 + ph * 0.4))
            bubble(d, ln["text"], (hx, hy), box, fsize, prefer, placed)
        d.rectangle(box, outline=INK, width=5 * S)

    f = font(26 * S, bold=False)
    d.text(((W * S - d.textlength(HANDLE, font=f)) / 2, H * S - 48 * S), HANDLE, font=f, fill=(110, 110, 110))
    img.resize((W, H), Image.LANCZOS).save(out, "JPEG", quality=93)


if __name__ == "__main__":
    render(json.load(open(sys.argv[1])), sys.argv[2])
    print(sys.argv[2])
