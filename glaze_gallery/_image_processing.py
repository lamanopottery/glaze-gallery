import os
import io
from pathlib import Path
from dataclasses import dataclass, InitVar
from PIL import Image
from glaze_gallery._random_dirs import random_str


@dataclass
class ImagePath:
    file_name: str
    downloads_dir: InitVar[Path]

    def __post_init__(self, downloads_dir: Path) -> None:
        dir_name = random_str()
        (downloads_dir / dir_name).mkdir()
        self.relative = os.path.join(dir_name, self.file_name)
        self.full = downloads_dir / self.relative


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

    def __init__(
        self,
        image_bytes: io.BytesIO,
        file_name_base: str,
    ) -> None:
        self.im = Image.open(image_bytes)

        self.im_high = self.im.copy()
        self.im_high.thumbnail(self._HIGH_DIMS)
        self.file_name_high = f"{file_name_base}-high.webp"

        self.im_low = self.im.copy()
        self.im_low.thumbnail(self._LOW_DIMS)
        self.file_name_low = f"{file_name_base}-low.webp"

    def save(self, downloads_dir: Path) -> ImagePaths:
        image_paths = ImagePaths(self.file_name_high, self.file_name_low, downloads_dir)
        self.im_high.save(image_paths.high.full)
        self.im_low.save(image_paths.low.full)
        return image_paths
