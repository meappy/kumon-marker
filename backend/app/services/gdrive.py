"""Google Drive integration service."""

import io
from datetime import datetime
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from app.models.schemas import GDriveFile
from app.core.config import settings

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


def get_token_path() -> Path:
    """Get path to Google token file."""
    return Path(settings.data_dir) / "google_token.json"


class GDriveService:
    """Google Drive service for listing and downloading files."""

    def __init__(self, token_path: Path | None = None):
        self.token_path = token_path or get_token_path()
        self._service = None

    def _get_credentials(self) -> Credentials:
        """Get or refresh Google OAuth credentials."""
        if not self.token_path.exists():
            raise FileNotFoundError(
                "Google Drive not connected. Please connect via Settings."
            )

        creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self.token_path.write_text(creds.to_json())
                except Exception as e:
                    # Token refresh failed - likely revoked or invalid
                    error_msg = str(e).lower()
                    if "revoked" in error_msg or "invalid" in error_msg or "expired" in error_msg:
                        raise FileNotFoundError(
                            "Google Drive access was revoked. Please reconnect via Settings."
                        )
                    raise FileNotFoundError(
                        f"Failed to refresh Google Drive token: {e}. Please reconnect via Settings."
                    )
            else:
                # Token is invalid and can't be refreshed
                raise FileNotFoundError(
                    "Google Drive token expired. Please reconnect via Settings."
                )

        return creds

    @property
    def service(self):
        """Get authenticated Google Drive service (lazy init)."""
        if self._service is None:
            creds = self._get_credentials()
            self._service = build('drive', 'v3', credentials=creds)
        return self._service

    def find_folder_id(self, folder_name: str) -> str | None:
        """Find folder ID by name."""
        results = self.service.files().list(
            q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
            spaces='drive',
            fields='files(id, name)'
        ).execute()

        files = results.get('files', [])
        return files[0]['id'] if files else None

    def list_pdfs(self, folder_name: str, limit: int = 20) -> list[GDriveFile]:
        """List PDF files in a folder, sorted by date (newest first)."""
        folder_id = self.find_folder_id(folder_name)
        if not folder_id:
            return []

        results = self.service.files().list(
            q=f"'{folder_id}' in parents and mimeType='application/pdf' and trashed=false",
            spaces='drive',
            fields='files(id, name, createdTime, size)',
            orderBy='createdTime desc',
            pageSize=limit,
        ).execute()

        files = []
        for f in results.get('files', []):
            files.append(GDriveFile(
                id=f['id'],
                name=f['name'],
                created_time=datetime.fromisoformat(f['createdTime'].replace('Z', '+00:00')),
                size=int(f.get('size', 0)) if f.get('size') else None,
            ))

        return files

    def download_file(self, file_id: str, dest_path: Path) -> None:
        """Download a file from Google Drive."""
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        dest_path.write_bytes(fh.getvalue())

    def download_file_bytes(self, file_id: str) -> bytes:
        """Download a file from Google Drive and return bytes."""
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        return fh.getvalue()
