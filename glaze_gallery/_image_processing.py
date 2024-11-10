import os
import io
from PIL import Image
from glaze_gallery._constants import LA_MANO_DIR, MUD_MATTERS_DIR


def download_image(
    image_bytes: io.BytesIO,
    hide_la_mano: bool,
    hide_mud_matters: bool,
    file_name_base: str,
) -> None:
    im = Image.open(image_bytes)

    im_high = im.copy()
    im_high.thumbnail((2000, 2000))

    im_low = im.copy()
    im_low.thumbnail((700, 700))

    if not hide_la_mano:
        la_mano_file_path = os.path.join(LA_MANO_DIR, file_name_base)
        im_high.save(f"{la_mano_file_path}-high.webp")
        im_low.save(f"{la_mano_file_path}-low.webp")
    if not hide_mud_matters:
        mud_matters_file_path = os.path.join(MUD_MATTERS_DIR, file_name_base)
        im_high.save(f"{mud_matters_file_path}-high.webp")
        im_low.save(f"{mud_matters_file_path}-low.webp")
