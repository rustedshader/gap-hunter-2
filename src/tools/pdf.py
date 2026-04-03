from docling.document_converter import DocumentConverter
from pathlib import Path

def pdf_to_markdown(source: Path) -> str | ValueError:
    if source.suffix != ".pdf": raise ValueError("File must be a PDF.")
    converter = DocumentConverter()
    doc = converter.convert(source).document
    return doc.export_to_markdown()