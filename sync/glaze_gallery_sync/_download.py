from dotenv import load_dotenv
from glaze_gallery_sync._google_api import GoogleDrive


def download():
    load_dotenv()
    google_drive = GoogleDrive()
