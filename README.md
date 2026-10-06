# amaspe-instagram

Publicación programada del portafolio de A+P Arquitectura en Instagram (@amaspe.arq) mediante la API oficial de Meta y GitHub Actions.

## Cómo funciona

- `posts/<id>/` contiene las láminas 1080×1350 (`01.jpg` … `10.jpg`, en orden) y el texto de la publicación (`texto.txt`).
- `calendario.json` define fecha, hora y estado de cada publicación.
- `.github/workflows/publicar.yml` corre cada hora y publica lo que esté **aprobado** y con fecha vencida.
- `herramientas/carrusel.py` es el script que genera las láminas desde la exportación del portafolio (se corre en el PC, no en GitHub).

## Estados en el calendario

| Estado | Qué pasa |
|---|---|
| `borrador` | No se publica. Pendiente de revisión. |
| `aprobado` | Se publica en la primera ejecución después de la fecha indicada. |
| `publicado` | Ya salió. El workflow agrega `media_id` y `publicado_en`. |

Para aprobar una publicación, cambia su `estado` a `aprobado` y guarda el archivo.

## Configuración

- Secreto del repositorio `IG_TOKEN`: token de larga duración de la app de Meta (Instagram API con inicio de sesión de Instagram), con permisos `instagram_business_basic` e `instagram_business_content_publish`. Dura 60 días; hay que renovarlo antes de que venza.
- Para probar el token sin publicar: pestaña **Actions** > **Publicar en Instagram** > **Run workflow** > modo `verificar`.

## Notas

- El repositorio es público porque Meta descarga las imágenes desde una URL pública.
- GitHub desactiva los workflows programados de repositorios públicos sin actividad durante 60 días; cada publicación hace un commit, lo que lo mantiene activo mientras haya calendario.
