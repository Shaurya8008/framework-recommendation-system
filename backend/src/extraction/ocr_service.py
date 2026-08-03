import logging
import pytesseract
import pymupdf
from PIL import Image
import io

logger = logging.getLogger(__name__)

class OCRService:
    @staticmethod
    def is_ocr_available() -> bool:
        """Checks if tesseract is installed on the system."""
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    @staticmethod
    def extract_text_with_ocr(file_path: str, max_pages: int = 10) -> dict:
        """
        Renders pages to images and runs OCR.
        Limits to max_pages to avoid excessive processing time for large PDFs.
        """
        if not OCRService.is_ocr_available():
            logger.warning("OCR requested but Tesseract is not available.")
            return {"text": "", "status": "unavailable"}

        try:
            doc = pymupdf.open(file_path)
            ocr_text = []
            
            # Limit pages for performance
            pages_to_process = min(len(doc), max_pages)
            
            for page_num in range(pages_to_process):
                page = doc[page_num]
                # Render to high-resolution image
                pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                text = pytesseract.image_to_string(img)
                ocr_text.append(text)
                
            doc.close()
            return {
                "text": "\n".join(ocr_text),
                "status": "success",
                "pages_ocred": pages_to_process
            }
        except Exception as e:
            logger.error(f"OCR failed for {file_path}: {e}")
            return {"text": "", "status": "error", "error": str(e)}

    @staticmethod
    def needs_ocr(extracted_text: str, page_count: int) -> bool:
        """
        Heuristics to decide if OCR is needed.
        If the extracted text is very short compared to the page count, it's likely a scanned PDF.
        """
        if page_count == 0:
            return False
            
        text_length = len(extracted_text.strip())
        # If less than 100 characters per page on average, probably needs OCR
        if text_length / page_count < 100:
            return True
            
        return False
