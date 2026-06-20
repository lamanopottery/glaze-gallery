import os
import shutil
from pathlib import Path
import requests
from dotenv import load_dotenv

_DATA_DIR = Path("src", "data")
_IMAGES_URLS = {
    "lamanopottery": "https://glazegalleryimages.lamanopottery.com",
    "mudmatters": "https://glazegalleryimages.mudmatters.com",
}


def _download_file(images_url: str, relative_path: str, file_name: str) -> None:
    r = requests.get(f"{images_url}/{relative_path}")
    with open(_DATA_DIR / file_name, "wb") as f:
        f.write(r.content)


def download_data() -> None:
    load_dotenv()
    studio = os.environ["GLAZE_GALLERY_STUDIO"]
    images_url = _IMAGES_URLS.get(studio)
    if images_url is None:
        raise ValueError(f"Unknown GLAZE_GALLERY_STUDIO: {studio!r}")

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
