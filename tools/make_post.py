#!/usr/bin/env python3
"""Render an Instagram quote post.

Usage:
  python3 make_post.py photo "Quote text" OUT.jpg [--handle @name] [--seed N]
  python3 make_post.py reel  "Quote text" OUT.mp4 [--handle @name] [--seed N]

photo -> 1080x1350 JPG (4:5 feed)
reel  -> 1080x1920 MP4, 9 s, slow zoom + text fade-in (silent; add trending audio in-app if wanted)
"""
import argparse, os, random, subprocess, tempfile, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_DIR = "/usr/share/fonts/truetype/google-fonts"
QUOTE_FONTS = [
    f"{FONT_DIR}/Poppins-Bold.ttf",
    f"{FONT_DIR}/Poppins-SemiBold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
]
SMALL_FONT = f"{FONT_DIR}/Poppins-Medium.ttf"

# (top colour, bottom colour, accent colour)
PALETTES = [
    ((15, 15, 20), (45, 40, 60), (232, 190, 110)),      # midnight + gold
    ((10, 25, 40), (20, 70, 90), (120, 230, 210)),      # deep teal
    ((40, 10, 20), (110, 30, 50), (255, 200, 170)),     # wine
    ((20, 20, 20), (60, 60, 60), (255, 255, 255)),      # monochrome
    ((25, 15, 45), (90, 40, 120), (255, 170, 220)),     # violet dusk
    ((5, 30, 20), (30, 80, 50), (220, 240, 160)),       # forest
    ((60, 30, 10), (160, 80, 30), (255, 235, 200)),     # sunset amber
]


