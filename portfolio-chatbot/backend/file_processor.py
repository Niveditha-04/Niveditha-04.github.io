import csv
import io
from pathlib import Path


def extract_text(filename: str, content: bytes) -> str:
    ext = Path(filename).suffix.lower()

    if ext == ".pdf":
        try:
            import fitz  # PyMuPDF
            doc   = fitz.open(stream=content, filetype="pdf")
            pages = [page.get_text() for page in doc]
            return "\n\n".join(p for p in pages if p.strip())
        except ImportError:
            return "[PDF support requires PyMuPDF — install with: pip install PyMuPDF]"
        except Exception as e:
            return f"[Could not read PDF: {e}]"

    if ext == ".docx":
        try:
            import docx
            doc  = docx.Document(io.BytesIO(content))
            text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
            return text
        except ImportError:
            return "[DOCX support requires python-docx — install with: pip install python-docx]"
        except Exception as e:
            return f"[Could not read DOCX: {e}]"

    if ext == ".txt":
        return content.decode("utf-8", errors="ignore")

    if ext == ".csv":
        raw    = content.decode("utf-8", errors="ignore")
        reader = csv.reader(io.StringIO(raw))
        return "\n".join(", ".join(row) for row in reader)

    return ""
