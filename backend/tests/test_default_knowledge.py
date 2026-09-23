import sys
import io
from app.services.default_knowledge import get_default_answer, SILAPPATHIKARAM_QA

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

queries = [
  ('Silappathikaarathil Kannagi evvaaru sirappikkappadugiraal?', 10),
  ('சிலப்பதிகாரத்தில் கண்ணகி எவ்வாறு சிறப்பிக்கப்படுகிறார்?', 10),
  ('Silappathikaarathai iyatriyavar yaar?', 1),
  ('சிலப்பதிகாரத்தை இயற்றியவர் யார்?', 1),
  ('Silappathikaarathin kadhanaayagi yaar?', 2),
  ('சிலப்பதிகாரத்தின் கதாநாயகி யார்?', 2),
  ('Kannagiyin kanavar yaar?', 3),
  ('கண்ணகியின் கணவர் யார்?', 3),
  ('Silappathikaarathil Kovalan sendra nagaram edhu?', 4),
  ('சிலப்பதிகாரத்தில் கோவலன் சென்ற நகரம் எது?', 4),
  ('Kannagiyin silambil irundhadhu enna?', 5),
  ('கண்ணகியின் சிலம்பில் இருந்தது என்ன?', 5),
  ('Kovalanudan thodarbudaiya nadanak kalaignar yaar?', 6),
  ('கோவலனுடன் தொடர்புடைய நடனக் கலைஞர் யார்?', 6),
  ('Silappathikaarathin mudhal kaandam edhu?', 7),
  ('சிலப்பதிகாரத்தின் முதல் காண்டம் எது?', 7),
  ('Silappathikaarathin irandaavadhu kaandam edhu?', 8),
  ('சிலப்பதிகாரத்தின் இரண்டாவது காண்டம் எது?', 8),
  ('Silappathikaarathin moondraavadhu kaandam edhu?', 9),
  ('சிலப்பதிகாரத்தின் மூன்றாவது காண்டம் எது?', 9)
]

for q, expected_id in queries:
    ans = get_default_answer(q)
    expected_ans = None
    for item in SILAPPATHIKARAM_QA:
        if item["id"] == expected_id:
            expected_ans = item["answer_ta"] if any('\u0B80' <= c <= '\u0BFF' for c in q) else item["answer_tanglish"]
    matched = (ans == expected_ans)
    print(f"Q: {q}")
    print(f"Match status: {matched}")
    if not matched:
        print(f"Got: {ans}")
        print(f"Expected: {expected_ans}")
    print("-" * 50)
