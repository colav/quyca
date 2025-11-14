import os
import pickle
from typing import Optional
from flask import current_app
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

"""
Google Drive API repository for folders resolution and file upload.
"""


class GoogleDriveRepository:
    SCOPES = ["https://www.googleapis.com/auth/drive"]
    """
    Loads credentials from config, validates Drive scope, builds v3 client.
    """

    def __init__(self):
        credentials_path = current_app.config.get("GOOGLE_CREDENTIALS")
        if not credentials_path:
            raise ValueError("GOOGLE_CREDENTIALS no está configurado")
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"No se encontró el archivo {credentials_path }")

        with open(credentials_path, "rb") as f:
            creds = pickle.load(f)

        if getattr(creds, "expired", False) and getattr(creds, "refresh_token", None):
            creds.refresh(Request())

        if not getattr(creds, "valid", False) or not set(self.SCOPES).issubset(set(getattr(creds, "scopes", []) or [])):
            raise ValueError("El token no tiene los permisos necesarios. Regenera el token con el scope de Drive.")

        self.service = build("drive", "v3", credentials=creds)

    """
    Resolves shortcut folders to target IDs when necessary.
    """

    def resolve_folder_id(self, folder_id: str) -> str:
        try:
            folder = (
                self.service.files()
                .get(fileId=folder_id, fields="id, name, mimeType, shortcutDetails", supportsAllDrives=True)
                .execute()
            )

            if folder.get("mimeType") == "application/vnd.google-apps.shortcut":
                return folder["shortcutDetails"]["targetId"]
            return folder_id
        except HttpError as e:
            raise ValueError(f"No se pudo acceder al folder_id { folder_id }: {e}")

    """
    Finds or creates a Drive folder under an optional parent.
    """

    def get_or_create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> str:
        if parent_id is None:
            parent_id = current_app.config["GOOGLE_PARENT_ID"]
        if parent_id:
            parent_id = self.resolve_folder_id(parent_id)
            query = f"name = '{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false and '{parent_id}' in parents"
        else:
            query = f"name = '{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"

        results = (
            self.service.files()
            .list(
                q=query,
                spaces="drive",
                fields="files(id, name)",
                pageSize=1,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            )
            .execute()
        )

        folders = results.get("files", [])
        if folders:
            return folders[0]["id"]

        folder_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id] if parent_id else [],
        }
        folder = self.service.files().create(body=folder_metadata, fields="id", supportsAllDrives=True).execute()
        return folder["id"]

    """
    Uploads a file into a target folder and returns its web view link.
    """

    def upload_file(self, filepath: str, filename: str, folder_id: str) -> str:
        folder_id = self.resolve_folder_id(folder_id)
        file_metadata = {"name": filename, "parents": [folder_id]}
        media = MediaFileUpload(filepath, resumable=True)
        file = (
            self.service.files()
            .create(body=file_metadata, media_body=media, fields="id, webViewLink", supportsAllDrives=True)
            .execute()
        )

        return file.get("webViewLink")
