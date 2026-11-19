import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.join(HERE, "logo.png")
ROBOTO = "/usr/share/fonts/truetype/google-fonts/ofl/roboto/Roboto[wdth,wght].ttf"
INTER = "/usr/share/fonts/opentype/inter/"

BG = (244, 241, 234)
INK = (20, 20, 20)
GREY = (95, 95, 95)
ACC = (200, 16, 46)
GRID = (226, 222, 212)


def rob(size, wght=700, wdth=80):
    ft = ImageFont.truetype(ROBOTO, size)
    try:
        ft.set_variation_by_axes([wght, wdth])
    except Exception:
        pass
    return ft


def inter(name, size):
    return ImageFont.truetype(INTER + name, size)


def canvas(w, h):
    im = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(im)
    for x in range(0, w, 54):
        d.line([(x, 0), (x, h)], fill=GRID, width=1)
    for y in range(0, h, 54):
        d.line([(0, y), (w, y)], fill=GRID, width=1)
    return im, d


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


def fit(d, text, maxw, maxlines, start, stop, wght=700, wdth=80):
    for size in range(start, stop, -4):
        ft = rob(size, wght, wdth)
        lines = wrap(d, text, ft, maxw)
        if len(lines) <= maxlines:
            return ft, lines, int(size * 1.08)
    ft = rob(stop, wght, wdth)
    return ft, wrap(d, text, ft, maxw), int(stop * 1.08)


def label(d, x, y, text, size=28):
    d.rectangle([x, y + 6, x + 14, y + 20], fill=ACC)
    d.text((x + 30, y), text.upper(), font=inter("Inter-SemiBold.otf", size), fill=INK)


def logo(im, x, ybottom, maxw=560, maxh=80):
    if not os.path.exists(LOGO):
        return
    lg = Image.open(LOGO).convert("RGBA")
    lg.thumbnail((maxw, maxh), Image.LANCZOS)
    im.paste(lg, (x, ybottom - lg.height), lg)
