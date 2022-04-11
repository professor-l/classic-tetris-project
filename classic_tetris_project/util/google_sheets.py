from google.oauth2 import service_account
from googleapiclient import errors
from googleapiclient.discovery import build

from django.conf import settings


class GoogleSheetsError(Exception):
    pass

class GoogleSheetsService:
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    SERVICE_ACCOUNT_FILE = settings.ENV("GOOGLE_SERVICE_ACCOUNT_FILE")

    def __init__(self):
        if not self.__class__.SERVICE_ACCOUNT_FILE:
            raise GoogleSheetsError("Service account not configured")
        credentials = service_account.Credentials.from_service_account_file(
            self.__class__.SERVICE_ACCOUNT_FILE,
            scopes=self.__class__.SCOPES)
        self.service = build("sheets", "v4", credentials=credentials)

    def update(self, spreadsheet_id, sheet_range, data):
        request = self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=sheet_range,
            valueInputOption="RAW",
            body={ "values": data },
        )
        try:
            return request.execute()
        except errors.HttpError as e:
            raise GoogleSheetsError(e.error_details)

    def append(self, spreadsheet_id, sheet_range, data):
        request = self.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=sheet_range,
            valueInputOption="RAW",
            body={ "values": data },
        )
        try:
            return request.execute()
        except errors.HttpError as e:
            raise GoogleSheetsError(e.error_details)
