import os
import mimetypes
from datetime import datetime
import pytz
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build
from googleapiclient.http import HttpRequest, MediaIoBaseDownload

_CREDENTIALS_PATH = "credentials.json"
_TOKEN_PATH = "token.json"
_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]


class GoogleDrive:

    def __init__(
        self,
        credentials_path: str = _CREDENTIALS_PATH,
        token_path: str = _TOKEN_PATH,
        scopes: list[str] = _SCOPES,
    ) -> None:
        self.credentials = self._get_credentials(credentials_path, token_path, scopes)

    def _get_credentials(
        self, credentials_path: str, token_path: str, scopes: list[str]
    ) -> Credentials:
        creds = None
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, scopes
                )
                creds = flow.run_local_server(port=0)
            with open(token_path, "w") as token:
                token.write(creds.to_json())
        return creds

    @property
    def _spreadsheets(self) -> Resource:
        return build("sheets", "v4", credentials=self.credentials).spreadsheets()

    @property
    def _files(self) -> Resource:
        return build("drive", "v3", credentials=self.credentials).files()

    @property
    def _glaze_gallery_spreadsheet_id(self) -> str:
        return os.environ["GLAZE_GALLERY_SPREADSHEET_ID"]

    @property
    def _glaze_gallery_data_range(self) -> str:
        return os.environ["GLAZE_GALLERY_DATA_RANGE"]

    @property
    def _glaze_gallery_last_synced_cell(self) -> str:
        return os.environ["GLAZE_GALLERY_LAST_SYNCED_CELL"]

    def _fmt_glaze(self, glaze: str) -> str:
        return "".join(glaze.split()).lower()

    def get_glaze_data(self) -> pd.DataFrame:
        request: HttpRequest = self._spreadsheets.values().get(
            spreadsheetId=self._glaze_gallery_spreadsheet_id,
            range=self._glaze_gallery_data_range,
        )
        response = request.execute()
        values = response["values"]
        # Include the header row in the data to ensure that the first row has the right
        # number of columns, even if some cells at the end are empty. Then select it out.
        return pd.DataFrame(data=values, columns=values[0]).iloc[1:]

    def update_last_synced_cell(self, *, never=True) -> None:
        if never:
            last_updated_date = "NEVER"
        else:
            tz = pytz.timezone("US/Eastern")
            now = datetime.now(tz)
            last_updated_date = now.strftime("%a %b %-d %Y at %-I:%M:%S %p %Z")
        update_message = (
            f"Last synced to sites on {last_updated_date} (computed, do not update)"
        )
        request: HttpRequest = self._spreadsheets.values().update(
            spreadsheetId=self._glaze_gallery_spreadsheet_id,
            range=self._glaze_gallery_last_synced_cell,
            valueInputOption="RAW",
            body={"values": [[update_message]]},
        )
        request.execute()

    def download_glaze_image(
        self,
        file_id: str,
        download_dir: str,
        mime_type: str,
        glaze1: str,
        glaze2: str,
        side: str,
    ):
        extension = mimetypes.guess_extension(mime_type)
        file_name = os.path.join(
            download_dir,
            f"{self._fmt_glaze(glaze1)}-{self._fmt_glaze(glaze2)}-{side}{extension}",
        )
        request: HttpRequest = self._files.get_media(fileId=file_id)
        with open(file_name, "wb") as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
