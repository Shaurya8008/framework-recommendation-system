import pymupdf
import logging

logger = logging.getLogger(__name__)

class PDFExtractor:
    @staticmethod
    def extract_text(file_path: str) -> dict:
        """
        Extracts text natively from a PDF using PyMuPDF.
        Returns a dict with 'text' and 'page_count'.
        """
        try:
            text_content = []
            doc = pymupdf.open(file_path)
            page_count = len(doc)
            for page in doc:
                text_content.append(page.get_text())
            doc.close()
            return {
                "text": "\n".join(text_content),
                "page_count": page_count,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Failed to extract text from PDF {file_path}: {e}")
            return {
                "text": "",
                "page_count": 0,
                "status": "error",
                "error": str(e)
            }
