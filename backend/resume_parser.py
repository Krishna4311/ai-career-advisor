import io
from fastapi import UploadFile, HTTPException
from pypdf import PdfReader
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
        raise HTTPException(status_code=415, detail="Unsupported file type. Please upload a PDF or DOCX file.")

def _parse_pdf(content: bytes) -> str:
    text = ""
    try:
        reader = PdfReader(io.BytesIO(content))
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:

        print(f"!!! CRITICAL ERROR: PyPDF2 failed to parse PDF: {e} !!!")

        raise HTTPException(status_code=422, detail="Failed to parse PDF. The file may be corrupt or encrypted.")

def _parse_docx(content: bytes) -> str:
    text = ""
    try:
        doc = Document(io.BytesIO(content))
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        print(f"!!! CRITICAL ERROR: python-docx failed to parse DOCX: {e} !!!")
        raise HTTPException(status_code=4.22, detail="Failed to parse .docx file. The file may be corrupt.")