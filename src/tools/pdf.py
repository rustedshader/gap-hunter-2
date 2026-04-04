from docling.document_converter import DocumentConverter
from pathlib import Path
import re
import logging

logger = logging.getLogger(__name__)


def _decode_mt_codes(text: str) -> str:
    """
    Decode /MT font codes to readable text.
    
    Some PDFs use custom fonts where glyphs are encoded as /MT followed
    by ASCII decimal values. Example: /MT73/MT110/MT102/MT111 -> "Info"
    """
    pattern = r'/MT(\d+)'
    
    def replace_mt(match):
        try:
            code = int(match.group(1))
            if 32 <= code <= 126:  # Printable ASCII range
                return chr(code)
            return match.group(0)
        except (ValueError, OverflowError):
            return match.group(0)
    
    decoded = re.sub(pattern, replace_mt, text)
    
    # Fix spaced-out words (e.g., "r e q u i r e m e n t" -> "requirement")
    # Pattern: single letter followed by space, repeated
    decoded = re.sub(r'\b(\w) (?=\w\b)', r'\1', decoded)
    
    # Clean up excessive spaces but preserve line structure
    lines = decoded.splitlines()
    cleaned_lines = []
    for line in lines:
        # Collapse multiple spaces within a line
        cleaned = re.sub(r' {2,}', ' ', line.strip())
        cleaned_lines.append(cleaned)
    
    return '\n'.join(cleaned_lines)


def pdf_to_markdown(source: Path) -> str | ValueError:
    if source.suffix != ".pdf": 
        raise ValueError("File must be a PDF.")
    
    converter = DocumentConverter()
    doc = converter.convert(source).document
    markdown = doc.export_to_markdown()
    
    # Check for and decode font encoding issues
    if "/MT" in markdown:
        logger.warning("Detected /MT font codes in %s - decoding...", source.name)
        markdown = _decode_mt_codes(markdown)
        logger.info("Successfully decoded /MT codes")
    
    return markdown
