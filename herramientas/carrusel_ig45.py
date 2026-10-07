"""Carrusel con portada A+P + imágenes ig_4x5 de ESTRUCTURA WEB, tal cual.
Uso: python3 carrusel_ig45.py <proyecto> <orden ig_4x5 ej. 04,02,05> <salida> ['{"sub":..,"oficina":..}']"""
import sys, os, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from carrusel import BASE, cover
from PIL import Image
p, orden, outdir = sys.argv[1], [int(x) for x in sys.argv[2].split(",")], sys.argv[3]
ov = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
pj = json.load(open(f"{BASE}/proyectos/{p}/proyecto.json", encoding="utf-8"))
hero = next((i for i in pj["imagenes"] if i.get("hero")), pj["imagenes"][0])
os.makedirs(outdir, exist_ok=True)
for f in os.listdir(outdir):
    if f.endswith(".jpg"): os.remove(f"{outdir}/{f}")
total = len(orden) + 1
cover(pj, Image.open(f"{BASE}/{hero['original']}").convert("RGB"), f"{outdir}/01.jpg", total, ov)
for k, n in enumerate(orden, 2):
    im = next(i for i in pj["imagenes"] if i["n"] == n)
    src = Image.open(f"{BASE}/{im['ig_4x5']['archivo']}").convert("RGB")
    assert src.size == (1080, 1350), (p, n, src.size)
    src.save(f"{outdir}/{k:02d}.jpg", "JPEG", quality=92)
print(outdir, total)
