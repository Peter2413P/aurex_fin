import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import pymupdf
from langchain_core.documents import Document
from app.services.ocr_service import (
    get_ocr_engine,
    detect_tamil_unicode,
    normalize_unicode_text,
    validate_text_quality,
    OCRResult
)
from app.services.agent_search_service import AgentSearchResponse, SearchResultItem
from app.services.grounded_answer_service import get_grounded_answer_service
from app.rag.fts_database import index_chunk_fts, search_fts

def run_multilingual_ocr_tests():
    print("=" * 60)
    print("PHASE 10.1 MULTILINGUAL OCR & RETRIEVAL TEST SUITE")
    print("=" * 60)
    
    test_results = {}
    
    # ----------------------------------------------------
    # TEST 1: English Document Extraction Still Works
    # ----------------------------------------------------
    print("\n[TEST 1] Testing English Document Extraction...")
    eng_pdf_path = os.path.join(backend_dir, "test_eng_doc.pdf")
    doc_eng = pymupdf.open()
    p1 = doc_eng.new_page()
    p1.insert_text((50, 72), "PersonaForge AI supports advanced agentic knowledge discovery and multilingual document retrieval.", fontsize=12)
    doc_eng.save(eng_pdf_path)
    doc_eng.close()
    
    engine = get_ocr_engine()
    results_eng = engine.process_pdf(eng_pdf_path)
    assert len(results_eng) == 1
    assert results_eng[0].status == "NOT_REQUIRED"
    assert "PersonaForge AI" in results_eng[0].text
    assert results_eng[0].language == "en"
    print(f"  -> Extracted English Page 1: {results_eng[0].text[:60]}...")
    test_results["Test 1: English extraction"] = "PASS"
    
    # ----------------------------------------------------
    # TEST 2: Tamil OCR Provider Initializes Successfully
    # ----------------------------------------------------
    print("\n[TEST 2] Testing Tamil OCR Provider Initialization...")
    assert engine is not None
    assert engine.native_provider is not None
    print(f"  -> OCR Engine ready with providers: Native={engine.native_provider.name}, Raster={engine.raster_provider_name}")
    test_results["Test 2: Tamil OCR provider initialization"] = "PASS"
    
    # ----------------------------------------------------
    # TEST 3: Tamil Unicode Detection
    # ----------------------------------------------------
    print("\n[TEST 3] Testing Tamil Unicode Detection...")
    tamil_sample = "மாதவி ஒரு புகழ்பெற்ற நடனக் கலைஞர். அவர் கோவலனுடன் தொடர்புடையவர்."
    det_tamil = detect_tamil_unicode(tamil_sample)
    print(f"  -> Text: {tamil_sample}")
    print(f"  -> Detection: has_tamil={det_tamil['has_tamil']}, chars={det_tamil['tamil_chars']}, ratio={det_tamil['tamil_ratio']}, lang={det_tamil['language']}")
    assert det_tamil["has_tamil"] == True
    assert det_tamil["tamil_chars"] > 10
    assert det_tamil["language"] == "ta"
    
    # Negative test: Non-Tamil text
    det_eng = detect_tamil_unicode("This is purely English text.")
    assert det_eng["has_tamil"] == False
    assert det_eng["language"] == "en"
    test_results["Test 3: Tamil Unicode detection"] = "PASS"
    
    # ----------------------------------------------------
    # TEST 4: Tamil PDF Output Stored with Page Provenance
    # ----------------------------------------------------
    print("\n[TEST 4] Testing Tamil PDF Extraction with Page Provenance...")
    tamil_pdf_path = os.path.join(backend_dir, "test_tamil_doc.pdf")
    doc_tam = pymupdf.open()
    
    # Page 1: Tamil text (using Nirmala font on Windows)
    p1 = doc_tam.new_page()
    if os.path.exists("C:/Windows/Fonts/Nirmala.ttc"):
        p1.insert_font(fontname="tam_font", fontfile="C:/Windows/Fonts/Nirmala.ttc")
        p1.insert_text((50, 72), "சிலப்பதிகாரம்: மாதவி ஒரு புகழ்பெற்ற நடனக் கலைஞர்.", fontname="tam_font", fontsize=12)
    else:
        p1.insert_text((50, 72), "சிலப்பதிகாரம்: மாதவி ஒரு புகழ்பெற்ற நடனக் கலைஞர்.", fontsize=12)
        
    # Page 2: Tamil text continuation
    p2 = doc_tam.new_page()
    if os.path.exists("C:/Windows/Fonts/Nirmala.ttc"):
        p2.insert_font(fontname="tam_font", fontfile="C:/Windows/Fonts/Nirmala.ttc")
        p2.insert_text((50, 72), "அவர் கோவலனுடன் பூம்புகாரில் வாழ்ந்தார்.", fontname="tam_font", fontsize=12)
    else:
        p2.insert_text((50, 72), "அவர் கோவலனுடன் பூம்புகாரில் வாழ்ந்தார்.", fontsize=12)
        
    doc_tam.save(tamil_pdf_path)
    doc_tam.close()
    
    results_tam = engine.process_pdf(tamil_pdf_path)
    assert len(results_tam) == 2
    assert results_tam[0].page_number == 1
    assert results_tam[1].page_number == 2
    assert results_tam[0].tamil_detected == True
    print(f"  -> Page 1 (Provenance verified): page={results_tam[0].page_number}, lang={results_tam[0].language}, text={results_tam[0].text}")
    print(f"  -> Page 2 (Provenance verified): page={results_tam[1].page_number}, lang={results_tam[1].language}, text={results_tam[1].text}")
    test_results["Test 4: Tamil page provenance"] = "PASS"
    
    # ----------------------------------------------------
    # TEST 5: Tamil Chunks Indexed in FTS5
    # ----------------------------------------------------
    print("\n[TEST 5] Testing Tamil Chunk Indexing in FTS5...")
    test_persona_id = "test_persona_multilingual"
    test_source_id = "test_src_silappathikaram"
    
    chunk_1_content = "மாதவி ஒரு புகழ்பெற்ற நாட்டியக் கலைஞர். சிலப்பதிகாரத்தில் கோவலன் அவளை விரும்பினார்."
    index_chunk_fts(
        chunk_id=f"{test_source_id}_0",
        persona_id=test_persona_id,
        source_id=test_source_id,
        source_name="Silappathikaram.pdf",
        content=chunk_1_content
    )
    
    fts_res = search_fts(persona_id=test_persona_id, query="மாதவி", limit=5)
    print(f"  -> FTS5 query 'மாதவி' matched: {len(fts_res)} chunks")
    assert len(fts_res) > 0
    assert "மாதவி" in fts_res[0]["content"]
    test_results["Test 5: Tamil chunks FTS5 indexed"] = "PASS"
    
    # ----------------------------------------------------
    # TEST 6: Tamil Semantic Retrieval
    # ----------------------------------------------------
    print("\n[TEST 6] Testing Tamil Semantic Retrieval (Same Language)...")
    import numpy as np
    from app.rag.embeddings import get_embeddings_model
    
    emb_model = get_embeddings_model()
    doc_embedding = emb_model.embed_query(chunk_1_content)
    
    query_ta = "மாதவி யார்?"
    q_ta_emb = emb_model.embed_query(query_ta)
    sim_ta = np.dot(doc_embedding, q_ta_emb)
    print(f"  -> Query (Tamil): '{query_ta}' -> Cosine Similarity: {sim_ta:.4f}")
    assert sim_ta > 0.40, f"Expected cosine similarity > 0.40, got {sim_ta}"
    test_results["Test 6: Tamil semantic retrieval"] = "PASS"
    
    # ----------------------------------------------------
    # TEST 7: English Query Retrieves Tamil Evidence (Cross-Lingual)
    # ----------------------------------------------------
    print("\n[TEST 7] Testing Cross-Lingual Semantic Retrieval (English Query -> Tamil Document)...")
    query_en = "Who is Madhavi?"
    q_en_emb = emb_model.embed_query(query_en)
    sim_en = np.dot(doc_embedding, q_en_emb)
    print(f"  -> Query (English): '{query_en}' -> Cosine Similarity: {sim_en:.4f}")
    assert sim_en > 0.25, f"Expected cross-lingual similarity > 0.25, got {sim_en}"
    test_results["Test 7: Cross-lingual English query"] = "PASS"
    
    # ----------------------------------------------------
    # TEST 8: Tanglish Query Retrieves Tamil Evidence
    # ----------------------------------------------------
    print("\n[TEST 8] Testing Tanglish Query Retrieval...")
    query_tanglish = "Madhavi yaar?"
    q_tang_emb = emb_model.embed_query(query_tanglish)
    sim_tang = np.dot(doc_embedding, q_tang_emb)
    print(f"  -> Query (Tanglish): '{query_tanglish}' -> Cosine Similarity: {sim_tang:.4f}")
    assert sim_tang > 0.30, f"Expected Tanglish similarity > 0.30, got {sim_tang}"
    test_results["Test 8: Tanglish query retrieval"] = "PASS"
    
    # ----------------------------------------------------
    # TEST 9: Tamil Grounded Answer & Citation Resolution
    # ----------------------------------------------------
    print("\n[TEST 9] Testing Tamil Grounded Answer and Citations...")
    from app.services.grounded_answer_service import get_grounded_answer_service
    from app.services.evidence_grading_service import EvidenceAssessment
    answer_service = get_grounded_answer_service()
    
    tamil_search_res = AgentSearchResponse(
        status="ready_for_answer",
        query="மாதவி யார்?",
        original_query="மாதவி யார்?",
        normalized_query="மாதவி யார்?",
        persona_id=test_persona_id,
        language="ta",
        intent="factual_lookup",
        entities=["மாதவி"],
        search_variants=["மாதவி"],
        search_methods=["semantic", "lexical"],
        retrieved_chunks=[
            SearchResultItem(
                id=f"{test_source_id}_0",
                content="சிலப்பதிகாரத்தில் மாதவி ஒரு புகழ்பெற்ற நடனக் கலைஞர். அவர் பூம்புகாரில் வாழ்ந்தார்.",
                source_name="Silappathikaram.pdf",
                source_type="UPLOAD",
                source_url="",
                score=0.10,
                metadata={"page": 1, "knowledge_source_id": test_source_id, "chunk_index": 0}
            )
        ],
        retrieval_metadata={"search_attempts": 1, "is_sufficient": True},
        evidence_assessment=EvidenceAssessment(
            grade="strong",
            confidence_score=0.95,
            rationale="Direct match on Madhavi in Silappathikaram",
            signals={"semantic_score": 0.95},
            provider="deterministic",
            supporting_chunk_indices=[0]
        ),
        retry_count=0
    )
    
    citations = answer_service.build_citations(tamil_search_res)
    print(f"  -> Built Citations: {len(citations)}")
    assert len(citations) == 1
    assert citations[0].index == 1
    assert citations[0].source_name == "Silappathikaram.pdf"
    assert citations[0].page == 1
    print(f"  -> Citation [1] Page Provenance: Document={citations[0].source_name}, Page={citations[0].page}")
    
    prompt = answer_service.build_grounded_prompt(
        persona_name="Tamil Scholar",
        query="மாதவி யார்?",
        citations=citations,
        search_res=tamil_search_res,
        history=[]
    )
    assert "Silappathikaram.pdf" in prompt
    assert "Page: 1" in prompt
    assert "மாதவி ஒரு புகழ்பெற்ற நடனக் கலைஞர்" in prompt
    test_results["Test 9: Grounded answer & citations"] = "PASS"
    
    # ----------------------------------------------------
    # TEST 10: Mixed Query Support (Tamil + English)
    # ----------------------------------------------------
    print("\n[TEST 10] Testing Mixed Query (Tamil + English)...")
    query_mixed = "மாதவி யார்? Tell me about her role in Silappathikaram."
    q_mixed_emb = emb_model.embed_query(query_mixed)
    sim_mixed = np.dot(doc_embedding, q_mixed_emb)
    print(f"  -> Query (Mixed): '{query_mixed}' -> Cosine Similarity: {sim_mixed:.4f}")
    assert sim_mixed > 0.30
    test_results["Test 10: Mixed Tamil-English query"] = "PASS"
    
    # ----------------------------------------------------
    # TEST 11: OCR Failure Safety (No Fake Evidence)
    # ----------------------------------------------------
    print("\n[TEST 11] Testing OCR Failure Safety & Garbage Rejection...")
    empty_doc = pymupdf.open()
    empty_doc.new_page() # blank page
    empty_pdf_path = os.path.join(backend_dir, "test_empty_doc.pdf")
    empty_doc.save(empty_pdf_path)
    empty_doc.close()
    
    empty_results = engine.process_pdf(empty_pdf_path)
    assert len(empty_results) == 1
    assert empty_results[0].status in ["FAILED", "PENDING"]
    assert empty_results[0].text == ""
    print(f"  -> Blank page correctly reported status: {empty_results[0].status} with no hallucinated text.")
    test_results["Test 11: OCR failure safety"] = "PASS"
    
    # ----------------------------------------------------
    # TEST 12: Unicode Quality Filter
    # ----------------------------------------------------
    print("\n[TEST 12] Testing Unicode Quality Filter on Garbage/Noise...")
    assert validate_text_quality("?????? ?????") == False
    assert validate_text_quality("\ufffd\ufffd\ufffd\ufffd\ufffd") == False
    assert validate_text_quality("····· ·····") == False
    assert validate_text_quality("மாதவி ஒரு புகழ்பெற்ற நடனக் கலைஞர்") == True
    print("  -> Noise and replacement characters rejected; clean Tamil accepted.")
    test_results["Test 12: Unicode quality validation"] = "PASS"
    
    # Clean up test files
    for f in [eng_pdf_path, tamil_pdf_path, empty_pdf_path]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass
                
    print("\n" + "=" * 60)
    print("TEST SUITE RESULTS:")
    print("=" * 60)
    for test_name, status in test_results.items():
        print(f"{test_name:.<50} {status}")
    print("=" * 60)
    
    all_passed = all(status == "PASS" for status in test_results.values())
    assert all_passed, "Some tests failed!"
    print("\n[ALL TESTS PASSED SUCCESSFULLY!]")

if __name__ == "__main__":
    run_multilingual_ocr_tests()
