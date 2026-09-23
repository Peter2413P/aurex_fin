import sys
sys.stdout.reconfigure(encoding='utf-8')
print("[START] Loading dependencies for real Tamil pipeline test...", flush=True)

import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import pymupdf
from app.db.session import SessionLocal
from app.db.models import Persona, KnowledgeSource
from app.services.document_service import ingest_document
from app.services.agent_search_service import get_agent_search_service
from app.services.grounded_answer_service import get_grounded_answer_service

def test_real_tamil_document_pipeline():
    print("=" * 60, flush=True)
    print("REAL TAMIL DOCUMENT INGESTION & GROUNDED SEARCH PIPELINE", flush=True)
    print("=" * 60, flush=True)
    
    # 1. Ensure test persona exists in DB
    db = SessionLocal()
    persona = db.query(Persona).filter(Persona.id == "persona_tamil_eval").first()
    if not persona:
        persona = Persona(
            id="persona_tamil_eval",
            name="Tamil Literary Scholar",
            tagline="Expert on Sangam and Epic literature",
            system_prompt="You are a knowledgeable scholar on classical Tamil literature.",
            greeting="வணக்கம்! சிலப்பதிகாரம் மற்றும் தமிழ் இலக்கியம் பற்றி கேளுங்கள்."
        )
        db.add(persona)
        db.commit()
    db.close()
    
    # 2. Generate a real 3-page Tamil PDF (Silappathikaram)
    pdf_path = os.path.join(backend_dir, "Silappathikaram_Madhavi.pdf")
    doc = pymupdf.open()
    
    # Page 1: Introduction to Madhavi
    p1 = doc.new_page()
    if os.path.exists("C:/Windows/Fonts/Nirmala.ttc"):
        p1.insert_font(fontname="tam_font", fontfile="C:/Windows/Fonts/Nirmala.ttc")
        p1.insert_text((50, 72), "சிலப்பதிகாரம் - காவிய நாயகி மாதவி\nமாதவி ஒரு புகழ்பெற்ற சோழ நாட்டு நடனக் கலைஞர். அவள் பூம்புகாரில் வாழ்ந்தாள்.", fontname="tam_font", fontsize=12)
    else:
        p1.insert_text((50, 72), "சிலப்பதிகாரம் - காவிய நாயகி மாதவி\nமாதவி ஒரு புகழ்பெற்ற சோழ நாட்டு நடனக் கலைஞர். அவள் பூம்புகாரில் வாழ்ந்தாள்.", fontsize=12)
        
    # Page 2: Relationship with Kovalan
    p2 = doc.new_page()
    if os.path.exists("C:/Windows/Fonts/Nirmala.ttc"):
        p2.insert_font(fontname="tam_font", fontfile="C:/Windows/Fonts/Nirmala.ttc")
        p2.insert_text((50, 72), "கோவலன் மற்றும் மாதவி உறவு\nகோவலன் மாதவியின் கலைத்திறனைக் கண்டு வியந்து அவளுடன் பல ஆண்டுகள் வாழ்ந்தார்.", fontname="tam_font", fontsize=12)
    else:
        p2.insert_text((50, 72), "கோவலன் மற்றும் மாதவி உறவு\nகோவலன் மாதவியின் கலைத்திறனைக் கண்டு வியந்து அவளுடன் பல ஆண்டுகள் வாழ்ந்தார்.", fontsize=12)
        
    # Page 3: Daughter Manimekalai
    p3 = doc.new_page()
    if os.path.exists("C:/Windows/Fonts/Nirmala.ttc"):
        p3.insert_font(fontname="tam_font", fontfile="C:/Windows/Fonts/Nirmala.ttc")
        p3.insert_text((50, 72), "மணிமேகலை\nமாதவி மற்றும் கோவலனின் மகள் மணிமேகலை ஆவார். அவர் பௌத்த துறவியாக மாறினார்.", fontname="tam_font", fontsize=12)
    else:
        p3.insert_text((50, 72), "மணிமேகலை\nமாதவி மற்றும் கோவலனின் மகள் மணிமேகலை ஆவார். அவர் பௌத்த துறவியாக மாறினார்.", fontsize=12)
        
    doc.save(pdf_path)
    doc.close()
    print(f"[STEP 1] Created real 3-page Tamil PDF: {pdf_path}", flush=True)
    
    # 3. Ingest document through full unified pipeline
    print("[STEP 2] Ingesting document into SQLite + ChromaDB + FTS5 with page provenance...", flush=True)
    source_id = ingest_document(pdf_path, "Silappathikaram_Madhavi.pdf", "persona_tamil_eval")
    print(f"  -> Ingestion completed! Source ID: {source_id}", flush=True)
    
    db = SessionLocal()
    ks = db.query(KnowledgeSource).filter(KnowledgeSource.id == source_id).first()
    assert ks is not None
    assert ks.status == "COMPLETED"
    print(f"  -> Knowledge Source status: {ks.status}, chunk_count: {ks.chunk_count}", flush=True)
    db.close()
    
    # 4. Search Pipeline with Tamil Query
    print("\n[STEP 3] Running Hybrid Agentic Search for Tamil Query: 'மாதவி யார்?'...", flush=True)
    search_service = get_agent_search_service()
    search_res = search_service.search(
        persona_id="persona_tamil_eval",
        query="மாதவி யார்?"
    )
    print(f"  -> Search status: {search_res.status}, retrieved {len(search_res.retrieved_chunks)} chunks", flush=True)
    assert len(search_res.retrieved_chunks) > 0
    top_chunk = search_res.retrieved_chunks[0]
    print(f"  -> Top Chunk Content: {top_chunk.content[:100]}...", flush=True)
    print(f"  -> Top Chunk Metadata: {top_chunk.metadata}", flush=True)
    assert "மாதவி" in top_chunk.content
    assert "page" in top_chunk.metadata
    
    # 5. Search Pipeline with English Query
    print("\n[STEP 4] Running Hybrid Agentic Search for English Query: 'Who is Madhavi?'...", flush=True)
    search_res_en = search_service.search(
        persona_id="persona_tamil_eval",
        query="Who is Madhavi?"
    )
    print(f"  -> English Query retrieved {len(search_res_en.retrieved_chunks)} chunks", flush=True)
    assert len(search_res_en.retrieved_chunks) > 0
    print(f"  -> Top Chunk (Cross-Lingual): {search_res_en.retrieved_chunks[0].content[:100]}...", flush=True)
    
    # 6. Search Pipeline with Tanglish Query
    print("\n[STEP 5] Running Hybrid Agentic Search for Tanglish Query: 'Madhavi yaar?'...", flush=True)
    search_res_tang = search_service.search(
        persona_id="persona_tamil_eval",
        query="Madhavi yaar?"
    )
    print(f"  -> Tanglish Query retrieved {len(search_res_tang.retrieved_chunks)} chunks", flush=True)
    assert len(search_res_tang.retrieved_chunks) > 0
    
    # 7. Grounded Answer & Citation Resolution
    print("\n[STEP 6] Generating Grounded Answer & Citations...", flush=True)
    answer_service = get_grounded_answer_service()
    citations = answer_service.build_citations(search_res)
    assert len(citations) > 0
    print(f"  -> Resolved Citations: {len(citations)}", flush=True)
    for c in citations:
        print(f"     Citation [{c.index}] -> Document: '{c.source_name}', Page: {c.page}, Snippet: {c.snippet[:60]}...", flush=True)
        assert c.source_name == "Silappathikaram_Madhavi.pdf"
        assert c.page in [1, 2, 3]
        
    answer_resp = answer_service.generate_grounded_answer_sync(
        persona_name="Tamil Literary Scholar",
        query="மாதவி யார்?",
        search_res=search_res
    )
    print(f"  -> Generated Grounded Answer: {answer_resp.answer[:150]}...", flush=True)
    print(f"  -> Answer Citations count: {len(answer_resp.citations)}", flush=True)
    
    print("\n" + "=" * 60, flush=True)
    print("[ALL REAL DOCUMENT PIPELINE CHECKS PASSED 100%!]", flush=True)
    print("=" * 60, flush=True)
    
    # Clean up test PDF
    if os.path.exists(pdf_path):
        try:
            os.remove(pdf_path)
        except Exception:
            pass

if __name__ == "__main__":
    test_real_tamil_document_pipeline()
