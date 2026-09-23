import hashlib
import unicodedata
from app.rag.text_splitter import RecursiveCharacterTextSplitter
from app.rag.database import get_vector_store
from app.rag.fts_database import index_chunk_fts, delete_source_chunks_fts
from app.db.session import SessionLocal
from app.db.models import KnowledgeSource, Entity, DatasetSchema, StructuredRecord, ExplicitFact
from sqlalchemy.orm import Session
from langchain_core.documents import Document
from app.services.extraction_service import detect_entity, detect_dataset_schema, normalize_table_records, extract_explicit_facts
from app.services.ocr_service import decode_legacy_tamil_font, detect_tamil_unicode

EXTRACTION_VERSION = "10.1B"
EMBEDDING_VERSION = "multilingual-v1"
OCR_VERSION = "10.1A"
INDEX_VERSION = "10.1B"

def process_knowledge_source(
    source_id: str,
    text_content: str = "",
    metadata: dict = None,
    raw_records: list[dict] = None,
    page_documents: list[Document] = None
):
    metadata = metadata or {}
    db: Session = SessionLocal()
    source_record = db.query(KnowledgeSource).filter(KnowledgeSource.id == source_id).first()
    
    if not source_record:
        db.close()
        return

    try:
        source_title = metadata.get("source_title", source_record.name)
        
        # Invalidate/delete old chunks from Chroma and FTS to ensure idempotence
        try:
            vector_store = get_vector_store()
            vector_store._collection.delete(where={"knowledge_source_id": source_id})
        except Exception:
            pass
        try:
            delete_source_chunks_fts(source_id)
        except Exception:
            pass
        
        # Clean existing SQL records for this source
        db.query(StructuredRecord).filter(StructuredRecord.source_id == source_id).delete()
        db.query(ExplicitFact).filter(ExplicitFact.source_id == source_id).delete()
        db.commit()

        # Combine text for entity and fact extraction if full text not provided
        if not text_content and page_documents:
            text_content = "\n\n".join([doc.page_content for doc in page_documents if doc.page_content])
            
        # Decode any legacy font corruption in the full text
        if text_content:
            text_content = decode_legacy_tamil_font(text_content)
            text_content = unicodedata.normalize("NFC", text_content)

        # 1. Detect Entity
        entity_info = detect_entity(source_title, text_content)
        entity_name = entity_info["entity_name"]
        
        entity = db.query(Entity).filter(Entity.name == entity_name, Entity.persona_id == source_record.persona_id).first()
        if not entity:
            entity = Entity(persona_id=source_record.persona_id, name=entity_name, aliases=entity_info["aliases"])
            db.add(entity)
            db.commit()
            db.refresh(entity)
            
        source_record.entity_id = entity.id
        db.commit()

        docs = []
        dataset = None
        
        # 2. Process Structured Records
        if raw_records and len(raw_records) > 0:
            headers = list(raw_records[0].keys())
            schema_info = detect_dataset_schema(entity_name, headers, raw_records)
            
            dataset = DatasetSchema(
                entity_id=entity.id,
                dataset_type=schema_info["dataset_type"],
                primary_fields=schema_info["primary_fields"],
                attributes=schema_info["attributes"],
                sortable_fields=schema_info["sortable_fields"],
                filterable_fields=schema_info["filterable_fields"]
            )
            db.add(dataset)
            db.commit()
            db.refresh(dataset)
            
            normalized = normalize_table_records(dataset.dataset_type, raw_records)
            
            for idx, (raw_rec, norm_rec) in enumerate(zip(raw_records, normalized)):
                db_record = StructuredRecord(
                    dataset_id=dataset.id,
                    source_id=source_id,
                    entity_id=entity.id,
                    record_index=idx,
                    original_row_number=idx+1,
                    raw_data=raw_rec,
                    normalized_data=norm_rec
                )
                db.add(db_record)
                
                # Create a text chunk for hybrid retrieval
                record_meta = metadata.copy()
                record_meta.update(norm_rec)
                record_meta["content_type"] = "structured_record"
                record_meta["dataset_type"] = dataset.dataset_type
                record_meta["entity_name"] = entity_name
                record_meta["page"] = 1
                
                content_str = " | ".join(f"{k.capitalize()}: {v}" for k, v in raw_rec.items())
                docs.append(Document(page_content=content_str, metadata=record_meta))
                
            db.commit()
            
        # 3. Extract Explicit Facts
        facts = extract_explicit_facts(entity_name, text_content)
        for f in facts:
            db_fact = ExplicitFact(
                entity_id=entity.id,
                source_id=source_id,
                subject=f.get("subject", entity_name),
                predicate=f.get("predicate", "unknown"),
                object_val=str(f.get("object", "")),
                year=f.get("year"),
                position=f.get("position")
            )
            db.add(db_fact)
        db.commit()
                
        # 4. Clean & Chunk regular text with page provenance
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        if page_documents and len(page_documents) > 0:
            for p_doc in page_documents:
                clean_page_text = decode_legacy_tamil_font(p_doc.page_content) if p_doc.page_content else ""
                clean_page_text = unicodedata.normalize("NFC", clean_page_text).strip()
                if clean_page_text:
                    p_meta = metadata.copy()
                    p_meta.update(p_doc.metadata)
                    split_p_docs = text_splitter.split_documents([
                        Document(page_content=clean_page_text, metadata=p_meta)
                    ])
                    docs.extend(split_p_docs)
        elif text_content and text_content.strip():
            raw_meta = metadata.copy()
            if "page" not in raw_meta:
                raw_meta["page"] = 1
            raw_doc = Document(page_content=text_content, metadata=raw_meta)
            docs.extend(text_splitter.split_documents([raw_doc]))
        
        chunk_count = len(docs)
        
        # 5. Add complete metadata and deterministic hashes to each chunk
        for i, doc in enumerate(docs):
            tamil_info = detect_tamil_unicode(doc.page_content)
            chunk_lang = "ta" if tamil_info.get("has_tamil") else "en"
            chunk_page = doc.metadata.get("page", 1)
            chunk_hash = hashlib.sha256(f"{source_id}_{chunk_page}_{doc.page_content}".encode("utf-8")).hexdigest()
            
            doc.metadata.update({
                "persona_id": source_record.persona_id,
                "knowledge_source_id": source_id,
                "entity_id": entity.id,
                "entity_name": entity_name,
                "dataset_type": dataset.dataset_type if dataset else "text",
                "source_type": source_record.source_type,
                "source_name": source_record.name,
                "source_url": source_record.source_url or "",
                "page": chunk_page,
                "chunk_index": i,
                "total_chunks": chunk_count,
                "language": chunk_lang,
                "canonical_text": doc.page_content,
                "chunk_hash": chunk_hash,
                "extraction_version": EXTRACTION_VERSION,
                "embedding_version": EMBEDDING_VERSION,
                "ocr_version": OCR_VERSION,
                "index_version": INDEX_VERSION
            })
            # Ensure no complex types in Chroma metadata (must be string, int, float, bool)
            doc.metadata = {k: v for k, v in doc.metadata.items() if isinstance(v, (str, int, float, bool))}
            
        # 6. Store in ChromaDB and FTS5
        if chunk_count > 0:
            vector_store = get_vector_store()
            vector_store.add_documents(docs)
            for i, doc in enumerate(docs):
                chunk_id = f"{source_id}_{i}"
                index_chunk_fts(
                    chunk_id=chunk_id,
                    persona_id=source_record.persona_id,
                    source_id=source_id,
                    source_name=source_record.name,
                    content=doc.page_content,
                    page=doc.metadata.get("page", 1)
                )
            
        # 7. Update Database Tracking
        source_hash = hashlib.sha256(f"{source_id}_{text_content}".encode("utf-8")).hexdigest()
        source_record.content_hash = source_hash
        source_record.chunk_count = chunk_count
        source_record.status = "COMPLETED"
        db.commit()

    except Exception as e:
        import traceback
        traceback.print_exc()
        source_record.status = "FAILED"
        source_record.error_message = str(e)
        db.commit()
    finally:
        db.close()

