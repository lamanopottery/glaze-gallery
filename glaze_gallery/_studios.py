from pathlib import Path
from typing import TypedDict


class Studio(TypedDict):
    images_url: str
    downloads_dir: Path
    hide_column: str
    logo_path: Path
    logo_color: str


_DOWNLOADS_DIR = Path("downloads")
_ASSETS_DIR = Path(__file__).resolve().parent.parent / "src" / "assets"

_STUDIOS: dict[str, Studio] = {
    "lamanopottery": {
        "images_url": "https://glazegalleryimages.lamanopottery.com",
        "downloads_dir": _DOWNLOADS_DIR / "la-mano",
        "hide_column": "hide_la_mano",
        "logo_path": _ASSETS_DIR / "LM-logo.svg",
        "logo_color": "#755239",
    },
    "mudmatters": {
        "images_url": "https://glazegalleryimages.mudmatters.com",
        "downloads_dir": _DOWNLOADS_DIR / "mud-matters",
        "hide_column": "hide_mud_matters",
        "logo_path": _ASSETS_DIR / "MM-logo.svg",
        "logo_color": "#42635e",
    },
}
