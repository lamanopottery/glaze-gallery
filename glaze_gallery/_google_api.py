from typing import Any
import os
import io
from datetime import datetime
import pytz
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore[import-untyped]
from googleapiclient.discovery import Resource, build  # type: ignore[import-untyped]
from googleapiclient.http import HttpRequest, MediaIoBaseDownload  # type: ignore[import-untyped]

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
        self.creds = self._get_creds(credentials_path, token_path, scopes)

    def _get_creds(self, creds_path: str, token_path: str, scopes: list[str]) -> Any:
        creds = None
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, scopes)  # type: ignore[no-untyped-call]
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())  # type: ignore[no-untyped-call]
            else:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, scopes)
                creds = flow.run_local_server(port=0)
            with open(token_path, "w") as token:
                token.write(creds.to_json())
        return creds

    @property
    def _spreadsheets(self) -> Resource:
        return build("sheets", "v4", credentials=self.creds).spreadsheets()

    @property
    def _files(self) -> Resource:
        return build("drive", "v3", credentials=self.creds).files()

    @property
    def _glaze_gallery_spreadsheet_id(self) -> str:
        return os.environ["GLAZE_GALLERY_SPREADSHEET_ID"]

    def get_glaze_data(self) -> pd.DataFrame:
        request: HttpRequest = self._spreadsheets.values().get(
            spreadsheetId=self._glaze_gallery_spreadsheet_id,
            range=os.environ["GLAZE_GALLERY_DATA_RANGE"],
        )
        response = request.execute()
        values = response["values"]
        # Include the header row in the data to ensure that the first row has the right
        # number of columns, even if some cells at the end are empty. Then select it out.
        # None values can occur when the row is empty at the end. For consistency, we
        # replace them with empty strings.
        return pd.DataFrame(data=values, columns=values[0]).iloc[1:].fillna(value="")

    def update_last_synced_cell(self, *, never: bool = False) -> None:
        if never:
            last_updated_date = "NEVER"
        else:
            tz = pytz.timezone("US/Eastern")
            now = datetime.now(tz)
            last_updated_date = now.strftime("%a %b %-d %Y at %-I:%M:%S %p %Z")
        update_message = f"Last synced to sites on {last_updated_date}"
        request: HttpRequest = self._spreadsheets.values().update(
            spreadsheetId=self._glaze_gallery_spreadsheet_id,
            range=os.environ["GLAZE_GALLERY_LAST_SYNCED_CELL"],
            valueInputOption="RAW",
            body={"values": [[update_message]]},
        )
        request.execute()

    def download_glaze_image(self, file_id: str) -> io.BytesIO:
        request: HttpRequest = self._files.get_media(fileId=file_id)
        image_bytes = io.BytesIO()
        downloader = MediaIoBaseDownload(image_bytes, request)
        done = False
        while done is False:
            _, done = downloader.next_chunk()
        return image_bytes
