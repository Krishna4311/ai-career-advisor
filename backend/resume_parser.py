import io
from fastapi import UploadFile
from PyPDF2 import PdfReader
from docx import Document

async def parse_resume(file: UploadFile) -> str:
    """
    Parses the raw text content from an uploaded file (PDF or DOCX).
    """
    content = await file.read()
    if file.content_type == "application/pdf":
        return _parse_pdf(content)
    elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return _parse_docx(content)
    else:
        raise ValueError("Unsupported file type. Please upload a PDF or DOCX file.")

def _parse_pdf(content: bytes) -> str:
    text = ""
    reader = PdfReader(io.BytesIO(content))
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def _parse_docx(content: bytes) -> str:
    text = ""
    doc = Document(io.BytesIO(content))
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text
