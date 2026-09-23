import pytest
import os
import sys
import sqlite3

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.knowledge_service import reindex_knowledge_source
from app.rag.database import get_vector_store
from app.db.session import SessionLocal
from app.db.models import KnowledgeSource

def test_reindex_integrity_no_stale_corrupted_chunks():
    fts_db_path = os.path.join(backend_dir, "knowledge_v2.db")
    conn = sqlite3.connect(fts_db_path)
    cur = conn.cursor()
    
    cur.execute("SELECT chunk_id, content FROM knowledge_chunks_fts WHERE source_name LIKE '%Dheerkadharisi%'")
    rows = cur.fetchall()
    conn.close()
    
    assert len(rows) > 0, "Dheerkadharisi chunks must exist in FTS"
    
    # Verify no legacy font artifacts in any indexed chunk
    corrupted = []
    for cid, content in rows:
        if any(x in content for x in [']', '\\`', '`து', 'ஜேமாட்b', 'க]வு', 'டைK']):
            corrupted.append(cid)
            
    assert len(corrupted) == 0, f"Found {len(corrupted)} corrupted chunks: {corrupted}"

def test_reindex_version_metadata():
    vs = get_vector_store()
    results = vs._collection.get(limit=10, where={"source_name": "Dheerkadharisi_A4.pdf"})
    metadatas = results.get("metadatas", [])
    assert len(metadatas) > 0
    
    for meta in metadatas:
        assert meta.get("extraction_version") == "10.1B"
        assert meta.get("embedding_version") == "multilingual-v1"
        assert meta.get("index_version") == "10.1B"
        assert meta.get("language") in ["ta", "en"]
        assert meta.get("chunk_hash") is not None
