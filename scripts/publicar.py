"""Publica en Instagram los carruseles de calendario.json que ya vencieron.

Solo publica entradas con "estado": "aprobado". Los borradores se ignoran.
Modos:
  python scripts/publicar.py verificar   -> comprueba el token y muestra la cuenta, no publica
  python scripts/publicar.py publicar    -> publica lo aprobado cuya fecha ya pasó

Variables de entorno: IG_TOKEN (secreto), GITHUB_REPOSITORY, GITHUB_SHA.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://graph.instagram.com/v25.0"
RAIZ = Path(__file__).resolve().parent.parent
CAL = RAIZ / "calendario.json"
TOKEN = os.environ.get("IG_TOKEN", "")


def llamar(metodo, ruta, **params):
    params["access_token"] = TOKEN
    datos = urllib.parse.urlencode(params).encode()
    if metodo == "GET":
        req = urllib.request.Request(f"{API}/{ruta}?{datos.decode()}")
    else:
        req = urllib.request.Request(f"{API}/{ruta}", data=datos, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        cuerpo = e.read().decode(errors="replace")
        raise SystemExit(f"Error de la API ({e.code}) en {ruta}: {cuerpo}")


def esperar_contenedor(cid, intentos=10):
    for _ in range(intentos):
        estado = llamar("GET", cid, fields="status_code").get("status_code")
        if estado == "FINISHED":
            return
        if estado in ("ERROR", "EXPIRED"):
            raise SystemExit(f"El contenedor {cid} terminó en estado {estado}")
        time.sleep(20)
    raise SystemExit(f"El contenedor {cid} no estuvo listo a tiempo")


def publicar_carrusel(ig_id, entrada, repo, sha):
    carpeta = RAIZ / "posts" / entrada["id"]
    laminas = sorted(carpeta.glob("*.jpg"))
    if not 2 <= len(laminas) <= 10:
        raise SystemExit(f"{entrada['id']}: un carrusel necesita entre 2 y 10 imágenes, hay {len(laminas)}")
    texto = (carpeta / "texto.txt").read_text(encoding="utf-8").strip()
    if len(texto) > 2200:
        raise SystemExit(f"{entrada['id']}: el texto supera 2.200 caracteres")

    hijos = []
    for f in laminas:
        url = f"https://raw.githubusercontent.com/{repo}/{sha}/posts/{entrada['id']}/{f.name}"
        r = llamar("POST", f"{ig_id}/media", image_url=url, is_carousel_item="true")
        hijos.append(r["id"])
        print(f"  lámina {f.name} -> contenedor {r['id']}")
    for h in hijos:
        esperar_contenedor(h)

    padre = llamar("POST", f"{ig_id}/media", media_type="CAROUSEL",
                   children=",".join(hijos), caption=texto)["id"]
    esperar_contenedor(padre)
    media = llamar("POST", f"{ig_id}/media_publish", creation_id=padre)["id"]
    return media


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else "publicar"
    if not TOKEN:
        raise SystemExit("Falta el secreto IG_TOKEN en el repositorio")

    cuenta = llamar("GET", "me", fields="user_id,username")
    ig_id = cuenta.get("user_id") or cuenta["id"]
    print(f"Cuenta conectada: @{cuenta.get('username')} (id {ig_id})")
    if modo == "verificar":
        return

    repo = os.environ["GITHUB_REPOSITORY"]
    sha = os.environ["GITHUB_SHA"]
    cal = json.loads(CAL.read_text(encoding="utf-8"))
    ahora = datetime.now(timezone.utc)
    cambios = False

    for e in cal["publicaciones"]:
        if e.get("estado") != "aprobado":
            continue
        if datetime.fromisoformat(e["fecha"]) > ahora:
            continue
        print(f"Publicando {e['id']} (programado {e['fecha']})")
        e["media_id"] = publicar_carrusel(ig_id, e, repo, sha)
        e["estado"] = "publicado"
        e["publicado_en"] = ahora.isoformat(timespec="seconds")
        cambios = True
        CAL.write_text(json.dumps(cal, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"  publicado, media_id {e['media_id']}")

    if not cambios:
        print("Nada pendiente por publicar.")


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        if e.code not in (0, None):
            print(f"::error::{e.code}", flush=True)
        raise
