import os
from langchain_core.documents import Document
from app.rag.loaders import get_loader_for_file
from app.db.session import SessionLocal
from app.db.models import KnowledgeSource
from app.services.knowledge_service import process_knowledge_source
from app.services.ocr_service import get_ocr_engine, detect_tamil_unicode

def ingest_document(file_path: str, filename: str, persona_id: str) -> str:
    db = SessionLocal()
    # Create DB Record immediately
    source = KnowledgeSource(
        persona_id=persona_id,
        name=filename,
        source_type="UPLOAD",
        original_filename=filename,
        status="PROCESSING"
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    source_id = source.id
    db.close()
    
    try:
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        page_documents = []
        full_text = ""
        
        if ext == 'pdf':
            ocr_engine = get_ocr_engine()
            ocr_results = ocr_engine.process_pdf(file_path)
            
            successful_pages = [r for r in ocr_results if r.text and len(r.text.strip()) > 0]
            if not successful_pages:
                failed_reasons = [r.error_message for r in ocr_results if r.error_message]
                reason_str = "; ".join(failed_reasons[:2]) if failed_reasons else "No usable text extracted from PDF pages."
                raise ValueError(f"OCR/Text extraction failed: {reason_str}")
                
            for res in ocr_results:
                if res.text and res.text.strip():
                    p_doc = Document(
                        page_content=res.text,
                        metadata={
                            "page": res.page_number,
                            "ocr_status": res.status,
                            "ocr_provider": res.provider,
                            "ocr_language": res.language,
                            "is_tamil": res.tamil_detected,
                            "tamil_char_count": res.tamil_char_count,
                            "original_filename": filename
                        }
                    )
                    page_documents.append(p_doc)
            full_text = "\n\n".join([doc.page_content for doc in page_documents])
        else:
            # Extract non-PDF documents
            loader = get_loader_for_file(file_path)
            raw_docs = loader.load()
            for idx, r_doc in enumerate(raw_docs):
                p_num = r_doc.metadata.get("page", idx + 1)
                tamil_info = detect_tamil_unicode(r_doc.page_content)
                p_doc = Document(
                    page_content=r_doc.page_content,
                    metadata={
                        "page": p_num,
                        "ocr_status": "NOT_REQUIRED",
                        "ocr_provider": "native_loader",
                        "ocr_language": tamil_info["language"],
                        "is_tamil": tamil_info["has_tamil"],
                        "tamil_char_count": tamil_info["tamil_chars"],
                        "original_filename": filename
                    }
                )
                page_documents.append(p_doc)
            full_text = "\n\n".join([doc.page_content for doc in page_documents])
        
        # Pass to unified pipeline
        process_knowledge_source(
            source_id=source_id,
            text_content=full_text,
            metadata={"original_filename": filename},
            page_documents=page_documents
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        db = SessionLocal()
        source = db.query(KnowledgeSource).filter(KnowledgeSource.id == source_id).first()
        if source:
            source.status = "FAILED"
            source.error_message = str(e)
            db.commit()
        db.close()
        
    return source_id

