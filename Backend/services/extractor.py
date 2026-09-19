from pypdf import PdfReader
from docx import Document

def extract_text(file_path: str) -> str:
    text = ""
    lower_path = file_path.lower()

    if lower_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    elif lower_path.endswith(".docx"):
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"

    elif lower_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            text = file.read()

    else:
        return "Unsupported file type"

    return text