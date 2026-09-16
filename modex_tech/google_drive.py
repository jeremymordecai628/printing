#!/usr/bin/python3

"""
Google Drive file upload integration for Flask.

Required environment variables:
    GOOGLE_DRIVE_FOLDER_ID
    GOOGLE_SERVICE_ACCOUNT_FILE

Python modules:
    google-api-python-client
        Provides the Google Drive API client.

    google-auth
        Handles Google authentication and credentials.

    google-auth-httplib2
        Provides HTTP transport for Google API authentication.

    google-auth-oauthlib
        Provides OAuth-related authentication support.
"""

import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


SCOPES = ["https://www.googleapis.com/auth/drive"]


def get_drive_service():
    """
    Create and return an authenticated Google Drive service.
    """

    credentials_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")

    if not credentials_file:
        raise RuntimeError(
            "GOOGLE_SERVICE_ACCOUNT_FILE is not configured"
        )

    credentials = service_account.Credentials.from_service_account_file(
        credentials_file,
        scopes=SCOPES
    )

    return build(
        "drive",
        "v3",
        credentials=credentials
    )


def upload_to_google_drive(file_storage):
    """
    Upload a Flask FileStorage object to Google Drive.

    Args:
        file_storage:
            Flask request.files file object.

    Returns:
        Dictionary containing Google Drive file information.
    """

    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

    if not folder_id:
        raise RuntimeError(
            "GOOGLE_DRIVE_FOLDER_ID is not configured"
        )

    if not file_storage:
        raise ValueError("No file supplied")

    filename = file_storage.filename

    if not filename:
        raise ValueError("File has no filename")

    drive_service = get_drive_service()

    file_metadata = {
        "name": filename,
        "parents": [folder_id]
    }

    media = MediaIoBaseUpload(
        file_storage.stream,
        mimetype=file_storage.mimetype or "application/octet-stream",
        resumable=True
    )

    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id,name,mimeType,size,webViewLink,createdTime"
    ).execute()

    return uploaded_file