"""Original doodle cast for the joke/poster agent.

draw_character(img, cx, ground_y, name, height=600, pose="stand", face="neutral", flip=False)
Draws on a PIL RGB image. Everything is plain shapes with a slightly wobbly marker line.
"""
import math, random
from PIL import Image, ImageDraw, ImageFont

INK = (25, 22, 20)
SKIN = [(242, 214, 188), (224, 182, 146), (186, 134, 96), (140, 96, 66)]

CAST = {
    # name: body colour, skin, head shape, touch
    "Benny": dict(body=(46, 160, 168), skin=0, head="round", touch="glasses", hair="tuft",
                  bio="The overthinker. Has a plan B for his plan B."),
    "Lula": dict(body=(247, 196, 52), skin=1, head="round", touch="bun_bow", hair="bun", dress=True,
                 bio="Sassy, always right, never wrong (ask her)."),
    "Uncle Gjon": dict(body=(214, 64, 52), skin=0, head="wide", touch="mustache_cap", hair=None,
                       bio="King of dad jokes. Nobody asked."),
    "Mimi": dict(body=(142, 92, 196), skin=2, head="round", touch="headphones", hair="ponytail",
                 bio="Professional napper. Allergic to Mondays."),
    "Tito": dict(body=(92, 178, 84), skin=3, head="tall", touch="sprout", hair=None,
                 bio="The optimist. Literally growing every day."),
}


def _wobble(pts, rng, amt):
    out = []
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        steps = max(2, int(math.hypot(x1 - x0, y1 - y0) / 18))
        for s in range(steps):
            t = s / steps
            out.append((x0 + (x1 - x0) * t + rng.uniform(-amt, amt), y0 + (y1 - y0) * t + rng.uniform(-amt, amt)))
    out.append(pts[-1])
    return out


def _line(d, pts, w, rng, amt=0.8, fill=INK):
    p = _wobble(pts, rng, amt)
    d.line(p, fill=fill, width=w, joint="curve")
    r = w / 2
    for x, y in (p[0], p[-1]):
        d.ellipse([x - r, y - r, x + r, y + r], fill=fill)


def _ellipse_pts(cx, cy, rx, ry, n=60, rng=None, amt=0.0):
    pts = []
    for i in range(n + 1):
        a = 2 * math.pi * i / n
        j = rng.uniform(-amt, amt) if rng else 0
        pts.append((cx + (rx + j) * math.cos(a), cy + (ry + j) * math.sin(a)))
    return pts


