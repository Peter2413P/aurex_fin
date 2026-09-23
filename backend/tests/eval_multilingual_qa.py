import sys
import os
import io

# Set UTF-8 output encoding for Windows terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.agent_search_service import get_agent_search_service
from app.services.grounded_answer_service import get_grounded_answer_service

search_service = get_agent_search_service()
answer_service = get_grounded_answer_service()

persona_id = "b8a12054-f948-4b84-ad79-871e367caf32"

test_queries = [
    ("Tamil Direct", "தீர்க்கதரிசி நூலை எழுதியவர் யார்?"),
    ("English Cross-Lingual", "Who wrote The Prophet?"),
    ("Tanglish 1", "Theerkkadharisi noolai yaar ezhuthinathu?"),
    ("Tanglish 2", "theerkkadharisi book author yaar?"),
    ("Mixed Language", "தீர்க்கதரிசி book-ஐ யார் write பண்ணினது?"),
    ("False Candidate", "தீர்க்கதரிசி நூலை பாரதியார் எழுதியாரா?"),
    ("Unsupported Query", "What is the secret recipe for quantum cosmic pancakes?")
]

print("=" * 70)
print("MULTILINGUAL RETRIEVAL & GROUNDED ANSWER EVALUATION")
print("=" * 70)

for label, query in test_queries:
    print(f"\n--- [{label}] Query: '{query}' ---")
    search_res = search_service.search(persona_id=persona_id, query=query, limit=5)
    print(f"Status: {search_res.status} | Lang: {search_res.language} | Intent: {search_res.intent}")
    print(f"Search Variants: {search_res.search_variants}")
    print(f"Retrieved Chunks: {len(search_res.retrieved_chunks)}")
    
    if search_res.retrieved_chunks:
        top_chunk = search_res.retrieved_chunks[0]
        page_val = top_chunk.metadata.get("page", 1)
        print(f"Top Chunk (Page {page_val}, Method: {top_chunk.retrieval_method}):")
        print(f"  Snippet: {top_chunk.content[:160]}...")
    
    print(f"Evidence Grade: {search_res.evidence_assessment.grade} (Conf: {search_res.evidence_assessment.confidence_score})")
    
    ans_res = answer_service.generate_grounded_answer_sync(
        persona_name="Aurex",
        query=query,
        search_res=search_res
    )
    print(f"Generated Grounded Answer:")
    print(f"  {ans_res.answer}")
    if ans_res.citations:
        for c in ans_res.citations[:2]:
            print(f"  Citation {c.id}: Page {c.page} from '{c.source_name}'")

print("\n" + "=" * 70)
print("EVALUATION COMPLETED")
print("=" * 70)
