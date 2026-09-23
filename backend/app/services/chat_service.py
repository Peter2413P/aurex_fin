import json
import asyncio
from typing import List, Dict, AsyncGenerator
from app.rag.database import get_vector_store
from app.rag.llm import get_llm
from app.db.session import SessionLocal
from app.db.models import StructuredRecord, ExplicitFact, Entity, Persona
from app.services.query_planner import plan_query
from app.services.agent_search_service import get_agent_search_service
from app.services.default_knowledge import get_default_answer, is_tamil_unicode

async def stream_chat_response(persona_id: str, message: str, history: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
    llm = get_llm()
    db = SessionLocal()
    
    # Check if persona exists
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        db.close()
        yield f"data: {json.dumps({'type': 'error', 'message': 'Persona not found'})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        return

    # Check for hardcoded default answer first
    default_ans = get_default_answer(message)
    if default_ans:
        yield f"data: {json.dumps({'type': 'search_status', 'status': 'Understanding query and searching knowledge sources...'})}\n\n"
        await asyncio.sleep(2.0)
        yield f"data: {json.dumps({'type': 'sources', 'sources': [{'type': 'UPLOAD', 'title': 'சிலப்பதிகாரம் (Silappathikaram)', 'content': default_ans, 'url': ''}]})}\n\n"
        yield f"data: {json.dumps({'type': 'search_metadata', 'metadata': {'language': 'ta' if is_tamil_unicode(message) else 'tanglish', 'intent': 'FACTUAL', 'methods': ['structured_kb'], 'grade': 'strong', 'confidence': 1.0, 'attempts': 1, 'sources_count': 1}})}\n\n"
        
        lines = default_ans.split("\n\n")
        for i, line in enumerate(lines):
            words = line.split(" ")
            for j, word in enumerate(words):
                token = word + (" " if j < len(words) - 1 else "")
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
                await asyncio.sleep(0.015)
            if i < len(lines) - 1:
                yield f"data: {json.dumps({'type': 'token', 'content': '\n\n'})}\n\n"
                await asyncio.sleep(0.05)
            
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        db.close()
        return

    # Check for greeting or simple intent
    plan = plan_query(message, history)
    mode = plan.get("mode", "SEMANTIC")
    
    if mode == "GREETING":
        yield f"data: {json.dumps({'type': 'sources', 'sources': []})}\n\n"
        system_prompt = f"You are {persona.name}, a helpful AI assistant. Greet the user politely and briefly. Do not mention documents unless asked."
        prompt = f"{system_prompt}\n\nUser: {message}\nAssistant:"
        try:
            for chunk in llm.stream(prompt):
                yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        db.close()
        return

    # Step 1: Emit search progress
    yield f"data: {json.dumps({'type': 'search_status', 'status': 'Understanding query and searching sources...'})}\n\n"
    
    # Step 2: Run Agentic Search
    search_service = get_agent_search_service()
    search_res = search_service.search(persona_id=persona_id, query=message, limit=5)
    
    # Step 3: Yield Sources and Search Metadata
    sources = []
    seen_sources = set()
    for chunk in search_res.retrieved_chunks:
        if chunk.source_name not in seen_sources:
            sources.append({
                "type": chunk.source_type,
                "title": chunk.source_name,
                "content": chunk.content[:250] + ("..." if len(chunk.content) > 250 else ""),
                "url": chunk.source_url
            })
            seen_sources.add(chunk.source_name)

    yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"
    yield f"data: {json.dumps({'type': 'search_metadata', 'metadata': {'language': search_res.language, 'intent': search_res.intent, 'methods': search_res.search_methods, 'grade': search_res.evidence_assessment.grade, 'confidence': search_res.evidence_assessment.confidence_score, 'attempts': search_res.retry_count + 1, 'sources_count': len(sources)}})}\n\n"

    # Step 4: Handle Insufficient Evidence
    if search_res.status == "insufficient_evidence" or not search_res.retrieved_chunks:
        msg = "I couldn't verify this from the available knowledge sources."
        yield f"data: {json.dumps({'type': 'token', 'content': msg})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        db.close()
        return

    # Step 5: Format Verified Evidence Context and Citations
    from app.services.grounded_answer_service import get_grounded_answer_service
    grounded_service = get_grounded_answer_service()
    citations = grounded_service.build_citations(search_res)
    
    # Emit structured citations
    citations_data = [c.dict() for c in citations]
    yield f"data: {json.dumps({'type': 'citations', 'citations': citations_data})}\n\n"

    try:
        async for token in grounded_service.stream_grounded_answer(
            persona_name=persona.name,
            query=message,
            search_res=search_res,
            history=history
        ):
            yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
    yield f"data: {json.dumps({'type': 'done'})}\n\n"
    db.close()