def reindex_knowledge_source(source_id: str, new_text_content: str = None, page_documents: list[Document] = None) -> dict:
    """
    Safely reindexes an existing knowledge source, purging stale/corrupted chunks,
    re-extracting canonical representations, generating fresh embeddings, and updating FTS5.
    """
    db = SessionLocal()
    source = db.query(KnowledgeSource).filter(KnowledgeSource.id == source_id).first()
    if not source:
        db.close()
        return {"status": "error", "message": f"Knowledge source {source_id} not found."}
    
    source_name = source.name
    persona_id = source.persona_id
    db.close()

    # Reprocess using canonical text / page documents
    process_knowledge_source(
        source_id=source_id,
        text_content=new_text_content or "",
        metadata={"source_title": source_name, "original_filename": source_name},
        page_documents=page_documents
    )

    db = SessionLocal()
    updated_source = db.query(KnowledgeSource).filter(KnowledgeSource.id == source_id).first()
    result = {
        "status": "success",
        "source_id": source_id,
        "source_name": source_name,
        "persona_id": persona_id,
        "chunk_count": updated_source.chunk_count if updated_source else 0,
        "content_hash": updated_source.content_hash if updated_source else None,
        "extraction_version": EXTRACTION_VERSION,
        "embedding_version": EMBEDDING_VERSION,
        "index_version": INDEX_VERSION
    }
    db.close()
    return result

def get_all_knowledge_sources(persona_id: str):
    db = SessionLocal()
    sources = db.query(KnowledgeSource).filter(KnowledgeSource.persona_id == persona_id).order_by(KnowledgeSource.created_at.desc()).all()
    result = []
    for s in sources:
        result.append({
            "id": s.id,
            "name": s.name,
            "source_type": s.source_type,
            "source_url": s.source_url,
            "status": s.status,
            "chunk_count": s.chunk_count,
            "source_count": s.source_count,
            "created_at": s.created_at.isoformat()
        })
    db.close()
    return result

def get_knowledge_source_status(source_id: str):
    db = SessionLocal()
    source = db.query(KnowledgeSource).filter(KnowledgeSource.id == source_id).first()
    db.close()
    if not source:
        return None
    return {
        "id": source.id,
        "status": source.status,
        "chunk_count": source.chunk_count,
        "error_message": source.error_message
    }

def delete_knowledge_source(source_id: str):
    db = SessionLocal()
    source = db.query(KnowledgeSource).filter(KnowledgeSource.id == source_id).first()
    if source:
        try:
            vector_store = get_vector_store()
            collection = vector_store._collection
            collection.delete(where={"knowledge_source_id": source_id})
        except Exception:
            pass
        
        try:
            delete_source_chunks_fts(source_id)
        except Exception:
            pass
            
        db.delete(source)
        db.commit()
    db.close()