def draw_character(img, cx, ground, name, height=600, pose="stand", face="neutral", flip=False, seed=1):
    spec = CAST[name]
    rng = random.Random(seed + hash(name) % 1000)
    d = ImageDraw.Draw(img)
    u = height / 100.0          # unit
    W = max(3, int(1.6 * u))   # line width
    sgn = -1 if flip else 1

    leg_h, body_h = 30 * u, 30 * u
    head_rx = {"round": 15, "wide": 17, "tall": 13}[spec["head"]] * u
    head_ry = {"round": 15, "wide": 14, "tall": 17}[spec["head"]] * u
    hip_y = ground - leg_h
    sh_y = hip_y - body_h
    head_cy = sh_y - head_ry * 0.85

    # legs
    lx = 5 * u
    if pose == "jump":
        _line(d, [(cx - lx, hip_y), (cx - lx - 6 * u, hip_y + 18 * u), (cx - lx - 2 * u, ground - 4 * u)], W, rng)
        _line(d, [(cx + lx, hip_y), (cx + lx + 6 * u, hip_y + 18 * u), (cx + lx + 2 * u, ground - 4 * u)], W, rng)
    else:
        _line(d, [(cx - lx, hip_y), (cx - lx - 1.5 * u, ground)], W, rng)
        _line(d, [(cx + lx, hip_y), (cx + lx + 1.5 * u, ground)], W, rng)
        for fx in (cx - lx - 1.5 * u, cx + lx + 1.5 * u):  # little feet
            _line(d, [(fx - 2.5 * u, ground), (fx + 2.5 * u * (1 if fx > cx else -0.2), ground)], W, rng)

    # arms (drawn before body so shoulders tuck under)
    bw = 13 * u
    arms = {
        "stand": [((-1, 0.15), (-1.35, 0.55), (-1.2, 0.95)), ((1, 0.15), (1.35, 0.55), (1.2, 0.95))],
        "wave": [((-1, 0.15), (-1.35, 0.55), (-1.2, 0.95)), ((1, 0.15), (1.7, -0.35), (1.9, -0.95))],
        "shrug": [((-1, 0.15), (-1.8, 0.3), (-2.1, -0.15)), ((1, 0.15), (1.8, 0.3), (2.1, -0.15))],
        "point": [((-1, 0.15), (-1.35, 0.55), (-1.2, 0.95)), ((1, 0.2), (1.9, 0.15), (2.7, 0.05))],
        "hips": [((-1, 0.15), (-1.7, 0.45), (-1, 0.75)), ((1, 0.15), (1.7, 0.45), (1, 0.75))],
        "jump": [((-1, 0.15), (-1.7, -0.4), (-2.0, -0.95)), ((1, 0.15), (1.7, -0.4), (2.0, -0.95))],
        "facepalm": [((-1, 0.15), (-1.35, 0.55), (-1.2, 0.95)), ((1, 0.15), (1.2, -0.3), (0.3, -0.75))],
    }[pose]
    for arm in arms:
        pts = [(cx + sgn * ax * bw, sh_y + ay * body_h) for ax, ay in arm]
        _line(d, pts, W, rng)

    # body
    if spec.get("dress"):
        poly = [(cx - bw * 0.8, sh_y), (cx + bw * 0.8, sh_y), (cx + bw * 1.25, hip_y + 2 * u), (cx - bw * 1.25, hip_y + 2 * u)]
    else:
        poly = [(cx - bw, sh_y + 2 * u), (cx + bw, sh_y + 2 * u), (cx + bw * 1.05, hip_y), (cx - bw * 1.05, hip_y)]
    d.polygon(poly, fill=spec["body"])
    shade = tuple(int(c * 0.85) for c in spec["body"])
    d.polygon([poly[1], (poly[1][0] - 4 * u, poly[1][1]), (poly[2][0] - 5 * u, poly[2][1]), poly[2]], fill=shade)
    _line(d, poly + [poly[0]], W, rng, 0.6)

    # touches behind the head
    if spec["hair"] == "ponytail":
        px = cx - sgn * head_rx * 0.95
        d.ellipse([px - 7 * u, head_cy - 6 * u, px + 3 * u, head_cy + 10 * u], fill=(60, 40, 30))
        _line(d, _ellipse_pts(px - 2 * u, head_cy + 2 * u, 5 * u, 8 * u, 30), W, rng, 0.4)

    # head
    skin = SKIN[spec["skin"]]
    d.ellipse([cx - head_rx, head_cy - head_ry, cx + head_rx, head_cy + head_ry], fill=skin)
    mask = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([cx - head_rx, head_cy - head_ry, cx + head_rx, head_cy + head_ry], fill=255)
    cut = ImageDraw.Draw(Image.new("L", (1, 1)))
    md.ellipse([cx - head_rx * 1.35 + sgn * head_rx * -0.0, head_cy - head_ry * 1.2,
                cx + head_rx * 0.7, head_cy + head_ry * 1.2], fill=0) if sgn > 0 else \
        md.ellipse([cx - head_rx * 0.7, head_cy - head_ry * 1.2, cx + head_rx * 1.35, head_cy + head_ry * 1.2], fill=0)
    img.paste(tuple(int(c * 0.92) for c in skin), (0, 0), mask)
    _line(d, _ellipse_pts(cx, head_cy, head_rx, head_ry, 70, rng, 0.25 * u), W, rng, 0.3)

    # face
    ex = 5 * u * sgn
    ey = head_cy + 1 * u
    er = 1.4 * u
    fx0 = cx + 1.5 * u * sgn
    for e in (fx0 - ex * 0.9, fx0 + ex * 0.9):
        if face == "sleepy":
            _line(d, [(e - 2 * u, ey), (e + 2 * u, ey)], int(W * 0.8), rng, 0.2)
        else:
            d.ellipse([e - er, ey - er, e + er, ey + er], fill=INK)
    brow = {"neutral": (0, 0), "happy": (-1, 1), "angry": (2, -2), "shock": (-2.5, 2.5), "sleepy": (1, 1), "smug": (2, -1)}[face]
    for i, e in enumerate((fx0 - ex * 0.9, fx0 + ex * 0.9)):
        tilt = brow[1] if i == 0 else -brow[1]
        y0 = ey - 5 * u + brow[0] * u * 0.5
        _line(d, [(e - 2.2 * u, y0 + tilt * 0.4 * u), (e + 2.2 * u, y0 - tilt * 0.4 * u)], int(W * 0.7), rng, 0.2)
    my = head_cy + 7 * u
    if face == "happy":
        d.arc([fx0 - 4 * u, my - 4 * u, fx0 + 4 * u, my + 2 * u], 20, 160, fill=INK, width=int(W * 0.8))
    elif face == "shock":
        d.ellipse([fx0 - 2 * u, my - 2 * u, fx0 + 2 * u, my + 3 * u], fill=INK)
    elif face == "angry":
        d.arc([fx0 - 3.5 * u, my, fx0 + 3.5 * u, my + 5 * u], 200, 340, fill=INK, width=int(W * 0.8))
    elif face == "smug":
        d.arc([fx0 - 1 * u, my - 4 * u, fx0 + 4 * u, my + 1 * u], 20, 120, fill=INK, width=int(W * 0.8))
    elif face == "sleepy":
        _line(d, [(fx0 - 1.5 * u, my), (fx0 + 1.5 * u, my)], int(W * 0.7), rng, 0.2)
    # blush
    if name in ("Lula", "Mimi"):
        for e in (fx0 - ex * 1.3, fx0 + ex * 1.3):
            d.ellipse([e - 2.2 * u, ey + 2.5 * u, e + 2.2 * u, ey + 4.5 * u], fill=(240, 150, 150))

    # signature touches
    t = spec["touch"]
    top = head_cy - head_ry
    if spec["hair"] == "tuft":
        for k in (-2, 0, 2):
            _line(d, [(cx + k * u, top + 1 * u), (cx + k * 1.8 * u + 1 * u, top - 4 * u)], W, rng, 0.3)
    if t == "glasses":
        for e in (fx0 - ex * 0.9, fx0 + ex * 0.9):
            _line(d, _ellipse_pts(e, ey, 3.6 * u, 3.6 * u, 30), int(W * 0.8), rng, 0.2)
        _line(d, [(fx0 - ex * 0.9 + 3.6 * u * sgn, ey), (fx0 + ex * 0.9 - 3.6 * u * sgn, ey)], int(W * 0.8), rng, 0.1)
    elif t == "bun_bow":
        d.ellipse([cx - 5 * u, top - 8 * u, cx + 5 * u, top + 1 * u], fill=(70, 45, 30))
        _line(d, _ellipse_pts(cx, top - 3.5 * u, 5 * u, 4.5 * u, 30), W, rng, 0.2)
        bx, by = cx + 5 * u, top - 3 * u
        d.polygon([(bx, by), (bx + 6 * u, by - 4 * u), (bx + 6 * u, by + 4 * u)], fill=(232, 72, 120))
        d.polygon([(bx, by), (bx - 3 * u, by - 4 * u), (bx - 3 * u, by + 4 * u)], fill=(232, 72, 120))
        _line(d, [(bx, by), (bx + 6 * u, by - 4 * u), (bx + 6 * u, by + 4 * u), (bx, by)], int(W * 0.7), rng, 0.1)
    elif t == "mustache_cap":
        d.chord([cx - head_rx * 0.95, top - 2 * u, cx + head_rx * 0.95, top + head_ry * 1.0], 180, 360, fill=(40, 70, 150))
        by0 = top + head_ry * 0.42
        brim = [(cx, by0), (cx + sgn * head_rx * 1.4, by0 + 1 * u), (cx + sgn * head_rx * 1.4, by0 + 3 * u), (cx, by0 + 3 * u)]
        d.polygon(brim, fill=(30, 55, 125))
        _line(d, [(cx - head_rx * 0.95, by0 + 1 * u), (cx + sgn * head_rx * 1.4, by0 + 2 * u)], W, rng, 0.2)
        d.arc([cx - head_rx * 0.95, top - 2 * u, cx + head_rx * 0.95, top + head_ry * 1.0], 180, 360, fill=INK, width=W)
        my2 = head_cy + 4.5 * u
        d.ellipse([fx0 - 6 * u, my2 - 1.5 * u, fx0, my2 + 2 * u], fill=(60, 40, 30))
        d.ellipse([fx0, my2 - 1.5 * u, fx0 + 6 * u, my2 + 2 * u], fill=(60, 40, 30))
    elif t == "headphones":
        d.arc([cx - head_rx * 1.05, head_cy - head_ry * 1.12, cx + head_rx * 1.05, head_cy + head_ry * 0.6], 185, 355,
              fill=INK, width=int(W * 1.4))
        for sx in (-1, 1):
            hx = cx + sx * head_rx * 1.02
            d.rounded_rectangle([hx - 3 * u, head_cy - 4 * u, hx + 3 * u, head_cy + 5 * u], radius=2 * u, fill=(250, 110, 160))
            _line(d, [(hx - 3 * u, head_cy - 4 * u), (hx + 3 * u, head_cy - 4 * u), (hx + 3 * u, head_cy + 5 * u),
                      (hx - 3 * u, head_cy + 5 * u), (hx - 3 * u, head_cy - 4 * u)], int(W * 0.7), rng, 0.1)
    elif t == "sprout":
        _line(d, [(cx, top + 0.5 * u), (cx + 1 * u, top - 7 * u)], int(W * 0.9), rng, 0.2)
        for sx in (-1, 1):
            lx0, ly0 = cx + 1 * u, top - 6 * u
            leaf = [(lx0, ly0), (lx0 + sx * 4 * u, ly0 - 4 * u), (lx0 + sx * 8 * u, ly0 - 2 * u), (lx0 + sx * 4 * u, ly0 + 1 * u)]
            d.polygon(leaf, fill=(110, 200, 90))
            _line(d, leaf + [leaf[0]], int(W * 0.7), rng, 0.1)
    return (cx, head_cy - head_ry)  # top of head, for speech bubbles


def font(size, bold=True):
    p = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf" if bold else "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
    return ImageFont.truetype(p, size)
