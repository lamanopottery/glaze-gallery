import os
import shutil
from pathlib import Path
import requests
from dotenv import load_dotenv
from glaze_gallery._studios import _STUDIOS

_DATA_DIR = Path("src", "data")


def _download_file(images_url: str, relative_path: str, file_name: str) -> None:
    r = requests.get(f"{images_url}/{relative_path}")
    with open(_DATA_DIR / file_name, "wb") as f:
        f.write(r.content)


def download_data() -> None:
    load_dotenv()
    studio_key = os.environ["GLAZE_GALLERY_STUDIO"]
    studio = _STUDIOS.get(studio_key)
    if studio is None:
        raise ValueError(f"Unknown GLAZE_GALLERY_STUDIO: {studio_key!r}")
    images_url = studio["images_url"]

    if _DATA_DIR.is_dir():
        shutil.rmtree(_DATA_DIR)
    _DATA_DIR.mkdir()
    _download_file(
        images_url, os.environ["GLAZE_GALLERY_GLAZE_NAMES"], "glaze-names.json"
    )
    _download_file(
        images_url,
        os.environ["GLAZE_GALLERY_GLAZE_COMBO_INFO"],
        "glaze-combo-info.json",
    )
    _download_file(
        images_url, os.environ["GLAZE_GALLERY_IMAGES_HIGH"], "images-high.json"
    )
    _download_file(
        images_url, os.environ["GLAZE_GALLERY_IMAGES_LOW"], "images-low.json"
    )
