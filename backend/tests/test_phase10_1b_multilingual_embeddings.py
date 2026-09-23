import pytest
import os
import sys
import unicodedata

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.rag.embeddings import get_embeddings
from app.rag.database import get_vector_store
from app.services.ocr_service import detect_tamil_unicode, decode_legacy_tamil_font

def test_multilingual_embedding_provider_initialization():
    emb = get_embeddings()
    assert emb is not None
    test_text = "தீர்க்கதரிசி நூலை எழுதியவர் கலீல் ஜிப்ரான்."
    vec = emb.embed_query(test_text)
    assert isinstance(vec, list)
    assert len(vec) == 384
    assert any(v != 0.0 for v in vec)

def test_cross_lingual_semantic_similarity():
    emb = get_embeddings()
    import numpy as np
    
    vec_ta = np.array(emb.embed_query("தீர்க்கதரிசி நூலை எழுதியவர் கலீல் ஜிப்ரான்."))
    vec_en = np.array(emb.embed_query("The Prophet was written by Khalil Gibran."))
    vec_unrelated = np.array(emb.embed_query("Quantum gravity and astrophysics."))
    
    # Cosine similarity
    cos_sim_cross = np.dot(vec_ta, vec_en) / (np.linalg.norm(vec_ta) * np.linalg.norm(vec_en))
    cos_sim_unrelated = np.dot(vec_ta, vec_unrelated) / (np.linalg.norm(vec_ta) * np.linalg.norm(vec_unrelated))
    
    assert cos_sim_cross > cos_sim_unrelated
    assert cos_sim_cross > 0.20

def test_canonical_source_representation_preservation():
    raw_snippet = "பற்றிக் க]வு காண்கி`து. க]வுகடைள நம்புங்கள். ஏவெ]னில், அவற்றிஜேல தான் ஜேமாட்bத்தின் வாயில் அடைமந்திருக்கி`து."
    decoded = decode_legacy_tamil_font(raw_snippet)
    
    # Must be valid Tamil Unicode and not corrupted
    assert "கனவு" in decoded
    assert "காண்கிறது" in decoded
    assert "கனவுகளை" in decoded
    assert "ஏனெனில்" in decoded
    assert "அவற்றிலே" in decoded
    assert "மோட்சத்தின்" in decoded
    assert "அமைந்திருக்கிறது" in decoded
    assert "]" not in decoded
    assert "`" not in decoded
    assert "b" not in decoded
