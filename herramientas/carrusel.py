"""Genera carruseles 1080x1350 para Instagram desde ESTRUCTURA WEB.
Uso: python3 carrusel.py <slug-carpeta> <orden ej. 01,02,08> <salida>
Lámina 1: foto a sangre arriba + bloque de texto. Resto: foto completa (sin recorte) sobre blanco."""
import sys, os, json
from PIL import Image, ImageDraw, ImageFont
BASE = os.path.expanduser("~/mnt/02_CV_PORTFOLIO_REEL/03_PORTFOLIO/ESTRUCTURA WEB")
W, H = 1080, 1350
TXT, MUTED, LINE = (58,58,56), (138,138,134), (200,198,194)
F = "/usr/share/fonts/truetype/liberation/LiberationSansNarrow-%s.ttf"
def font(st, sz): return ImageFont.truetype(F % st, sz)
def spaced(d, xy, s, f, fill, track):
    x, y = xy
    for ch in s:
        d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + track
def spaced_w(d, s, f, track): return sum(d.textlength(c, font=f) + track for c in s) - track
def load(p, n):
    pj = json.load(open(f"{BASE}/proyectos/{p}/proyecto.json", encoding="utf-8"))
    im = next(i for i in pj["imagenes"] if i["n"] == n)
    return pj, Image.open(f"{BASE}/{im['original']}").convert("RGB")
def cover(pj, img, out, total, ov={}):
    c = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(c)
    hh = 900; r = max(W / img.width, hh / img.height)
    im = img.resize((round(img.width * r), round(img.height * r)), Image.LANCZOS)
    l = (im.width - W) // 2; t = (im.height - hh) // 2
    c.paste(im.crop((l, t, l + W, t + hh)), (0, 0))
    name = pj["nombre"]["es"].upper(); fi = pj["ficha"]["es"]
    f1 = font("Bold", 64 if len(name) < 22 else 52)
    spaced(d, ((W - spaced_w(d, name, f1, 6)) // 2, 975), name, f1, TXT, 6)
    d.line((W//2 - 60, 1075, W//2 + 60, 1075), fill=LINE, width=2)
    sub = ov.get("sub") or f"{fi.get('ubicacion','').replace(', Colombia','')}  ·  {fi.get('anio','')}".upper()
    f2 = font("Regular", 30)
    spaced(d, ((W - spaced_w(d, sub, f2, 4)) // 2, 1105), sub, f2, MUTED, 4)
    of = ov.get("oficina") or fi.get("oficina") or fi.get("diseno") or ""
    if of:
        s3 = of.upper(); f3 = font("Regular", 24)
        spaced(d, ((W - spaced_w(d, s3, f3, 4)) // 2, 1160), s3, f3, MUTED, 4)
    f4 = font("Regular", 22); s4 = f"01 / {total:02d}"
    d.text(((W - d.textlength(s4, font=f4)) // 2, 1270), s4, font=f4, fill=LINE)
    c.save(out, "JPEG", quality=92)
def inner(pj, img, out, k, total):
    c = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(c)
    bw, bh = 980, 1150; r = min(bw / img.width, bh / img.height)
    im = img.resize((round(img.width * r), round(img.height * r)), Image.LANCZOS)
    c.paste(im, ((W - im.width) // 2, 50 + (bh - im.height) // 2))
    f = font("Regular", 22); name = pj["nombre"]["es"].upper()
    spaced(d, (50, 1270), name, f, MUTED, 3)
    s = f"{k:02d} / {total:02d}"; d.text((W - 50 - d.textlength(s, font=f), 1270), s, font=f, fill=LINE)
    c.save(out, "JPEG", quality=92)
if __name__ == "__main__":
    p, orden, outdir = sys.argv[1], [int(x) for x in sys.argv[2].split(",")], sys.argv[3]
    ov = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
    os.makedirs(outdir, exist_ok=True); total = len(orden)
    for k, n in enumerate(orden, 1):
        pj, img = load(p, n); out = f"{outdir}/{k:02d}.jpg"
        cover(pj, img, out, total, ov) if k == 1 else inner(pj, img, out, k, total)
    print(outdir, total)
