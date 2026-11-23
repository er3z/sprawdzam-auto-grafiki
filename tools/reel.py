"""Rolka 1080x1920 MP4 z 3 faktami i własną ścieżką dźwiękową.

Użycie: python3 tools/reel.py spec.json
spec.json:
{
  "label": "Premiera",
  "hook": "Ta usterka kosztuje 8 tys. zł",
  "title": "Chwytliwy tytuł, 25-60 znaków",
  "facts": ["Fakt 1 (krótko)", "Fakt 2", "Fakt 3"],
  "source": "Motor1, Autocar",
  "out": "posts/2026-11-20-rolka-slug.mp4"
}
Z polem "hook" (zalecane, od 23.11.2026): krótka rolka ok. 9 s. Hak (do ok. 45 znaków,
konkret: liczba, model, koszt) jest widoczny dużym tekstem od pierwszej klatki, bez logo,
potem 3 fakty po 2,2 s (każdy do ok. 55 znaków) i 1 s zakończenia. Pole "title" jest wtedy
pomijane. Bez "hook": stary format ok. 15 s z animowanym tytułem.
Tworzy też okładkę <out bez .mp4>-cover.jpg (w trybie hook: klatka z hakiem).
"""
import json
import math
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np
from PIL import Image, ImageDraw

from common import canvas, fit, wrap, rob, inter, label, logo, BG, INK, GREY, ACC

W, H, M = 1080, 1920, 90
FPS = 30
T_TITLE, T_FACT, T_END = 3.5, 3.2, 2.0


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def base(spec):
    im, d = canvas(W, H)
    label(d, M, 170, spec.get("label", "Nowość"), size=34)
    logo(im, M, H - 170, maxw=600, maxh=86)
    return im


def hook_frame(spec, t):
    """Hak widoczny w całości od pierwszej klatki (bez animacji wejścia i bez logo)."""
    im, d = canvas(W, H)
    label(d, M, 170, spec.get("label", "Nowość"), size=34)
    ft, lines, lh = fit(d, spec["hook"], W - 2 * M, 4, 176, 96)
    y0 = (H - lh * len(lines)) // 2 - 60
    for i, ln in enumerate(lines):
        d.text((M, y0 + i * lh), ln, font=ft, fill=INK)
    yb = y0 + lh * len(lines) + 40
    grow = ease(t / 0.6)
    d.rectangle([M, yb, M + 160 + int(200 * grow), yb + 14], fill=ACC)
    return im


def title_frame(bg, spec, t):
    im = bg.copy()
    d = ImageDraw.Draw(im)
    ft, lines, lh = fit(d, spec["title"], W - 2 * M, 5, 150, 84)
    y0 = (H - lh * len(lines)) // 2 - 80
    for i, ln in enumerate(lines):
        p = ease((t - i * 0.12) / 0.5)
        if p <= 0:
            continue
        x = M - int((1 - p) * 120)
        layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(layer).text((x, y0 + i * lh), ln, font=ft, fill=INK + (int(255 * p),))
        im.paste(layer, (0, 0), layer)
    bar = ease((t - 0.6) / 0.5)
    yb = y0 + lh * len(lines) + 40
    d.rectangle([M, yb, M + int(160 * bar), yb + 10], fill=ACC)
    return im


def fact_frame(bg, spec, k, t, anim=0.45):
    im = bg.copy()
    d = ImageDraw.Draw(im)
    p = ease(t / anim)
    num = rob(260, 800, 80)
    d.text((M, 420 - int((1 - p) * 60)), f"{k + 1}", font=num, fill=ACC)
    ft, lines, lh = fit(d, spec["facts"][k], W - 2 * M, 6, 104, 60)
    y = 820
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for i, ln in enumerate(lines):
        q = ease((t - 0.1 * anim / 0.45 - i * 0.08 * anim / 0.45) / anim)
        ld.text((M, y + i * lh + int((1 - q) * 40)), ln, font=ft, fill=INK + (int(255 * q),))
    im.paste(layer, (0, 0), layer)
    # pasek postepu
    for j in range(len(spec["facts"])):
        x = M + j * 120
        d.rectangle([x, 330, x + 100, 338], fill=ACC if j <= k else (210, 205, 195))
    return im


