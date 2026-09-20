from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

flow = InstalledAppFlow.from_client_secrets_file(
    "credentials/credentials.json",
    SCOPES
)

creds = flow.run_local_server(port=0)

service = build("drive", "v3", credentials=creds)

results = service.files().list(
    q="name = 'New_resume - Anchal.pdf' and trashed = false",
    pageSize=10,
    fields="files(id, name, mimeType)"
).execute()

files = results.get("files", [])

for file in files:
    print("Name:", file["name"])
    print("ID:", file["id"])
    print("Type:", file["mimeType"])
    
file_id = files[0]["id"]

request = service.files().get_media(fileId=file_id)

fh = io.FileIO("storage/New_resume.pdf", "wb")

downloader = MediaIoBaseDownload(fh, request)

done = False

while not done:
    status, done = downloader.next_chunk()
    print(f"Download progress: {int(status.progress() * 100)}%")

print("Download complete!")  

from services.extractor import extract_text

text = extract_text("storage/New_resume.pdf")

from services.chunker import chunk_text

chunks = chunk_text(text)

print("\nNumber of chunks:", len(chunks))

print("\nFirst chunk:")
print(chunks[0])

print("\nExtracted text:")
print(text[:1000])  