import pytest
import os
import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.agent_search_service import get_agent_search_service
from app.services.grounded_answer_service import get_grounded_answer_service

PERSONA_ID = "b8a12054-f948-4b84-ad79-871e367caf32"

def test_tamil_factual_retrieval():
    search_service = get_agent_search_service()
    query = "தீர்க்கதரிசி நூலை எழுதியவர் யார்?"
    res = search_service.search(persona_id=PERSONA_ID, query=query)
    
    assert res.status == "ready_for_answer"
    assert len(res.retrieved_chunks) > 0
    # Top chunk should mention Kahlil Gibran
    top_contents = " ".join([c.content for c in res.retrieved_chunks[:3]])
    assert "கலீல் ஜிப்ரான்" in top_contents or "கலீல்" in top_contents

def test_false_candidate_prevention():
    search_service = get_agent_search_service()
    answer_service = get_grounded_answer_service()
    query = "தீர்க்கதரிசி நூலை பாரதியார் எழுதியாரா?"
    
    res = search_service.search(persona_id=PERSONA_ID, query=query)
    ans = answer_service.generate_grounded_answer_sync("Aurex", query, res)
    
    # Must NOT say "ஆம்" (Yes) that Bharathiyar wrote it
    assert "ஆம்" not in ans.answer or "இல்லை" in ans.answer
    assert "பாரதியார்" not in ans.answer or "இல்லை" in ans.answer or "கலீல் ஜிப்ரான்" in ans.answer
