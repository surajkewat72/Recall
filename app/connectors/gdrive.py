import os
import io
from typing import List, Dict, Any

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Scopes needed for read-only access to Drive
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

class GoogleDriveConnector:
    """
    Handles authentication and interactions with the Google Drive API.
    """
    def __init__(self, credentials_file: str, token_file: str):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None

    def authenticate(self):
        """Authenticate with Google Drive API (supports Service Account and OAuth)."""
        # 1. Try Service Account (Production/Deployment method)
        if os.path.exists(self.credentials_file):
            try:
                # Check if it's a service account file
                import json
                with open(self.credentials_file, 'r') as f:
                    data = json.load(f)
                    if data.get('type') == 'service_account':
                        print("Authenticating with Service Account...")
                        creds = service_account.Credentials.from_service_account_file(
                            self.credentials_file, scopes=SCOPES
                        )
                        self.service = build('drive', 'v3', credentials=creds)
                        return
            except Exception:
                pass # Fall back to OAuth if service account fails

        # 2. Try OAuth (Local testing method)
        creds = None
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
            
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=8080)
                
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())

        self.service = build('drive', 'v3', credentials=creds)

    def list_files(self) -> List[Dict[str, Any]]:
        """
        Fetch files from Google Drive matching the required types.
        Filters for: PDF, Google Docs, TXT.
        """
        if not self.service:
            raise Exception("Google Drive service not authenticated. Call authenticate() first.")
            
        # Mime types to search for
        mime_types = [
            "application/pdf",
            "application/vnd.google-apps.document",
            "text/plain"
        ]
        
        # Build query string
        query_parts = [f"mimeType='{mt}'" for mt in mime_types]
        query = " or ".join(query_parts)
        # Only fetch files that are not trashed
        query = f"({query}) and trashed = false"

        results = self.service.files().list(
            q=query,
            pageSize=100,
            fields="nextPageToken, files(id, name, mimeType, modifiedTime)"
        ).execute()
        
        items = results.get('files', [])
        return items
        
    def download_file(self, file_id: str, file_name: str, mime_type: str, download_dir: str = "downloads") -> str:
        """
        Download a specific file from Google Drive.
        Google Docs are exported as DOCX.
        Binary files (PDF, TXT) are downloaded directly.
        Returns the path to the downloaded file.
        """
        if not self.service:
            raise Exception("Google Drive service not authenticated. Call authenticate() first.")
            
        os.makedirs(download_dir, exist_ok=True)
        
        # Handle Google Doc export
        if mime_type == "application/vnd.google-apps.document":
            request = self.service.files().export_media(
                fileId=file_id,
                mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            # Append .docx to filename if not present
            if not file_name.endswith('.docx'):
                file_name += '.docx'
        else:
            # Handle standard binary download (PDF, TXT)
            request = self.service.files().get_media(fileId=file_id)
            
        file_path = os.path.join(download_dir, file_name)
        
        with io.FileIO(file_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                
        return file_path
