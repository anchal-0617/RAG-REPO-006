import os
import io
import shutil
import re
import json

from fastapi import APIRouter, UploadFile, File
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from app.services.extractor import extract_text
from app.services.chunker import chunk_text
from app.services.embedding_service import create_embeddings
from app.services.faiss_service import (
    create_faiss_index,
    store_chunks,
    store_index
)
from app.services.metadata_service import create_metadata

router = APIRouter()

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

UPLOAD_DIR = os.path.join(BASE_DIR, "storage")

CREDENTIALS_PATH = os.path.join(
    BASE_DIR,
    "credentials",
    "credentials.json"
)

STATE_PATH = os.path.join(
    BASE_DIR,
    "sync_state.json"
)

os.makedirs(UPLOAD_DIR, exist_ok=True)


def clean_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def rebuild_index(all_chunks, all_metadata):
    if not all_chunks:
        return

    embeddings = create_embeddings(all_chunks)

    index = create_faiss_index(embeddings)

    store_chunks(
        all_chunks,
        all_metadata
    )

    store_index(index)


@router.post("/upload-doc")
async def upload_document(file: UploadFile = File(...)):

    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = extract_text(file_path)

    text = clean_text(text)

    chunks = chunk_text(text)

    if not chunks:
        return {
            "error": "No text could be extracted from the document"
        }

    metadata = create_metadata(
        chunks,
        file.filename,
        source="local"
    )

    if os.path.exists(STATE_PATH):

        with open(STATE_PATH, "r") as f:

            try:
                sync_state = json.load(f)
            except json.JSONDecodeError:
                sync_state = {}

    else:
        sync_state = {}

    local_id = "local_" + file.filename

    sync_state[local_id] = {
        "filename": file.filename,
        "modifiedTime": str(os.path.getmtime(file_path)),
        "chunks": chunks,
        "metadata": metadata,
        "source": "local"
    }

    with open(STATE_PATH, "w") as f:

        json.dump(
            sync_state,
            f,
            indent=4
        )

    all_chunks = []
    all_metadata = []

    for data in sync_state.values():

        all_chunks.extend(
            data.get("chunks", [])
        )

        all_metadata.extend(
            data.get("metadata", [])
        )

    rebuild_index(
        all_chunks,
        all_metadata
    )

    return {
        "message": "Document uploaded successfully",
        "file": file.filename,
        "chunks": len(chunks)
    }


@router.post("/sync-drive")
def sync_drive():

    SCOPES = [
        "https://www.googleapis.com/auth/drive.readonly"
    ]

    flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_PATH,
        SCOPES
    )

    creds = flow.run_local_server(port=0)

    service = build(
        "drive",
        "v3",
        credentials=creds
    )

    if os.path.exists(STATE_PATH):

        with open(STATE_PATH, "r") as f:

            try:
                sync_state = json.load(f)
            except json.JSONDecodeError:
                sync_state = {}

    else:
        sync_state = {}

    results = service.files().list(
        q="trashed = false",
        pageSize=100,
        fields="files(id, name, mimeType, modifiedTime)"
    ).execute()

    files = results.get("files", [])

    supported_files = []

    for file in files:

        if file["mimeType"] in [
            "application/pdf",
            "text/plain",
            "application/vnd.google-apps.document"
        ]:

            supported_files.append(file)

    new_files = 0
    changed_files = 0
    skipped_files = 0

    current_drive_ids = set()

    for file in supported_files:

        file_id = file["id"]
        file_name = file["name"]
        mime_type = file["mimeType"]
        modified_time = file["modifiedTime"]

        current_drive_ids.add(file_id)

        previous = sync_state.get(file_id)

        if (
            previous
            and previous.get("modifiedTime") == modified_time
            and previous.get("source") == "gdrive"
        ):

            skipped_files += 1

            continue

        if previous:

            changed_files += 1

        else:

            new_files += 1

        if mime_type == "application/vnd.google-apps.document":

            file_path = os.path.join(
                UPLOAD_DIR,
                file_name + ".txt"
            )

            request = service.files().export_media(
                fileId=file_id,
                mimeType="text/plain"
            )

        else:

            file_path = os.path.join(
                UPLOAD_DIR,
                file_name
            )

            request = service.files().get_media(
                fileId=file_id
            )

        fh = io.FileIO(
            file_path,
            "wb"
        )

        downloader = MediaIoBaseDownload(
            fh,
            request
        )

        done = False

        while not done:

            status, done = downloader.next_chunk()

        fh.close()

        text = extract_text(file_path)

        text = clean_text(text)

        chunks = chunk_text(text)

        if not chunks:
            continue

        metadata = create_metadata(
            chunks,
            file_name,
            source="gdrive",
            doc_id=file_id
        )

        sync_state[file_id] = {
            "filename": file_name,
            "modifiedTime": modified_time,
            "chunks": chunks,
            "metadata": metadata,
            "source": "gdrive"
        }

    deleted_drive_ids = []

    for key, data in sync_state.items():

        if data.get("source") == "gdrive":

            if key not in current_drive_ids:

                deleted_drive_ids.append(key)

    for key in deleted_drive_ids:

        del sync_state[key]

    with open(STATE_PATH, "w") as f:

        json.dump(
            sync_state,
            f,
            indent=4
        )

    all_chunks = []
    all_metadata = []

    for data in sync_state.values():

        all_chunks.extend(
            data.get("chunks", [])
        )

        all_metadata.extend(
            data.get("metadata", [])
        )

    if not all_chunks:

        return {
            "message": "No documents available",
            "new_files": new_files,
            "changed_files": changed_files,
            "skipped_files": skipped_files
        }

    rebuild_index(
        all_chunks,
        all_metadata
    )

    return {
        "message": "Incremental sync completed",
        "new_files": new_files,
        "changed_files": changed_files,
        "skipped_files": skipped_files,
        "chunks": len(all_chunks)
    }