import re
from typing import Optional, Dict

SILAPPATHIKARAM_QA = [
    {
        "id": 1,
        "keywords": ["iyatriyavar", "eyatriyavar", "author", "writer", "இயற்றியவர்", "எழுதியவர்", "இளங்கோவடிகள்", "ilango"],
        "question_ta": "சிலப்பதிகாரத்தை இயற்றியவர் யார்?",
        "answer_ta": "சிலப்பதிகாரத்தை இயற்றியவர் இளங்கோவடிகள் ஆவார். இவர் சேர மன்னர் குடும்பத்தைச் சேர்ந்தவர் எனக் கூறப்படுகிறார். சிலப்பதிகாரம் தமிழின் ஐம்பெரும் காப்பியங்களில் ஒன்றாகும். கண்ணகி, கோவலன் ஆகியோரின் வாழ்க்கையையும், அவர்களின் வழியாக அறம் மற்றும் நீதியின் முக்கியத்துவத்தையும் இந்நூல் எடுத்துரைக்கிறது.",
        "question_tanglish": "Silappathikaarathai iyatriyavar yaar?",
        "answer_tanglish": "Silappathikaarathai iyatriyavar Ilango Adigal aavaar. Ivar Chera mannar kudumbathai sernthavar ena koorappadugiradhu. Silappathikaaram Tamilin Aimperum Kaappiyangalil onraagaum. Kannagi matrum Kovalanin vaazhkaiyin moolamaaga aram matrum neethiyin mukkiyathuvathai indha nool eduthuraikkiradhu."
    },
    {
        "id": 2,
        "keywords": ["kadhanaayagi", "kathanayagi", "heroine", "கதாநாயகி", "தலைவி"],
        "question_ta": "சிலப்பதிகாரத்தின் கதாநாயகி யார்?",
        "answer_ta": "சிலப்பதிகாரத்தின் கதாநாயகி கண்ணகி ஆவார். கண்ணகி கற்பு, துணிவு மற்றும் நீதியின் அடையாளமாகக் காட்டப்படுகிறார். தனது கணவன் கோவலன் அநியாயமாகக் கொல்லப்பட்டதை அறிந்ததும், உண்மையை நிரூபிக்க மதுரை அரசனிடம் சென்று நீதி கேட்கிறாள். இதனால் கண்ணகியின் பாத்திரம் தமிழ்க் காப்பிய வரலாற்றில் மிகவும் முக்கியமானதாக விளங்குகிறது.",
        "question_tanglish": "Silappathikaarathin kadhanaayagi yaar?",
        "answer_tanglish": "Silappathikaarathin kadhanaayagi Kannagi aavaar. Kannagi karpu, thunivu matrum neethiyin adaiyaalamaaga kaattappadugiraal. Than kanavan Kovalan aniyaayamaaga kollappattadhai arindha piragu, unmaiyai nirupikka Madurai arasanidam sendru neethi ketkiraal. Idhanaal Kannagiyin paaththiram Tamil kaappiya varalatril migavum mukkiyamaanadhaaga vilangugiradhu."
    },
    {
        "id": 3,
        "keywords": ["kannagiyin kanavar", "kanavar", "husband", "கண்ணகியின் கணவர்", "கணவர் யார்", "கணவர்"],
        "question_ta": "கண்ணகியின் கணவர் யார்?",
        "answer_ta": "கண்ணகியின் கணவர் கோவலன் ஆவார். கோவலன் செல்வந்த வணிகக் குடும்பத்தைச் சேர்ந்தவர். மாதவியுடன் ஏற்பட்ட தொடர்பின் காரணமாக தனது செல்வத்தை இழந்த பின்னர் மீண்டும் கண்ணகியிடம் திரும்புகிறார். பின்னர் இருவரும் மதுரைக்குச் சென்று புதிய வாழ்க்கையைத் தொடங்க முயற்சிக்கின்றனர்.",
        "question_tanglish": "Kannagiyin kanavar yaar?",
        "answer_tanglish": "Kannagiyin kanavar Kovalan aavaar. Kovalan selvandha vaniga kudumbathai sernthavar. Maadhaviyudan erpatta thodarbin kaaranamaaga thanadhu selvathai izhandha piragu meendum Kannagiyidam thirumbugiraar. Pinnar iruvarum Maduraikku sendru pudhiya vaazhkaiyai thodanga muyarchi seygiraargal."
    },
    {
        "id": 4,
        "keywords": ["sendra nagaram", "nagaram", "city", "சென்ற நகரம்", "எந்த நகரம்", "நகரம் எது", "நகரம்"],
        "question_ta": "சிலப்பதிகாரத்தில் கோவலன் சென்ற நகரம் எது?",
        "answer_ta": "கோவலன் கண்ணகியுடன் மதுரை நகரத்திற்குச் செல்கிறார். அங்கு கண்ணகியின் சிலம்பை விற்று வாழ்க்கையைத் தொடங்க முயற்சிக்கிறார். ஆனால் அந்தச் சிலம்பு அரசியின் சிலம்பு என தவறாகக் கருதப்பட்டதால் கோவலன் குற்றவாளியாகக் கருதப்படுகிறார். இதன் விளைவாக அவர் அநியாயமாகத் தண்டிக்கப்படுகிறார்.",
        "question_tanglish": "Silappathikaarathil Kovalan sendra nagaram edhu?",
        "answer_tanglish": "Kovalan Kannagiyudan Madurai nagarathirkku selgiraar. Angu Kannagiyin silambai vitru pudhiya vaazhkaiyai thodanga muyarchikkiraar. Aanaal andha silambu arasiyaarudaiya silambu ena thavaraaga karuthappattadhaal Kovalan kutravaaliyaaga karuthappadugiraar. Idhan vilaivaaga avar aniyaayamaaga thandikkappadugiraar."
    },
    {
        "id": 5,
        "keywords": ["silambil irundhadhu", "silambil enna", "anklet", "சிலம்பில் இருந்தது", "மாணிக்கம்", "மாணிக்கக் கற்கள்"],
        "question_ta": "கண்ணகியின் சிலம்பில் இருந்தது என்ன?",
        "answer_ta": "கண்ணகியின் சிலம்பில் மாணிக்கக் கற்கள் இருந்தன. கோவலன் கண்ணகியின் சிலம்பை விற்க முயன்றபோது, அது அரசியின் சிலம்புடன் தொடர்புடையதாக தவறாகக் கருதப்பட்டது. பின்னர் கண்ணகி தனது சிலம்பை உடைத்து அதில் மாணிக்கங்கள் இருப்பதை நிரூபிக்கிறாள். இதன் மூலம் கோவலன் குற்றமற்றவன் என்பதை வெளிப்படுத்துகிறாள்.",
        "question_tanglish": "Kannagiyin silambil irundhadhu enna?",
        "answer_tanglish": "Kannagiyin silambil maanikkak kargal irundhana. Kovalan Kannagiyin silambai virka muyandrapodhu, adhu arasiyaarudaiya silambudan thodarbudaiyadhaaga thavaraaga karuthappattadhu. Pinnar Kannagi thanadhu silambai udaiththu adhil maanikkangal iruppadhai nirubikkiraal. Idhan moolam Kovalan kutramatravan enbadhai velippaduthugiraal."
    },
    {
        "id": 6,
        "keywords": ["nadanak kalaignar", "kalaignar", "dancer", "மாதவி", "நடனக் கலைஞர்", "நடன கலைஞர்"],
        "question_ta": "கோவலனுடன் தொடர்புடைய நடனக் கலைஞர் யார்?",
        "answer_ta": "கோவலனுடன் தொடர்புடைய நடனக் கலைஞர் மாதவி ஆவார். மாதவி புகார் நகரத்தில் புகழ்பெற்ற நடனக் கலைஞராக விளங்கினாள். கோவலன் அவளுடன் வாழ்ந்த காலத்தில் தனது செல்வத்தை இழந்தான். பின்னர் கோவலன் மாதவியை விட்டு கண்ணகியிடம் திரும்புகிறான்.",
        "question_tanglish": "Kovalanudan thodarbudaiya nadanak kalaignar yaar?",
        "answer_tanglish": "Kovalanudan thodarbudaiya nadanak kalaignar Maadhavi aavaal. Maadhavi Puhar nagarathil pugazhpetra nadanak kalaignaraaga vilanginaal. Kovalan avaludan vaazhntha kaalathil thanadhu selvathai izhandhaan. Pinnar Kovalan Maadhaviyai vittu Kannagiyidam thirumbugiraar."
    },
    {
        "id": 7,
        "keywords": ["mudhal kaandam", "first chapter", "முதல் காண்டம்", "புகார்க்காண்டம்", "முதல்"],
        "question_ta": "சிலப்பதிகாரத்தின் முதல் காண்டம் எது?",
        "answer_ta": "சிலப்பதிகாரத்தின் முதல் காண்டம் புகார்க்காண்டம் ஆகும். இது புகார் நகரத்தை மையமாகக் கொண்ட நிகழ்வுகளை எடுத்துரைக்கிறது. கோவலன், கண்ணகி மற்றும் மாதவி ஆகியோரின் வாழ்க்கையில் நடைபெறும் முக்கிய நிகழ்வுகள் இப்பகுதியில் இடம்பெறுகின்றன. கோவலன் மற்றும் கண்ணகியின் வாழ்க்கையில் ஏற்படும் மாற்றங்களுக்கும் இது அடித்தளமாக அமைகிறது.",
        "question_tanglish": "Silappathikaarathin mudhal kaandam edhu?",
        "answer_tanglish": "Silappathikaarathin mudhal kaandam Puharkkaandam aagum. Idhu Puhar nagarai maiyamaaga konda nigazhvugalai eduthuraikkiradhu. Kovalan, Kannagi matrum Maadhaviyin vaazhkaiyil nadakkum mukkiya nigazhvugal ippagudiyil idamperugindrana. Kovalan matrum Kannagiyin vaazhkaiyil erpadum maatrangalukkum idhu adithalamaaga amaigiradhu."
    },
    {
        "id": 8,
        "keywords": ["irandaavadhu kaandam", "second chapter", "இரண்டாவது காண்டம்", "மதுரைக்காண்டம்", "இரண்டாவது"],
        "question_ta": "சிலப்பதிகாரத்தின் இரண்டாவது காண்டம் எது?",
        "answer_ta": "சிலப்பதிகாரத்தின் இரண்டாவது காண்டம் மதுரைக்காண்டம் ஆகும். இதில் கோவலனும் கண்ணகியும் மதுரைக்குச் செல்லும் நிகழ்வுகள் முக்கியமாக இடம்பெறுகின்றன. கோவலன் அநியாயமாகக் கொல்லப்படுவதும், கண்ணகி மதுரை அரசனிடம் நீதி கேட்பதும் இக்காண்டத்தின் முக்கிய நிகழ்வுகளாகும். கண்ணகியின் நீதிப் போராட்டம் இப்பகுதியில் உச்சத்தை அடைகிறது.",
        "question_tanglish": "Silappathikaarathin irandaavadhu kaandam edhu?",
        "answer_tanglish": "Silappathikaarathin irandaavadhu kaandam Maduraikkaandam aagum. Idhil Kovalanum Kannagiyum Maduraikku sellum nigazhvugal mukkiyamaaga idamperugindrana. Kovalan aniyaayamaaga kollappaduvadhum, Kannagi Madurai arasanidam neethi ketpadhum ikkaandathin mukkiya nigazhvugalaaga amaigindrana. Kannagiyin neethikkaana poraattam ippagudiyil uchchathai adaigiradhu."
    },
    {
        "id": 9,
        "keywords": ["moondraavadhu kaandam", "third chapter", "மூன்றாவது காண்டம்", "வஞ்சிக்காண்டம்", "மூன்றாவது"],
        "question_ta": "சிலப்பதிகாரத்தின் மூன்றாவது காண்டம் எது?",
        "answer_ta": "சிலப்பதிகாரத்தின் மூன்றாவது காண்டம் வஞ்சிக்காண்டம் ஆகும். இது சேர நாட்டையும் சேர மன்னன் செங்குட்டுவனையும் மையமாகக் கொண்டுள்ளது. கண்ணகியின் சிறப்பும் பத்தினி வழிபாட்டின் முக்கியத்துவமும் இக்காண்டத்தில் எடுத்துரைக்கப்படுகின்றன. இதன் மூலம் சிலப்பதிகாரத்தின் கதை நிறைவுப் பகுதிக்குச் செல்கிறது.",
        "question_tanglish": "Silappathikaarathin moondraavadhu kaandam edhu?",
        "answer_tanglish": "Silappathikaarathin moondraavadhu kaandam Vanjikkaandam aagum. Idhu Chera naattaiyum Chera mannan Senguttuvanaiyum maiyamaaga kondulladhu. Kannagiyin sirappum Paththini vazhipaattin mukkiyathuvamum ikkaandathil eduthuraikkappadugindrana. Idhan moolam Silappathikaarathin kathai niraivup pagudhikku selgiradhu."
    },
    {
        "id": 10,
        "keywords": ["sirappikkappadugiraal", "sirappu", "how praise", "சிறப்பிக்கப்படுகிறார்", "சிறப்பு", "பத்தினி"],
        "question_ta": "சிலப்பதிகாரத்தில் கண்ணகி எவ்வாறு சிறப்பிக்கப்படுகிறார்?",
        "answer_ta": "சிலப்பதிகாரத்தில் கண்ணகி கற்பு, துணிவு மற்றும் நீதியின் அடையாளமாகச் சிறப்பிக்கப்படுகிறார். தனது கணவன் அநியாயமாகக் கொல்லப்பட்டதை அறிந்தவுடன், உண்மையை நிரூபிக்க அரசனிடம் நேரடியாகச் சென்று நீதி கேட்கிறாள். தனது சிலம்பின் மூலம் கோவலன் குற்றமற்றவன் என்பதை நிரூபிக்கிறாள். இதனால் கண்ணகி தமிழர் பண்பாட்டில் முக்கியமான பெண் பாத்திரமாகவும் பத்தினித் தெய்வமாகவும் போற்றப்படுகிறார்.",
        "question_tanglish": "Silappathikaarathil Kannagi evvaaru sirappikkappadugiraal?",
        "answer_tanglish": "Silappathikaarathil Kannagi karpu, thunivu matrum neethiyin adaiyaalamaaga sirappikkappadugiraal. Than kanavan aniyaayamaaga kollappattadhai arindhavudan, unmaiyai nirupikka arasanidam neradiyaaga sendru neethi ketkiraal. Thanadhu silambin moolam Kovalan kutramatravan enbadhai nirupikkiraal. Idhanaal Kannagi Tamilargalin panpaatil mukkiyamaana pen paaththiramaagavum Paththini theyvamaagavum potrappadugiraal."
    }
]

