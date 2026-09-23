import sys
import os
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.db.session import SessionLocal
from app.db.models import KnowledgeSource
from app.services.agent_search_service import get_agent_search_service
from app.services.grounded_answer_service import get_grounded_answer_service

db = SessionLocal()
sources = db.query(KnowledgeSource).filter(KnowledgeSource.name.like("%Dheerkadharisi%")).all()
print(f"Found {len(sources)} sources for Dheerkadharisi:")
for s in sources:
    print(f"  ID: {s.id} | Name: {s.name} | Persona: {s.persona_id} | Status: {s.status} | Chunks: {s.chunk_count}")

if sources:
    persona_id = sources[0].persona_id
    search_service = get_agent_search_service()
    query = "தீர்க்கதரிசி நூலை எழுதியவர் யார்?"
    print(f"\n[SEARCH] Running query '{query}' for persona '{persona_id}'...", flush=True)
    res = search_service.search(persona_id=persona_id, query=query, limit=5)
    print(f"Status: {res.status}")
    print(f"Retrieved {len(res.retrieved_chunks)} chunks:")
    for idx, c in enumerate(res.retrieved_chunks):
        p_num = c.metadata.get("page", "?")
        print(f"  [{idx+1}] (p.{p_num}) {c.source_name}: {c.content[:100]}... (score: {c.score})")

    answer_service = get_grounded_answer_service()
    answer_res = answer_service.generate_grounded_answer_sync("Tamil Scholar", query, res)
    print(f"\n[GENERATED ANSWER]\n{answer_res.answer}")
    print(f"Citations: {[c.dict() for c in answer_res.citations]}")

db.close()
