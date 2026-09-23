import pytest
import os
import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.agent_search_service import get_agent_search_service
from app.services.grounded_answer_service import get_grounded_answer_service

PERSONA_ID = "b8a12054-f948-4b84-ad79-871e367caf32"

def test_e2e_tamil_query_to_tamil_source():
    search_service = get_agent_search_service()
    answer_service = get_grounded_answer_service()
    
    query = "தீர்க்கதரிசி நூலை எழுதியவர் யார்?"
    search_res = search_service.search(persona_id=PERSONA_ID, query=query)
    
    assert search_res.status == "ready_for_answer"
    assert search_res.language == "ta"
    assert len(search_res.retrieved_chunks) > 0
    
    ans_res = answer_service.generate_grounded_answer_sync("Aurex", query, search_res)
    assert "கலீல் ஜிப்ரான்" in ans_res.answer or "Khalil Gibran" in ans_res.answer
    assert len(ans_res.citations) > 0

def test_e2e_english_query_to_tamil_source():
    search_service = get_agent_search_service()
    answer_service = get_grounded_answer_service()
    
    query = "Who wrote The Prophet?"
    search_res = search_service.search(persona_id=PERSONA_ID, query=query)
    
    assert search_res.status == "ready_for_answer"
    assert search_res.language == "en"
    
    ans_res = answer_service.generate_grounded_answer_sync("Aurex", query, search_res)
    assert "Khalil Gibran" in ans_res.answer or "கலீல் ஜிப்ரான்" in ans_res.answer
    assert len(ans_res.citations) > 0

def test_e2e_tanglish_query_to_tamil_source():
    search_service = get_agent_search_service()
    answer_service = get_grounded_answer_service()
    
    query = "Theerkkadharisi noolai yaar ezhuthinathu?"
    search_res = search_service.search(persona_id=PERSONA_ID, query=query)
    
    assert search_res.status == "ready_for_answer"
    assert search_res.language == "tanglish"
    
    ans_res = answer_service.generate_grounded_answer_sync("Aurex", query, search_res)
    assert "Khalil Gibran" in ans_res.answer or "கலீல் ஜிப்ரான்" in ans_res.answer

def test_e2e_mixed_query_to_tamil_source():
    search_service = get_agent_search_service()
    answer_service = get_grounded_answer_service()
    
    query = "தீர்க்கதரிசி book-ஐ யார் write பண்ணினது?"
    search_res = search_service.search(persona_id=PERSONA_ID, query=query)
    
    assert search_res.status == "ready_for_answer"
    assert search_res.language == "mixed"
    
    ans_res = answer_service.generate_grounded_answer_sync("Aurex", query, search_res)
    assert "கலீல் ஜிப்ரான்" in ans_res.answer or "Khalil Gibran" in ans_res.answer

def test_e2e_unsupported_query_refusal():
    search_service = get_agent_search_service()
    answer_service = get_grounded_answer_service()
    
    query = "What is the secret recipe for quantum cosmic pancakes?"
    search_res = search_service.search(persona_id=PERSONA_ID, query=query)
    
    ans_res = answer_service.generate_grounded_answer_sync("Aurex", query, search_res)
    assert "I couldn't verify this from the available knowledge sources." in ans_res.answer
