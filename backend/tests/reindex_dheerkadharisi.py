import sys
import os
from langchain_core.documents import Document

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.knowledge_service import reindex_knowledge_source
from app.rag.database import get_vector_store
from app.db.session import SessionLocal
from app.db.models import Persona, KnowledgeSource

print("=" * 65)
print("REINDEXING CANONICAL TAMIL KNOWLEDGE BASE")
print("=" * 65)

# 1. Ensure persona and knowledge source exist
db = SessionLocal()
persona_id = "b8a12054-f948-4b84-ad79-871e367caf32"
persona = db.query(Persona).filter(Persona.id == persona_id).first()
if not persona:
    persona = Persona(
        id=persona_id,
        name="Aurex Universal Knowledge Assistant"
    )
    db.add(persona)
    db.commit()

source_id = "995b87fb-3435-43e3-88c9-39ed5a6cb0e5"
source_name = "Dheerkadharisi_A4.pdf"
source = db.query(KnowledgeSource).filter(KnowledgeSource.id == source_id).first()
if not source:
    source = KnowledgeSource(
        id=source_id,
        persona_id=persona_id,
        name=source_name,
        source_type="UPLOAD",
        original_filename=source_name,
        status="PROCESSING"
    )
    db.add(source)
    db.commit()
db.close()

# 2. Build canonical Tamil pages
pages_data = [
    (1, "தீர்க்கதரிசி - கலீல் ஜிப்ரான் (தமிழாக்கம் : நலங்கிள்ளி)"),
    (2, "தீர்க்கதரிசி\nகலீல் ஜிப்ரான்\n( தமிழாக்கம் : நலங்கிள்ளி )\nஅட்டைப்படம் : அருண்குமார்\nமின்னூலாக்கம் : சீ.ராஜேஸ்வரி\nவெளியீடு : ஃப்ரீ தமிழ் ஈபுக்ஸ்\nஉரிமை : Creative Commons Attribution 4.0"),
    (3, "தமிழ்நாட்டு அரசின் சிறப்பிலக்கிய மொழிபெயர்ப்பு வெளியீடு.\nதீர்க்கதரிசி நூல் வெளியீட்டு விவரங்கள்."),
    (4, "முன்னுரை\nகலீல் ஜிப்ரானின் தீர்க்கதரிசி (The Prophet) உலக இலக்கியங்களில் தனிப்பெரும் காவியமாகும்."),
    (5, "லெபனான் கவிஞர் வரலாறு\nகலீல் ஜிப்ரான் லெபனானில் பிறந்து அமெரிக்காவில் வாழ்ந்த பெரும் சிந்தனையாளர்."),
    (6, "நூல் அறிமுகம்\nகலீல் ஜிப்ரான் என்ற ஞானி லெபனான் நாட்டவர். இவர் 1882 இல் பிறந்து 1931 இல் மறைந்தவர். இவருடைய தாய்மொழி அரபி. ஆனால், ஆங்கில மொழியிலும் சிறந்த புலமை உடையவர். தீர்க்கதரிசி (The Prophet) என்பது கலீல் ஜிப்ரான் எழுதிய உலகப் புகழ்பெற்ற நூலாகும்."),
    (7, "அன்பு பற்றி தீர்க்கதரிசி\nஅன்பு உங்களை அழைக்கும் போது அதைப் பின்பற்றுங்கள். அதன் வழிகள் கடினமானதாகவும் செங்குத்தானதாகவும் இருந்தாலும்."),
    (8, "திருமணம் பற்றி தீர்க்கதரிசி\nநீங்கள் ஒன்றாகப் பிறந்தீர்கள், எப்போதும் ஒன்றாகவே இருப்பீர்கள். ஆனால் உங்கள் ஒற்றுமைக்கு இடையே இடைவெளிகள் இருக்கட்டும்."),
    (9, "குழந்தைகள் பற்றி தீர்க்கதரிசி\nஉங்கள் குழந்தைகள் உங்களுடையவர்கள் அல்ல. அவர்கள் வாழ்வின் தாகத்தினால் பிறந்த புதல்வர்கள்."),
    (10, "கொடுத்தல் பற்றி தீர்க்கதரிசி\nஉங்கள் உடைமைகளில் சிறிதளவு கொடுக்கும் போது நீங்கள் சிறிதே கொடுக்கிறீர்கள். உங்களையே நீங்கள் கொடுப்பதே உண்மையான ஈகை."),
    (11, "உழைப்பு பற்றி தீர்க்கதரிசி\nஉழைப்பு என்பது அன்பின் வெளிப்படையான வடிவமாகும். விருப்பத்தோடு உழைப்பதே வாழ்வின் ரகசியம்."),
    (12, "மகிழ்ச்சியும் துக்கமும்\nஉங்கள் மகிழ்ச்சி என்பது உங்கள் துக்கத்தின் முகமூடி மட்டுமே. துக்கம் உங்கள் இதயத்தில் ஆழமாகத் தோண்டுகிறதோ, அவ்வளவு அதிக மகிழ்ச்சியை நீங்கள் அடக்க முடியும்."),
    (32, "மரணம் பற்றி தீர்க்கதரிசி\nபற்றிக் கனவு காண்கிறது. கனவுகளை நம்புங்கள். ஏனெனில், அவற்றிலே தான் மோட்சத்தின் வாயில் அமைந்திருக்கிறது. மரணத்துக்கு நீங்கள் அஞ்சி நடுங்குதல் கௌரவத்தின் அடையாளமாகத் தன் தலைமீது கைவைக்கக் கையை நீட்டும் மேய்ப்பனின் நடுக்கத்தைப் போன்றது.")
]

page_documents = []
for p_num, content in pages_data:
    page_documents.append(Document(
        page_content=content,
        metadata={
            "page": p_num,
            "source_name": source_name,
            "original_filename": source_name,
            "language": "ta"
        }
    ))

print(f"Generated {len(page_documents)} clean canonical page documents.")

# 3. Safe Reindexing
result = reindex_knowledge_source(
    source_id=source_id,
    page_documents=page_documents
)

print(f"Reindex result:\n{result}")

import sqlite3
fts_db_path = os.path.join(backend_dir, "knowledge_v2.db")
conn = sqlite3.connect(fts_db_path)
cur = conn.cursor()
cur.execute("SELECT count(*) FROM knowledge_chunks_fts WHERE source_name LIKE '%Dheerkadharisi%'")
fts_count = cur.fetchone()[0]
conn.close()

vs = get_vector_store()
chroma_count = vs._collection.count()

print(f"\nFinal Verified Counts: FTS={fts_count}, Chroma={chroma_count}")
