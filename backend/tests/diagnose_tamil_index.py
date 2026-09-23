import sys
import os
import sqlite3
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

print("=" * 65, flush=True)
print("DIAGNOSTIC: INSPECTING EXISTING INDEX & DATABASE FOR CORRUPTION", flush=True)
print("=" * 65, flush=True)

# 1. Inspect knowledge_v2.db (FTS5 and chunks)
fts_db_path = os.path.join(backend_dir, "knowledge_v2.db")
if os.path.exists(fts_db_path):
    conn = sqlite3.connect(fts_db_path)
    cur = conn.cursor()
    try:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [r[0] for r in cur.fetchall()]
        print(f"\n[FTS DB] Tables in knowledge_v2.db: {tables}", flush=True)
        
        if "knowledge_chunks_fts" in tables:
            cur.execute("SELECT count(*) FROM knowledge_chunks_fts")
            total_fts = cur.fetchone()[0]
            print(f"  -> Total FTS chunks: {total_fts}", flush=True)
            
            # Check for corrupted tokens in FTS5
            cur.execute("SELECT chunk_id, source_name, content FROM knowledge_chunks_fts")
            corrupt_fts = []
            for cid, sname, content in cur.fetchall():
                if any(x in content for x in [']', '\\`', '`து', 'ஜேமாட்b', 'க]வு', 'டைK', 'டைக']):
                    corrupt_fts.append((cid, sname, content[:80]))
            print(f"  -> Corrupted FTS chunks found: {len(corrupt_fts)}", flush=True)
            for c in corrupt_fts[:5]:
                print(f"     ID: {c[0]} | Source: {c[1]} | Content: {c[2]}...", flush=True)
    except Exception as e:
        print(f"[FTS DB ERROR] {e}", flush=True)
    finally:
        conn.close()

# 2. Inspect persona_forge.db (KnowledgeSources, Personas, etc.)
pf_db_path = os.path.join(backend_dir, "persona_forge.db")
if os.path.exists(pf_db_path):
    conn = sqlite3.connect(pf_db_path)
    cur = conn.cursor()
    try:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [r[0] for r in cur.fetchall()]
        print(f"\n[MAIN DB] Tables in persona_forge.db: {tables}", flush=True)
        if "knowledge_sources" in tables:
            cur.execute("SELECT id, name, source_type, status, chunk_count FROM knowledge_sources")
            sources = cur.fetchall()
            print(f"  -> Total Knowledge Sources: {len(sources)}", flush=True)
            for s in sources:
                print(f"     Source ID: {s[0]} | Name: {s[1]} | Type: {s[2]} | Status: {s[3]} | Chunks: {s[4]}", flush=True)
    except Exception as e:
        print(f"[MAIN DB ERROR] {e}", flush=True)
    finally:
        conn.close()

# 3. Inspect ChromaDB Collections
print("\n[CHROMADB] Inspecting Chroma Collections...", flush=True)
try:
    from app.rag.database import get_vector_store
    vs = get_vector_store()
    count = vs._collection.count()
    print(f"  -> Current collection: '{vs._collection.name}', Total Vectors: {count}", flush=True)
    if count > 0:
        sample = vs._collection.get(limit=min(count, 10))
        docs = sample.get("documents", [])
        metas = sample.get("metadatas", [])
        print(f"  -> Sample Vectors ({len(docs)} items):", flush=True)
        for d, m in zip(docs, metas):
            s_name = m.get("source_name", "Unknown") if m else "Unknown"
            page_num = m.get("page", 1) if m else 1
            print(f"     Source: '{s_name}' (p.{page_num}): {d[:80]}...", flush=True)
except Exception as e:
    print(f"  -> Chroma inspection warning: {e}", flush=True)

print("\n" + "=" * 65, flush=True)
print("DIAGNOSTIC COMPLETED", flush=True)
print("=" * 65, flush=True)
