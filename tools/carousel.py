"""Karuzela "Kupujesz X?" 1080x1350 JPEG.

Użycie: python3 tools/carousel.py spec.json
spec.json:
{
  "model": "Volkswagen Golf VII",
  "years": "2012-2019",
  "points": [{"title": "Skrzynia DSG", "body": "Krótki opis, co sprawdzić i jak."}, ...],   # 3 do 6
  "cta_url": "sprawdzamauto.netlify.app",
  "out_prefix": "posts/2026-11-20-karuzela-golf-vii"
}
Tworzy pliki <out_prefix>-01.jpg ... i wypisuje ich listę.
"""
import json
import sys
from common import canvas, fit, wrap, rob, inter, label, logo, INK, GREY, ACC

W, H, M = 1080, 1350, 90


def footer(im, d, i, n):
    logo(im, M, H - M + 10, maxw=460, maxh=64)
    d.text((W - M, H - M - 30), f"{i}/{n}", font=inter("Inter-SemiBold.otf", 28), fill=GREY, anchor="ra")


def cover(spec, n):
    im, d = canvas(W, H)
    label(d, M, M - 6, "Poradnik zakupowy")
    ft, lines, lh = fit(d, f"Kupujesz {spec['model']}?", W - 2 * M, 4, 150, 80)
    y = 330
    for ln in lines:
        d.text((M, y), ln, font=ft, fill=INK)
        y += lh
    sub = f"{len(spec['points'])} rzeczy do sprawdzenia przed zakupem."
    if spec.get("years"):
        sub += f" Roczniki {spec['years']}."
    sft = rob(54, 500, 80)
    y += 30
    for ln in wrap(d, sub, sft, W - 2 * M):
        d.text((M, y), ln, font=sft, fill=ACC)
        y += 64
    d.text((M, y + 40), "Przesuń  →", font=inter("Inter-SemiBold.otf", 32), fill=GREY)
    footer(im, d, 1, n)
    return im


def point(p, k, i, n):
    im, d = canvas(W, H)
    label(d, M, M - 6, "Sprawdź")
    d.text((M, 210), f"{k:02d}", font=rob(200, 800, 80), fill=ACC)
    ft, lines, lh = fit(d, p["title"], W - 2 * M, 3, 96, 60)
    y = 470
    for ln in lines:
        d.text((M, y), ln, font=ft, fill=INK)
        y += lh
    bft = inter("Inter-Regular.otf", 40)
    y += 40
    for ln in wrap(d, p["body"], bft, W - 2 * M)[:9]:
        d.text((M, y), ln, font=bft, fill=INK)
        y += 56
    footer(im, d, i, n)
    return im


def cta(spec, i, n):
    im, d = canvas(W, H)
    label(d, M, M - 6, "Zanim pojedziesz")
    ft, lines, lh = fit(d, "Zapisz ten post na oględziny", W - 2 * M, 3, 130, 70)
    y = 360
    for ln in lines:
        d.text((M, y), ln, font=ft, fill=INK)
        y += lh
    bft = inter("Inter-Regular.otf", 42)
    y += 50
    for ln in wrap(d, "Pełna lista kontrolna, dekoder VIN i poradniki modeli za darmo:", bft, W - 2 * M):
        d.text((M, y), ln, font=bft, fill=INK)
        y += 58
    d.text((M, y + 20), spec.get("cta_url", "sprawdzamauto.netlify.app"), font=rob(64, 700, 80), fill=ACC)
    footer(im, d, i, n)
    return im


def main(path):
    spec = json.load(open(path, encoding="utf-8"))
    pts = spec["points"]
    n = len(pts) + 2
    slides = [cover(spec, n)] + [point(p, k + 1, k + 2, n) for k, p in enumerate(pts)] + [cta(spec, n, n)]
    out = []
    for i, s in enumerate(slides, 1):
        f = f"{spec['out_prefix']}-{i:02d}.jpg"
        s.save(f, "JPEG", quality=92)
        out.append(f)
    print("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1])
