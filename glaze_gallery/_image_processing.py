import io
from pathlib import Path
from PIL import Image
from glaze_gallery._r2 import save_to_local_r2


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

    def save(self, downloads_dir: Path, r2_dir: str) -> None:
        file_path_high = downloads_dir / self.file_name_high
        file_path_low = downloads_dir / self.file_name_low
        self.im_high.save(file_path_high)
        self.im_low.save(file_path_low)
        save_to_local_r2(file_path_high, r2_path=f"{r2_dir}/{self.file_name_high}")
        save_to_local_r2(file_path_high, r2_path=f"{r2_dir}/{self.file_name_low}")
