import io
from pathlib import Path
from dataclasses import dataclass, InitVar
import requests
from fake_useragent import UserAgent
import numpy as np
from PIL import Image
import cairosvg  # type: ignore[import-untyped]
from glaze_gallery._random_dirs import random_str


def download_logo_image(svg_url: str) -> Image.Image:
    r = requests.get(svg_url, headers={"User-Agent": UserAgent().firefox})
    r.raise_for_status()
    out = io.BytesIO()
    cairosvg.svg2png(r.content, output_width=1000, write_to=out)
    return Image.open(out)


@dataclass
class ImagePath:
    file_name: str
    downloads_dir: InitVar[Path]

    def __post_init__(self, downloads_dir: Path) -> None:
        self.dir_name = random_str()
        dir_path = downloads_dir / self.dir_name
        dir_path.mkdir()
        self.path = dir_path / self.file_name


@dataclass
class ImagePaths:
    file_name_high: str
    file_name_low: str
    downloads_dir: InitVar[Path]

    def __post_init__(self, downloads_dir: Path) -> None:
        self.high = ImagePath(self.file_name_high, downloads_dir)
        self.low = ImagePath(self.file_name_low, downloads_dir)


class Images:

    _HIGH_DIMS = (2000, 2000)
    _LOW_DIMS = (700, 700)
    _LOGO_SCALE = 0.4
    _LOGO_OFFSET_X = 0.035
    _LOGO_OFFSET_Y = 0.03
    _LOGO_ALPHA = 0.25

    def __init__(self, image_bytes: io.BytesIO, file_name_base: str) -> None:
        self.im = Image.open(image_bytes)

        self.im_high = self.im.copy()
        self.im_high.thumbnail(self._HIGH_DIMS)

        self.file_name_high = f"{file_name_base}-high.webp"

        self.im_low = self.im.copy()
        self.im_low.thumbnail(self._LOW_DIMS)
        self.file_name_low = f"{file_name_base}-low.webp"

    def save(self, downloads_dir: Path, logo_im: Image.Image) -> ImagePaths:
        image_paths = ImagePaths(self.file_name_high, self.file_name_low, downloads_dir)
        im_high = self.im_high.copy()
        self.add_logo(im_high, logo_im)
        im_high.save(image_paths.high.path)
        im_low = self.im_low.copy()
        self.add_logo(im_low, logo_im)
        im_low.save(image_paths.low.path)
        return image_paths

    def add_logo(self, im: Image.Image, logo_im: Image.Image) -> None:
        logo_w = im.size[0] * self._LOGO_SCALE
        logo_h = logo_im.size[1] * logo_w / logo_im.size[0]
        logo_im_scaled = logo_im.copy()
        logo_im_scaled.thumbnail((logo_w, logo_h))
        alpha_array = np.array(logo_im_scaled.split()[-1])
        mask = Image.fromarray((alpha_array * self._LOGO_ALPHA).astype(np.uint8))
        im.paste(
            Image.new("RGB", logo_im_scaled.size),
            (
                round(im.size[0] * (1 - self._LOGO_OFFSET_X) - logo_w),
                round(im.size[1] * (1 - self._LOGO_OFFSET_Y) - logo_h),
            ),
            mask=mask,
        )