def font(path, size):
    for p in [path] + QUOTE_FONTS:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def background(w, h, pal, rng):
    top, bot, accent = pal
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        for x in range(w):
            px[x, y] = c
    # soft glow blobs
    glow = Image.new("RGB", (w, h), (0, 0, 0))
    g = ImageDraw.Draw(glow)
    for _ in range(3):
        r = rng.randint(w // 4, w // 2)
        cx, cy = rng.randint(0, w), rng.randint(0, h)
        g.ellipse([cx - r, cy - r, cx + r, cy + r], fill=tuple(int(v * 0.35) for v in accent))
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    from PIL import ImageChops
    img = ImageChops.add(img, glow)
    # subtle grain
    noise = Image.effect_noise((w, h), 18).convert("RGB")
    img = Image.blend(img, noise, 0.04)
    return img


def fit_text(draw, text, fpath, max_w, max_h, start=96, minimum=44):
    size = start
    while size >= minimum:
        f = font(fpath, size)
        chars = max(10, int(max_w / (size * 0.52)))
        lines = textwrap.wrap(text, width=chars)
        lh = int(size * 1.28)
        widest = max(draw.textlength(l, font=f) for l in lines)
        if widest <= max_w and lh * len(lines) <= max_h:
            return f, lines, lh
        size -= 4
    f = font(fpath, minimum)
    return f, textwrap.wrap(text, width=int(max_w / (minimum * 0.52))), int(minimum * 1.28)


def draw_card(w, h, quote, handle, pal, rng, text_alpha=255):
    """Return (background, text_layer RGBA)."""
    bg = background(w, h, pal, rng)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    accent = pal[2]
    fpath = rng.choice(QUOTE_FONTS)
    margin = int(w * 0.11)
    f, lines, lh = fit_text(d, quote, fpath, w - 2 * margin, int(h * 0.5))
    block_h = lh * len(lines)
    y0 = (h - block_h) // 2
    # big opening quote mark
    qm = font(QUOTE_FONTS[2], int(w * 0.22))
    d.text((margin - 10, y0 - int(w * 0.20)), "“", font=qm, fill=accent + (int(text_alpha * 0.9),))
    for i, line in enumerate(lines):
        lw = d.textlength(line, font=f)
        d.text(((w - lw) / 2, y0 + i * lh), line, font=f, fill=(255, 255, 255, text_alpha))
    # accent rule
    ry = y0 + block_h + int(lh * 0.6)
    d.rectangle([w / 2 - 60, ry, w / 2 + 60, ry + 6], fill=accent + (text_alpha,))
    if handle:
        sf = font(SMALL_FONT, int(w * 0.034))
        hw = d.textlength(handle, font=sf)
        bottom = 0.09 if h < 1500 else 0.24  # keep clear of the Reels UI overlay
        d.text(((w - hw) / 2, h - int(h * bottom)), handle, font=sf, fill=(255, 255, 255, int(text_alpha * 0.75)))
    return bg, layer


def make_photo(quote, out, handle, seed):
    rng = random.Random(seed)
    pal = rng.choice(PALETTES)
    bg, layer = draw_card(1080, 1350, quote, handle, pal, rng)
    bg.paste(layer, (0, 0), layer)
    bg.save(out, "JPEG", quality=94)


PROGRESSIONS = [  # semitone offsets from root for 4 chords (calm, uplifting)
    [[0, 4, 7, 11], [9, 12, 16, 19], [5, 9, 12, 16], [7, 11, 14, 17]],   # Imaj7 vi IV V
    [[0, 3, 7, 10], [8, 12, 15, 19], [3, 7, 10, 14], [10, 14, 17, 21]],  # i VI III VII
    [[0, 4, 7, 14], [7, 11, 14, 19], [9, 12, 16, 21], [5, 9, 12, 19]],   # I V vi IV
    [[0, 4, 7, 11], [5, 9, 12, 16], [2, 5, 9, 12], [7, 11, 14, 17]],     # I IV ii V
]


def make_music(path, seconds, seed):
    """Compose an original, copyright-free ambient piano + pad loop."""
    import numpy as np, wave
    rng = random.Random(seed)
    sr = 44100
    n = int(sr * seconds)
    t = np.arange(n) / sr
    root = 220.0 * 2 ** (rng.choice([-5, -3, -2, 0, 2, 3]) / 12)
    prog = rng.choice(PROGRESSIONS)
    bpm = rng.choice([70, 76, 82, 88])
    beat = 60 / bpm
    bar = beat * 4
    out = np.zeros(n)
    f = lambda semi: root * 2 ** (semi / 12)
    # warm pad
    for ci in range(int(seconds / bar) + 1):
        chord = prog[ci % 4]
        s, e = int(ci * bar * sr), min(n, int((ci + 1) * bar * sr) + sr // 2)
        if s >= n:
            break
        seg = t[s:e] - t[s]
        env = np.minimum(1, seg / 0.8) * np.minimum(1, (seg[-1] - seg + 1e-3) / 0.6)
        for semi in chord:
            for det in (-0.6, 0.6):
                out[s:e] += 0.035 * env * np.sin(2 * np.pi * (f(semi - 12) + det) * seg)
        # bass
        out[s:e] += 0.08 * env * np.sin(2 * np.pi * f(chord[0] - 24) * seg)
    # soft piano arpeggio
    step = beat / 2
    k = 0
    while k * step < seconds:
        ci = int(k * step / bar) % 4
        chord = prog[ci]
        semi = chord[rng.choice([0, 1, 2, 3, 1, 2])] + rng.choice([0, 0, 12])
        s = int(k * step * sr)
        L = min(n - s, int(sr * 1.6))
        seg = np.arange(L) / sr
        env = np.exp(-seg * 3.2) * np.minimum(1, seg / 0.005)
        fr = f(semi)
        tone = np.sin(2 * np.pi * fr * seg) + 0.35 * np.sin(4 * np.pi * fr * seg) + 0.1 * np.sin(6 * np.pi * fr * seg)
        if rng.random() > 0.15:
            out[s:s + L] += 0.12 * env * tone
        k += 1
    # simple echo for space
    d = int(sr * beat * 0.75)
    wet = np.zeros(n)
    wet[d:] = out[:-d] * 0.3
    out = out + wet
    fade = np.minimum(1, np.minimum(t / 1.0, (seconds - t) / 1.5))
    out = out * fade
    out = out / (np.max(np.abs(out)) + 1e-9) * 0.8
    pcm = (out * 32767).astype(np.int16)
    stereo = np.column_stack([pcm, pcm]).ravel()
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(stereo.tobytes())


def make_reel(quote, out, handle, seed):
    rng = random.Random(seed)
    pal = rng.choice(PALETTES)
    W, H, fps, dur = 1080, 1920, 30, 12
    bg, layer = draw_card(W, H, quote, handle, pal, rng)
    big = bg.resize((int(W * 1.12), int(H * 1.12)), Image.LANCZOS)
    tmp = tempfile.mkdtemp()
    n = fps * dur
    for i in range(n):
        t = i / (n - 1)
        z = 1.12 - 0.12 * t  # slow zoom out
        cw, ch = int(W * z), int(H * z)
        ox = (big.width - cw) // 2
        oy = (big.height - ch) // 2
        frame = big.crop((ox, oy, ox + cw, oy + ch)).resize((W, H), Image.BILINEAR)
        a = min(1.0, max(0.0, (t - 0.06) / 0.18))  # text fades in ~0.5s-2s
        if a > 0:
            lay = layer.copy()
            if a < 1:
                al = lay.split()[3].point(lambda v: int(v * a))
                lay.putalpha(al)
            frame.paste(lay, (0, 0), lay)
        frame.save(os.path.join(tmp, f"f{i:04d}.jpg"), quality=90)
    music = os.path.join(tmp, "music.wav")
    make_music(music, dur, seed)
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps),
        "-i", os.path.join(tmp, "f%04d.jpg"),
        "-i", music,
        "-shortest", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
        "-movflags", "+faststart", out], check=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["photo", "reel"])
    ap.add_argument("quote")
    ap.add_argument("out")
    ap.add_argument("--handle", default="")
    ap.add_argument("--seed", type=int, default=None)
    a = ap.parse_args()
    seed = a.seed if a.seed is not None else random.randrange(1 << 30)
    (make_photo if a.kind == "photo" else make_reel)(a.quote, a.out, a.handle, seed)
    print(a.out)
