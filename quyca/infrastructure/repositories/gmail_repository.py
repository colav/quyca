import os
import pickle
import base64
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from flask import current_app

"""
Gmail API repository to send HTML emails with attachments.
"""


class GmailRepository:
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
    """
    Loads pickled credentials from config, validates scopes and builds service client.
    """

    def __init__(self):
        credentials_path = current_app.config.get("GOOGLE_CREDENTIALS")
        if not credentials_path:
            raise ValueError("GOOGLE_CREDENTIALS no está configurado")
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"No se encontró el archivo {credentials_path}")

        with open(credentials_path, "rb") as f:
            creds = pickle.load(f)

        if getattr(creds, "expired", False) and getattr(creds, "refresh_token", None):
            creds.refresh(Request())

        scopes = set(getattr(creds, "scopes", []) or [])
        if not scopes or not set(self.SCOPES).issubset(scopes):
            raise ValueError(f"El token no tiene permisos necesarios: {self.SCOPES}")

        self.service = build("gmail", "v1", credentials=creds)

    def send_email(self, to_email: str, subject: str, body_html: str, attachments: list[dict]) -> dict:
        message = MIMEMultipart()
        message["to"] = to_email
        message["subject"] = subject
        message.attach(MIMEText(body_html, "html", "utf-8"))

        for att in attachments:
            part = MIMEBase(*att["mime"].split("/"))
            part.set_payload(att["bytes"].getvalue())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{att["filename"]}"')
            message.attach(part)

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        try:
            sent = self.service.users().messages().send(userId="me", body={"raw": raw}).execute()
            return {"success": True, "id": sent.get("id")}
        except HttpError as e:
            return {"success": False, "error": str(e)}