def is_tamil_unicode(text: str) -> bool:
    return bool(re.search(r'[\u0B80-\u0BFF]', text))

def _tokenize(text: str) -> set:
    clean = re.sub(r'[^\w\s]', '', text.lower())
    return set(clean.split())

def get_default_answer(query: str) -> Optional[str]:
    """
    Matches query against built-in hardcoded knowledge base using token overlap and keyword scoring.
    Returns paragraph answer in Tamil or Tanglish depending on input format.
    """
    clean_query = query.lower().strip()
    is_tamil = is_tamil_unicode(query)
    q_tokens = _tokenize(query)
    
    if not q_tokens:
        return None
        
    best_item = None
    best_score = 0
    
    for item in SILAPPATHIKARAM_QA:
        score = 0
        if is_tamil:
            target_text = item["question_ta"]
            t_tokens = _tokenize(target_text)
            overlap = len(q_tokens.intersection(t_tokens))
            score = overlap * 2.0
            
            for kw in item["keywords"]:
                if kw in clean_query:
                    score += 3.0
        else:
            target_text = item["question_tanglish"]
            t_tokens = _tokenize(target_text)
            overlap = len(q_tokens.intersection(t_tokens))
            score = overlap * 2.0
            
            for kw in item["keywords"]:
                if kw.lower() in clean_query:
                    score += 3.0
                    
        if score > best_score:
            best_score = score
            best_item = item
            
    if best_item and best_score >= 2.0:
        return best_item["answer_ta"] if is_tamil else best_item["answer_tanglish"]
        
    return None
