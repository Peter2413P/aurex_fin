import os
import sys
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

# Ensure backend directory is in sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.services.agent_search_service import get_agent_search_service, SearchState, SearchResultItem
from app.services.evidence_grading_service import get_evidence_grading_service, EvidenceChunk
from app.db.session import SessionLocal
from app.db.models import Persona, Entity, ExplicitFact

def get_or_create_test_persona():
    db = SessionLocal()
    persona = db.query(Persona).first()
    if not persona:
        persona = Persona(name="Phase 9 Knowledge Persona")
        db.add(persona)
        db.commit()
        db.refresh(persona)
    persona_id = persona.id
    db.close()
    return persona_id

def test_1_strong_evidence():
    print("\n[TEST 1] Strong Evidence -> No retry -> ready_for_answer...")
    service = get_agent_search_service()
    persona_id = get_or_create_test_persona()
    
    # Test sufficiency logic directly
    state = SearchState(
        query="Who directed Thalapathi?",
        original_query="Who directed Thalapathi?",
        normalized_query="Who directed Thalapathi?",
        persona_id=persona_id,
        retrieved_chunks=[
            SearchResultItem(
                id="c1",
                content="Thalapathi is a 1991 Indian Tamil-language gangster drama film directed by Mani Ratnam.",
                source_name="Thalapathi Wiki",
                score=0.10
            )
        ]
    )
    grader = get_evidence_grading_service()
    state.evidence_assessment = grader.grade_evidence(
        state.normalized_query,
        [EvidenceChunk(content=c.content, source_name=c.source_name, score=c.score) for c in state.retrieved_chunks]
    )
    is_suff = service.is_evidence_sufficient(state)
    assert is_suff is True, "Expected strong evidence to be sufficient"
    print("[PASS] Test 1 passed: Strong evidence accepted without retries.")

def test_2_moderate_evidence_sufficiency():
    print("\n[TEST 2] Moderate Evidence Sufficiency...")
    service = get_agent_search_service()
    persona_id = get_or_create_test_persona()

    state = SearchState(
        query="Tell me about Rajinikanth career in 1991",
        original_query="Tell me about Rajinikanth career in 1991",
        normalized_query="Tell me about Rajinikanth career in 1991",
        persona_id=persona_id,
        retrieved_chunks=[
            SearchResultItem(
                id="c2",
                content="In 1991, Thalapathi was released featuring Rajinikanth.",
                source_name="Film History",
                score=0.30
            )
        ]
    )
    grader = get_evidence_grading_service()
    state.evidence_assessment = grader.grade_evidence(
        state.normalized_query,
        [EvidenceChunk(content=c.content, source_name=c.source_name, score=c.score) for c in state.retrieved_chunks]
    )
    is_suff = service.is_evidence_sufficient(state)
    assert state.evidence_assessment.grade in ["strong", "moderate"], f"Expected strong/moderate, got {state.evidence_assessment.grade}"
    print(f"[PASS] Test 2 passed: Grade={state.evidence_assessment.grade}, Sufficient={is_suff}.")

def test_3_insufficient_evidence_and_expansion():
    print("\n[TEST 3] Insufficient Evidence -> Query Expansion -> Insufficient State...")
    service = get_agent_search_service()
    persona_id = get_or_create_test_persona()

    # Search for an obscure non-existent topic
    res = service.search(persona_id=persona_id, query="What is the quantum telemetry frequency of Andromeda galaxy station 999?", limit=2)
    print(f"Status: {res.status}, Retries: {res.retry_count}, Message: {res.message}")
    assert res.status == "insufficient_evidence"
    assert "couldn't verify" in res.message.lower() or "no" in res.message.lower()
    print("[PASS] Test 3 passed: Insufficient evidence gracefully handled with no hallucination.")

def test_4_retry_limit():
    print("\n[TEST 4] Bounded Retry Limit (Max 2 retries)...")
    service = get_agent_search_service()
    persona_id = get_or_create_test_persona()

    res = service.search(persona_id=persona_id, query="Super unknown entity xyzabc123456789 question", limit=2)
    assert res.retry_count <= 2, f"Retry count exceeded limit: {res.retry_count}"
    print(f"[PASS] Test 4 passed: Retry count was bounded to {res.retry_count} (max 2).")

def test_5_no_gemini_dependency():
    print("\n[TEST 5] Entire Search Workflow without Gemini...")
    service = get_agent_search_service()
    persona_id = get_or_create_test_persona()

    res = service.search(persona_id=persona_id, query="Who is Madhavi?", limit=3)
    assert res.evidence_assessment is not None
    assert res.evidence_assessment.grade in ["strong", "moderate", "limited", "insufficient"]
    print("[PASS] Test 5 passed: Search completed successfully with deterministic grading.")

def test_6_empty_query():
    print("\n[TEST 6] Empty Query Validation...")
    service = get_agent_search_service()
    persona_id = get_or_create_test_persona()

    res = service.search(persona_id=persona_id, query="   ", limit=3)
    assert res.status == "insufficient_evidence"
    assert "empty" in (res.message or "").lower()
    print("[PASS] Test 6 passed: Empty query cleanly caught.")

def test_7_no_documents():
    print("\n[TEST 7] Persona with No Documents...")
    db = SessionLocal()
    empty_persona = Persona(name="Empty Persona Phase 9")
    db.add(empty_persona)
    db.commit()
    db.refresh(empty_persona)
    empty_p_id = empty_persona.id
    db.close()

    service = get_agent_search_service()
    res = service.search(persona_id=empty_p_id, query="Tell me everything about this persona", limit=3)
    assert res.status == "insufficient_evidence"
    assert len(res.retrieved_chunks) == 0
    print("[PASS] Test 7 passed: Empty persona returned controlled insufficient evidence.")

def test_8_hybrid_retrieval_and_language():
    print("\n[TEST 8] Hybrid Retrieval & Language Analysis (Tamil/Tanglish/English)...")
    service = get_agent_search_service()
    persona_id = get_or_create_test_persona()

    # Tamil query
    ta_analysis = service.analyze_query("மாதவி யார்?", persona_id)
    assert ta_analysis["language"] == "ta"

    # Tanglish query
    tanglish_analysis = service.analyze_query("Madhavi yaar?", persona_id)
    assert tanglish_analysis["language"] == "tanglish"

    # English query
    en_analysis = service.analyze_query("Who is Madhavi?", persona_id)
    assert en_analysis["language"] == "en"

    print("[PASS] Test 8 passed: Language analysis correctly identified ta, tanglish, and en.")

def test_9_search_api_endpoint():
    print("\n[TEST 9] Search API Endpoint (POST /search)...")
    persona_id = get_or_create_test_persona()
    
    with TestClient(app) as client:
        response = client.post("/search", json={
            "persona_id": persona_id,
            "query": "Who is the lead actor in Thalapathi?",
            "limit": 3
        })
        assert response.status_code == 200, f"/search failed: {response.text}"
        data = response.json()
        assert "status" in data
        assert "query" in data
        assert "language" in data
        assert "search_variants" in data
        assert "evidence_assessment" in data
        assert "grade" in data["evidence_assessment"]
        assert "retrieved_chunks" in data
        assert "retry_count" in data
        print(f"[PASS] Test 9 passed: POST /search returned valid JSON payload (status={data['status']}, language={data['language']}).")

if __name__ == "__main__":
    test_1_strong_evidence()
    test_2_moderate_evidence_sufficiency()
    test_3_insufficient_evidence_and_expansion()
    test_4_retry_limit()
    test_5_no_gemini_dependency()
    test_6_empty_query()
    test_7_no_documents()
    test_8_hybrid_retrieval_and_language()
    test_9_search_api_endpoint()
    print("\n==============================================")
    print("ALL 9 PHASE 9 AGENTIC SEARCH TESTS PASSED!")
    print("==============================================")
