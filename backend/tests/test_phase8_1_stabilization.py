import os
import sys
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

# Ensure backend directory is in sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.services.evidence_grading_service import get_evidence_grading_service, EvidenceChunk
from app.services.agent_search_service import get_agent_search_service

def test_health_endpoint():
    print("\n[TEST] Health Endpoint Check...")
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200, f"Health check failed with {response.status_code}"
        data = response.json()
        print(f"Health check response: {data}")
        assert data["status"] in ["ok", "degraded"]
        assert "cache" in data
        assert "in-memory" in data["cache"]
        print("[PASS] Health endpoint passed.")

def test_evidence_grading_deterministic():
    print("\n[TEST] Evidence Grading Service (Deterministic Fallback)...")
    service = get_evidence_grading_service()
    
    # 1. Strong Evidence Case
    query = "Who is the lead actor in Thalapathi and when was it released?"
    strong_chunks = [
        EvidenceChunk(
            content="Thalapathi is a 1991 Indian Tamil-language gangster drama film directed by Mani Ratnam starring Rajinikanth as the lead actor.",
            source_name="Thalapathi - Wikipedia",
            score=0.15
        ),
        EvidenceChunk(
            content="The film Thalapathi was released on 5 November 1991 during Diwali, featuring Rajinikanth in the main role.",
            source_name="Thalapathi Release Info",
            score=0.20
        )
    ]
    assessment_strong = service.grade_evidence(query, strong_chunks)
    print(f"Strong assessment: grade={assessment_strong.grade}, confidence={assessment_strong.confidence_score}, rationale={assessment_strong.rationale}")
    assert assessment_strong.grade in ["strong", "moderate"], f"Expected strong/moderate, got {assessment_strong.grade}"
    assert assessment_strong.confidence_score > 0.4
    
    # 2. Insufficient Evidence Case
    empty_assessment = service.grade_evidence(query, [])
    print(f"Empty assessment: grade={empty_assessment.grade}, confidence={empty_assessment.confidence_score}")
    assert empty_assessment.grade == "insufficient"
    assert empty_assessment.confidence_score == 0.0

    # 3. Limited/Weak Evidence Case
    weak_chunks = [
        EvidenceChunk(
            content="A totally unrelated article about quantum physics and thermodynamics.",
            source_name="Physics Journal",
            score=1.85
        )
    ]
    assessment_weak = service.grade_evidence(query, weak_chunks)
    print(f"Weak assessment: grade={assessment_weak.grade}, confidence={assessment_weak.confidence_score}")
    assert assessment_weak.grade in ["limited", "insufficient"]
    print("[PASS] Evidence grading passed.")

def test_agent_search_service_startup():
    print("\n[TEST] AgentSearchService Startup & Execution without Gemini...")
    service = get_agent_search_service()
    assert service is not None
    
    # Create or fetch a test persona
    from app.db.session import SessionLocal
    from app.db.models import Persona
    db = SessionLocal()
    persona = db.query(Persona).first()
    if not persona:
        persona = Persona(name="Test Persona Phase 8.1")
        db.add(persona)
        db.commit()
        db.refresh(persona)
    persona_id = persona.id
    db.close()

    res = service.search(persona_id=persona_id, query="actor biography", limit=3)
    print(f"Search result status: {res.status}, chunks retrieved: {len(res.retrieved_chunks)}, grade: {res.evidence_assessment.grade}")
    assert res.persona_id == persona_id
    assert res.evidence_assessment is not None
    assert res.evidence_assessment.grade in ["strong", "moderate", "limited", "insufficient"]
    print("[PASS] AgentSearchService test passed.")

def test_api_endpoints():
    print("\n[TEST] API Endpoints (/search and /evidence/grade)...")
    with TestClient(app) as client:
        # Test /evidence/grade endpoint
        res = client.post("/evidence/grade", json={
            "query": "Rajinikanth debut film",
            "chunks": [
                {"content": "Rajinikanth made his debut in K. Balachander's 1975 film Apoorva Raagangal.", "source_name": "Biography"}
            ]
        })
        assert res.status_code == 200, f"/evidence/grade failed: {res.text}"
        grade_data = res.json()
        assert "grade" in grade_data
        assert grade_data["grade"] in ["strong", "moderate", "limited", "insufficient"]
        print(f"/evidence/grade result: {grade_data['grade']} (provider: {grade_data.get('provider')})")

        # Test /search endpoint
        from app.db.session import SessionLocal
        from app.db.models import Persona
        db = SessionLocal()
        persona = db.query(Persona).first()
        persona_id = persona.id if persona else "non_existent"
        db.close()

        search_res = client.post("/search", json={
            "persona_id": persona_id,
            "query": "test query",
            "limit": 3
        })
        assert search_res.status_code == 200, f"/search failed: {search_res.text}"
        s_data = search_res.json()
        assert "query" in s_data
        assert "evidence_assessment" in s_data
        print(f"/search API result: status={s_data['status']}")
        print("[PASS] API endpoints passed.")

if __name__ == "__main__":
    test_health_endpoint()
    test_evidence_grading_deterministic()
    test_agent_search_service_startup()
    test_api_endpoints()
    print("\n==========================================")
    print("ALL PHASE 8.1 STABILIZATION TESTS PASSED!")
    print("==========================================")
