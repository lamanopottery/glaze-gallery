import os
import shutil
from dotenv import load_dotenv
import pandas as pd
from glaze_gallery_sync._google_api import GoogleDrive

_DOWNLOADS_DIR = "downloads"


def _download_side_images(
    google_drive: GoogleDrive, glaze_data: pd.DataFrame, download_dir: str, side: str
) -> None:
    side_name = side.capitalize()
    filtered_glaze_data = glaze_data[glaze_data[f"{side_name} image"].astype(bool)]
    for i in range(len(filtered_glaze_data)):
        image_data = filtered_glaze_data.iloc[i]
        file_id = image_data[f"{side_name} file ID\n(computed, do not edit)"]
        assert isinstance(file_id, str) and file_id
        mime_type = image_data[f"{side_name} file MIME type\n(computed, do not edit)"]
        assert isinstance(mime_type, str) and mime_type
        glaze1 = image_data["1st dip"]
        assert isinstance(glaze1, str) and glaze1
        glaze2 = image_data["2nd dip"]
        assert isinstance(glaze2, str) and glaze2
        google_drive.download_glaze_image(
            file_id, download_dir, mime_type, glaze1, glaze2, side
        )


def download():
    load_dotenv()
    google_drive = GoogleDrive()
    glaze_data = google_drive.get_glaze_data()
    shutil.rmtree(_DOWNLOADS_DIR)
    os.mkdir(_DOWNLOADS_DIR)
    _download_side_images(google_drive, glaze_data, _DOWNLOADS_DIR, side="front")
    _download_side_images(google_drive, glaze_data, _DOWNLOADS_DIR, side="back")
