from pathlib import Path
from PyPDF2 import PdfReader
from typing import List


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract text from PDF.
    Args:
        pdf_path (Path): Path to PDF.
    Returns:
        str: Text extracted from PDF.
    """
    reader = PdfReader(str(pdf_path))
    text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)
    return "\n".join(text)

def chunk_text(text:str, chunk_size:int=5000, overlap:int=250) -> List[str]:
    """
    Splits text into overlapping chunks for LLM processing.

    Args:
        text (str): Text to chunk.
        chunk_size (int, optional): Chunk size. Defaults to 5000.
        overlap (int, optional): Overlap size. Defaults to 200.
    Returns:
        list: List of chunks.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks