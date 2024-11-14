import os
import shutil
from pathlib import Path
import requests
from dotenv import load_dotenv

_DATA_DIR = Path("src", "data")


def _download_file(relative_path: str, file_name: str) -> None:
    r = requests.get(f"{os.environ['GLAZE_GALLERY_IMAGES_URL']}/{relative_path}")
    with open(_DATA_DIR / file_name, "wb") as f:
        f.write(r.content)


def download_data() -> None:
    load_dotenv()
    if _DATA_DIR.is_dir():
        shutil.rmtree(_DATA_DIR)
    _DATA_DIR.mkdir()
    _download_file(os.environ["GLAZE_GALLERY_GLAZE_NAMES"], "glaze-names.json")
    _download_file(
        os.environ["GLAZE_GALLERY_GLAZE_COMBO_INFO"], "glaze-combo-info.json"
    )
    _download_file(os.environ["GLAZE_GALLERY_IMAGES_HIGH"], "images-high.json")
    _download_file(os.environ["GLAZE_GALLERY_IMAGES_LOW"], "images-low.json")
