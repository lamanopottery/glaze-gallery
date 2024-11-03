import io
from PIL import Image


def download_image(image_bytes: io.BytesIO, file_path: str) -> None:
    im = Image.open(image_bytes)
    im_high = im.copy()
    im_high.thumbnail((2000, 2000))
    im_high.save(f"{file_path}-high.webp")
    im_low = im.copy()
    im_low.thumbnail((700, 700))
    im_low.save(f"{file_path}-low.webp")