def end_frame(bg, spec, t):
    im, d = canvas(W, H)
    p = ease(t / 0.5)
    lg = Image.open(os.path.join(os.path.dirname(__file__), "logo.png")).convert("RGBA")
    lg.thumbnail((900, 130), Image.LANCZOS)
    a = lg.split()[3].point(lambda v: int(v * p))
    lg.putalpha(a)
    im.paste(lg, ((W - lg.width) // 2, H // 2 - 160), lg)
    f1 = inter("Inter-SemiBold.otf", 46)
    msg = "Obserwuj, zanim kupisz auto"
    d.text((W // 2, H // 2 + 40), msg, font=f1, fill=INK, anchor="ma")
    if spec.get("source"):
        d.text((W // 2, H - 260), "Źródło: " + spec["source"], font=inter("Inter-Regular.otf", 30), fill=GREY, anchor="ma")
    return im


def music(path, dur, sr=44100):
    """Prosta, własna ścieżka: miękki pad + delikatny puls 96 BPM."""
    t = np.arange(int(sr * dur)) / sr
    chords = [(220.0, 277.18, 329.63), (196.0, 246.94, 293.66), (174.61, 220.0, 261.63), (196.0, 246.94, 329.63)]
    seg = dur / len(chords)
    sig = np.zeros_like(t)
    for i, ch in enumerate(chords):
        m = (t >= i * seg) & (t < (i + 1) * seg)
        for f in ch:
            sig[m] += 0.12 * np.sin(2 * np.pi * f * t[m]) + 0.04 * np.sin(2 * np.pi * 2 * f * t[m])
    beat = 60 / 96
    ph = (t % beat)
    kick = 0.5 * np.sin(2 * np.pi * (50 + 80 * np.exp(-ph * 40)) * ph) * np.exp(-ph * 9)
    hat = 0.03 * np.random.default_rng(1).standard_normal(len(t)) * np.exp(-((t + beat / 2) % beat) * 60)
    sig = sig + kick + hat
    fade = np.minimum(1, np.minimum(t / 1.0, (dur - t) / 1.5))
    sig = sig * fade
    sig = sig / np.max(np.abs(sig)) * 0.6
    data = (sig * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data.tobytes())


def main(path):
    spec = json.load(open(path, encoding="utf-8"))
    assert 2 <= len(spec["facts"]) <= 4
    bg = base(spec)
    short = bool(spec.get("hook"))
    if short:
        t_first, t_fact, t_end, anim = 1.8, 2.2, 1.0, 0.25
    else:
        t_first, t_fact, t_end, anim = T_TITLE, T_FACT, T_END, 0.45
    frames = []
    for i in range(int(t_first * FPS)):
        frames.append(("h" if short else "t", None, i / FPS))
    for k in range(len(spec["facts"])):
        for i in range(int(t_fact * FPS)):
            frames.append(("f", k, i / FPS))
    for i in range(int(t_end * FPS)):
        frames.append(("e", None, i / FPS))
    dur = len(frames) / FPS
    out = spec["out"]
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "a.wav")
        music(wav, dur)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
               "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
               "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out]
        pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        cover = None
        for kind, k, t in frames:
            if kind == "h":
                im = hook_frame(spec, t)
                if t >= 0.6 and cover is None:
                    cover = im
            elif kind == "t":
                im = title_frame(bg, spec, t)
                if t >= T_TITLE - 0.5 and cover is None:
                    cover = im
            elif kind == "f":
                im = fact_frame(bg, spec, k, t, anim)
            else:
                im = end_frame(bg, spec, t)
            pr.stdin.write(im.tobytes())
        pr.stdin.close()
        pr.wait()
        if pr.returncode:
            sys.exit("ffmpeg error")
    cov = out[:-4] + "-cover.jpg"
    cover.save(cov, "JPEG", quality=92)
    print(out)
    print(cov)


if __name__ == "__main__":
    main(sys.argv[1])
