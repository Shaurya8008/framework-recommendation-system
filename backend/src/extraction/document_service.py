import logging
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.db.models import Document, DocumentExtraction
from app.schemas import DocumentUploadResponse, AutofillFieldSuggestion
from src.extraction.pdf_extractor import PDFExtractor
from src.extraction.ocr_service import OCRService
from src.extraction.extraction_signal_service import ExtractionSignalService
from src.extraction.profile_autofill_mapper import ProfileAutofillMapper

import tempfile
import os
import hashlib

logger = logging.getLogger(__name__)

class DocumentService:
    @staticmethod
    async def process_document(file: UploadFile, db: Session) -> DocumentUploadResponse:
        # 1. Save file temporarily
        content = await file.read()
        file_hash = hashlib.sha256(content).hexdigest()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name

        try:
            # 2. Create Document record
            db_doc = Document(
                filename=file.filename,
                content_type=file.content_type,
                size_bytes=len(content),
                hash=file_hash
            )
            db.add(db_doc)
            db.commit()
            db.refresh(db_doc)

            # 3. Extract Text
            ext_result = PDFExtractor.extract_text(temp_path)
            extracted_text = ext_result.get("text", "")
            page_count = ext_result.get("page_count", 0)

            # 4. Fallback to OCR if needed
            if OCRService.needs_ocr(extracted_text, page_count):
                logger.info(f"PDF {file.filename} appears to be scanned. Running OCR...")
                ocr_result = OCRService.extract_text_with_ocr(temp_path)
                if ocr_result.get("status") == "success":
                    extracted_text += "\n" + ocr_result.get("text", "")

            if not extracted_text.strip():
                return DocumentUploadResponse(
                    document_id=db_doc.id,
                    status="failed",
                    overall_confidence=0.0,
                    suggestions=[],
                    missing_fields=["industry", "size", "region", "energy_use_level"]
                )

            # 5. Extract Signals
            signals = ExtractionSignalService.extract_signals(extracted_text)

            # 6. Map to Profile Suggestions
            suggestions = ProfileAutofillMapper.map_signals_to_suggestions(signals)
            
            # Calculate overall confidence
            overall_confidence = sum(s.confidence for s in suggestions) / len(suggestions) if suggestions else 0.0

            # 7. Save Extractions to DB
            for suggestion in suggestions:
                db_extraction = DocumentExtraction(
                    document_id=db_doc.id,
                    field_name=suggestion.field,
                    suggested_value=str(suggestion.suggested_value),
                    confidence=suggestion.confidence,
                    source_snippet=suggestion.source_snippet,
                    reason=suggestion.reason
                )
                db.add(db_extraction)
            
            db.commit()

            # Required fields
            all_required = {"industry", "org_size", "region", "annual_energy_use_level"}
            found_fields = {s.field for s in suggestions}
            missing = list(all_required - found_fields)

            return DocumentUploadResponse(
                document_id=db_doc.id,
                status="complete",
                overall_confidence=round(overall_confidence, 2),
                suggestions=suggestions,
                missing_fields=missing
            )

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
