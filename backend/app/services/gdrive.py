"""Google Drive integration service."""

import io
import json
from datetime import datetime
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from app.models.schemas import GDriveFile
from app.core.config import settings

# Must match scopes in auth.py for token refresh to work correctly
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]


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
                    if (
                        "revoked" in error_msg
                        or "invalid" in error_msg
                        or "expired" in error_msg
                    ):
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
            self._service = build("drive", "v3", credentials=creds)
        return self._service

    def find_folder_id(self, folder_name: str) -> str | None:
        """Find folder ID by name."""
        results = (
            self.service.files()
            .list(
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                spaces="drive",
                fields="files(id, name)",
            )
            .execute()
        )

        files = results.get("files", [])
        return files[0]["id"] if files else None

    def list_pdfs(self, folder_name: str, limit: int = 20) -> list[GDriveFile]:
        """List PDF files in a folder, sorted by date (newest first)."""
        folder_id = self.find_folder_id(folder_name)
        if not folder_id:
            return []

        results = (
            self.service.files()
            .list(
                q=f"'{folder_id}' in parents and mimeType='application/pdf' and trashed=false",
                spaces="drive",
                fields="files(id, name, createdTime, size)",
                orderBy="createdTime desc",
                pageSize=limit,
            )
            .execute()
        )

        files = []
        for f in results.get("files", []):
            files.append(
                GDriveFile(
                    id=f["id"],
                    name=f["name"],
                    created_time=datetime.fromisoformat(
                        f["createdTime"].replace("Z", "+00:00")
                    ),
                    size=int(f.get("size", 0)) if f.get("size") else None,
                )
            )

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


def update_gdrive_cache_sheet_id(data_dir: Path, worksheet_id: str, sheet_id: str):
    """Update a GDrive cache entry's sheet_id after vision model correction.

    When the scanner's OCR produces an incorrect sheet ID in the filename
    (e.g., "B7" instead of "B71"), this corrects the cached value after
    the vision model determines the true sheet ID during processing.
    """
    cache_path = data_dir / "cache" / "gdrive_files.json"
    if not cache_path.exists():
        return

    try:
        cache = json.loads(cache_path.read_text())
    except (json.JSONDecodeError, IOError):
        return

    if "files" not in cache:
        return

    updated = False
    for f in cache["files"]:
        fname = f.get("name", "")
        if fname.endswith(".pdf"):
            fname = fname[:-4]
        if fname == worksheet_id and f.get("sheet_id") != sheet_id:
            f["sheet_id"] = sheet_id
            updated = True
            print(f"Updated GDrive cache: '{worksheet_id}' sheet_id -> '{sheet_id}'")
            break

    if updated:
        cache_path.write_text(json.dumps(cache, indent=2, default=str))
