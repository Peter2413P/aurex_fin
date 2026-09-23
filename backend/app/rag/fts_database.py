import sqlite3
import os
from typing import List, Dict, Any
from app.db.session import DB_FILE

FTS_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "knowledge_v2.db")

def init_fts():
    conn = sqlite3.connect(FTS_DB_PATH)
    cursor = conn.cursor()
    try:
        # Check if table exists and has page column
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_chunks_fts'")
        if cursor.fetchone():
            try:
                cursor.execute("SELECT page FROM knowledge_chunks_fts LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute("DROP TABLE IF EXISTS knowledge_chunks_fts")
        
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_chunks_fts USING fts5(
                chunk_id,
                persona_id UNINDEXED,
                knowledge_source_id UNINDEXED,
                source_name,
                content,
                page UNINDEXED,
                tokenize='porter unicode61'
            );
        """)
        conn.commit()
    except Exception as e:
        print(f"[FTS5] Init warning: {e}")
    finally:
        conn.close()

# Initialize FTS tables on import
init_fts()

def index_chunk_fts(chunk_id: str, persona_id: str, source_id: str, source_name: str, content: str, page: int = 1):
    conn = sqlite3.connect(FTS_DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM knowledge_chunks_fts WHERE chunk_id = ?", (chunk_id,))
        cursor.execute("""
            INSERT INTO knowledge_chunks_fts(chunk_id, persona_id, knowledge_source_id, source_name, content, page)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (chunk_id, persona_id, source_id, source_name, content, str(page)))
        conn.commit()
    except Exception as e:
        print(f"[FTS5] Index error: {e}")
    finally:
        conn.close()

def delete_source_chunks_fts(source_id: str):
    conn = sqlite3.connect(FTS_DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM knowledge_chunks_fts WHERE knowledge_source_id = ?", (source_id,))
        conn.commit()
    except Exception as e:
        print(f"[FTS5] Delete source chunks error: {e}")
    finally:
        conn.close()

def search_fts(persona_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
    import re
    cleaned_terms = re.findall(r'\w+', query)
    if not cleaned_terms:
        return []
    fts_query = " OR ".join([f'"{t}"*' for t in cleaned_terms if len(t) > 1])
    if not fts_query:
        return []

    conn = sqlite3.connect(FTS_DB_PATH)
    cursor = conn.cursor()
    results = []
    try:
        cursor.execute("""
            SELECT chunk_id, persona_id, knowledge_source_id, source_name, content, page, rank
            FROM knowledge_chunks_fts
            WHERE persona_id = ? AND knowledge_chunks_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (persona_id, fts_query, limit))
        rows = cursor.fetchall()
        for r in rows:
            p_val = 1
            if len(r) > 5 and r[5] is not None:
                try:
                    p_val = int(r[5])
                except (ValueError, TypeError):
                    p_val = 1
            results.append({
                "chunk_id": r[0],
                "persona_id": r[1],
                "knowledge_source_id": r[2],
                "source_name": r[3],
                "content": r[4],
                "page": p_val,
                "rank": r[6] if len(r) > 6 else r[5]
            })
    except Exception as e:
        print(f"[FTS5] Search error: {e}")
    finally:
        conn.close()
    return results
