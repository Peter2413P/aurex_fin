export interface QuestionItem {
  id: number;
  question: string;
  answer: string;
  question_ta?: string;
  answer_ta?: string;
  question_tanglish?: string;
  answer_tanglish?: string;
}

export const tamilQuestions: QuestionItem[] = [
  {
    id: 1,
    question: "சிலப்பதிகாரத்தை இயற்றியவர் யார்?",
    answer: "சிலப்பதிகாரத்தை இயற்றியவர் இளங்கோவடிகள் ஆவார். இவர் சேர மன்னர் குடும்பத்தைச் சேர்ந்தவர் எனக் கூறப்படுகிறார். சிலப்பதிகாரம் தமிழின் ஐம்பெரும் காப்பியங்களில் ஒன்றாகும். கண்ணகி, கோவலன் ஆகியோரின் வாழ்க்கையையும், அவர்களின் வழியாக அறம் மற்றும் நீதியின் முக்கியத்துவத்தையும் இந்நூல் எடுத்துரைக்கிறது."
  },
  {
    id: 2,
    question: "சிலப்பதிகாரத்தின் கதாநாயகி யார்?",
    answer: "சிலப்பதிகாரத்தின் கதாநாயகி கண்ணகி ஆவார். கண்ணகி கற்பு, துணிவு மற்றும் நீதியின் அடையாளமாகக் காட்டப்படுகிறார். தனது கணவன் கோவலன் அநியாயமாகக் கொல்லப்பட்டதை அறிந்ததும், உண்மையை நிரூபிக்க மதுரை அரசனிடம் சென்று நீதி கேட்கிறாள். இதனால் கண்ணகியின் பாத்திரம் தமிழ்க் காப்பிய வரலாற்றில் மிகவும் முக்கியமானதாக விளங்குகிறது."
  },
  {
    id: 3,
    question: "கண்ணகியின் கணவர் யார்?",
    answer: "கண்ணகியின் கணவர் கோவலன் ஆவார். கோவலன் செல்வந்த வணிகக் குடும்பத்தைச் சேர்ந்தவர். மாதவியுடன் ஏற்பட்ட தொடர்பின் காரணமாக தனது செல்வத்தை இழந்த பின்னர் மீண்டும் கண்ணகியிடம் திரும்புகிறார். பின்னர் இருவரும் மதுரைக்குச் சென்று புதிய வாழ்க்கையைத் தொடங்க முயற்சிக்கின்றனர்."
  },
  {
    id: 4,
    question: "சிலப்பதிகாரத்தில் கோவலன் சென்ற நகரம் எது?",
    answer: "கோவலன் கண்ணகியுடன் மதுரை நகரத்திற்குச் செல்கிறார். அங்கு கண்ணகியின் சிலம்பை விற்று வாழ்க்கையைத் தொடங்க முயற்சிக்கிறார். ஆனால் அந்தச் சிலம்பு அரசியின் சிலம்பு என தவறாகக் கருதப்பட்டதால் கோவலன் குற்றவாளியாகக் கருதப்படுகிறார். இதன் விளைவாக அவர் அநியாயமாகத் தண்டிக்கப்படுகிறார்."
  },
  {
    id: 5,
    question: "கண்ணகியின் சிலம்பில் இருந்தது என்ன?",
    answer: "கண்ணகியின் சிலம்பில் மாணிக்கக் கற்கள் இருந்தன. கோவலன் கண்ணகியின் சிலம்பை விற்க முயன்றபோது, அது அரசியின் சிலம்புடன் தொடர்புடையதாக தவறாகக் கருதப்பட்டது. பின்னர் கண்ணகி தனது சிலம்பை உடைத்து அதில் மாணிக்கங்கள் இருப்பதை நிரூபிக்கிறாள். இதன் மூலம் கோவலன் குற்றமற்றவன் என்பதை வெளிப்படுத்துகிறாள்."
  },
  {
    id: 6,
    question: "கோவலனுடன் தொடர்புடைய நடனக் கலைஞர் யார்?",
    answer: "கோவலனுடன் தொடர்புடைய நடனக் கலைஞர் மாதவி ஆவார். மாதவி புகார் நகரத்தில் புகழ்பெற்ற நடனக் கலைஞராக விளங்கினாள். கோவலன் அவளுடன் வாழ்ந்த காலத்தில் தனது செல்வத்தை இழந்தான். பின்னர் கோவலன் மாதவியை விட்டு கண்ணகியிடம் திரும்புகிறான்."
  },
  {
    id: 7,
    question: "சிலப்பதிகாரத்தின் முதல் காண்டம் எது?",
    answer: "சிலப்பதிகாரத்தின் முதல் காண்டம் புகார்க்காண்டம் ஆகும். இது புகார் நகரத்தை மையமாகக் கொண்ட நிகழ்வுகளை எடுத்துரைக்கிறது. கோவலன், கண்ணகி மற்றும் மாதவி ஆகியோரின் வாழ்க்கையில் நடைபெறும் முக்கிய நிகழ்வுகள் இப்பகுதியில் இடம்பெறுகின்றன. கோவலன் மற்றும் கண்ணகியின் வாழ்க்கையில் ஏற்படும் மாற்றங்களுக்கும் இது அடித்தளமாக அமைகிறது."
  },
  {
    id: 8,
    question: "சிலப்பதிகாரத்தின் இரண்டாவது காண்டம் எது?",
    answer: "சிலப்பதிகாரத்தின் இரண்டாவது காண்டம் மதுரைக்காண்டம் ஆகும். இதில் கோவலனும் கண்ணகியும் மதுரைக்குச் செல்லும் நிகழ்வுகள் முக்கியமாக இடம்பெறுகின்றன. கோவலன் அநியாயமாகக் கொல்லப்படுவதும், கண்ணகி மதுரை அரசனிடம் நீதி கேட்பதும் இக்காண்டத்தின் முக்கிய நிகழ்வுகளாகும். கண்ணகியின் நீதிப் போராட்டம் இப்பகுதியில் உச்சத்தை அடைகிறது."
  },
  {
    id: 9,
    question: "சிலப்பதிகாரத்தின் மூன்றாவது காண்டம் எது?",
    answer: "சிலப்பதிகாரத்தின் மூன்றாவது காண்டம் வஞ்சிக்காண்டம் ஆகும். இது சேர நாட்டையும் சேர மன்னன் செங்குட்டுவனையும் மையமாகக் கொண்டுள்ளது. கண்ணகியின் சிறப்பும் பத்தினி வழிபாட்டின் முக்கியத்துவமும் இக்காண்டத்தில் எடுத்துரைக்கப்படுகின்றன. இதன் மூலம் சிலப்பதிகாரத்தின் கதை நிறைவுப் பகுதிக்குச் செல்கிறது."
  },
  {
    id: 10,
    question: "சிலப்பதிகாரத்தில் கண்ணகி எவ்வாறு சிறப்பிக்கப்படுகிறார்?",
    answer: "சிலப்பதிகாரத்தில் கண்ணகி கற்பு, துணிவு மற்றும் நீதியின் அடையாளமாகச் சிறப்பிக்கப்படுகிறார். தனது கணவன் அநியாயமாகக் கொல்லப்பட்டதை அறிந்தவுடன், உண்மையை நிரூபிக்க அரசனிடம் நேரடியாகச் சென்று நீதி கேட்கிறாள். தனது சிலம்பின் மூலம் கோவலன் குற்றமற்றவன் என்பதை நிரூபிக்கிறாள். இதனால் கண்ணகி தமிழர் பண்பாட்டில் முக்கியமான பெண் பாத்திரமாகவும் பத்தினித் தெய்வமாகவும் போற்றப்படுகிறார்."
  }
];

export const tanglishQuestions: QuestionItem[] = [
  {
    id: 1,
    question: "Silappathikaarathai iyatriyavar yaar?",
    answer: "Silappathikaarathai iyatriyavar Ilango Adigal aavaar. Ivar Chera mannar kudumbathai sernthavar ena koorappadugiradhu. Silappathikaaram Tamilin Aimperum Kaappiyangalil onraagaum. Kannagi matrum Kovalanin vaazhkaiyin moolamaaga aram matrum neethiyin mukkiyathuvathai indha nool eduthuraikkiradhu."
  },
  {
    id: 2,
    question: "Silappathikaarathin kadhanaayagi yaar?",
    answer: "Silappathikaarathin kadhanaayagi Kannagi aavaar. Kannagi karpu, thunivu matrum neethiyin adaiyaalamaaga kaattappadugiraal. Than kanavan Kovalan aniyaayamaaga kollappattadhai arindha piragu, unmaiyai nirupikka Madurai arasanidam sendru neethi ketkiraal. Idhanaal Kannagiyin paaththiram Tamil kaappiya varalatril migavum mukkiyamaanadhaaga vilangugiradhu."
  },
  {
    id: 3,
    question: "Kannagiyin kanavar yaar?",
    answer: "Kannagiyin kanavar Kovalan aavaar. Kovalan selvandha vaniga kudumbathai sernthavar. Maadhaviyudan erpatta thodarbin kaaranamaaga thanadhu selvathai izhandha piragu meendum Kannagiyidam thirumbugiraar. Pinnar iruvarum Maduraikku sendru pudhiya vaazhkaiyai thodanga muyarchi seygiraargal."
  },
  {
    id: 4,
    question: "Silappathikaarathil Kovalan sendra nagaram edhu?",
    answer: "Kovalan Kannagiyudan Madurai nagarathirkku selgiraar. Angu Kannagiyin silambai vitru pudhiya vaazhkaiyai thodanga muyarchikkiraar. Aanaal andha silambu arasiyaarudaiya silambu ena thavaraaga karuthappattadhaal Kovalan kutravaaliyaaga karuthappadugiraar. Idhan vilaivaaga avar aniyaayamaaga thandikkappadugiraar."
  },
  {
    id: 5,
    question: "Kannagiyin silambil irundhadhu enna?",
    answer: "Kannagiyin silambil maanikkak kargal irundhana. Kovalan Kannagiyin silambai virka muyandrapodhu, adhu arasiyaarudaiya silambudan thodarbudaiyadhaaga thavaraaga karuthappattadhu. Pinnar Kannagi thanadhu silambai udaiththu adhil maanikkangal iruppadhai nirubikkiraal. Idhan moolam Kovalan kutramatravan enbadhai velippaduthugiraal."
  },
  {
    id: 6,
    question: "Kovalanudan thodarbudaiya nadanak kalaignar yaar?",
    answer: "Kovalanudan thodarbudaiya nadanak kalaignar Maadhavi aavaal. Maadhavi Puhar nagarathil pugazhpetra nadanak kalaignaraaga vilanginaal. Kovalan avaludan vaazhntha kaalathil thanadhu selvathai izhandhaan. Pinnar Kovalan Maadhaviyai vittu Kannagiyidam thirumbugiraar."
  },
  {
    id: 7,
    question: "Silappathikaarathin mudhal kaandam edhu?",
    answer: "Silappathikaarathin mudhal kaandam Puharkkaandam aagum. Idhu Puhar nagarai maiyamaaga konda nigazhvugalai eduthuraikkiradhu. Kovalan, Kannagi matrum Maadhaviyin vaazhkaiyil nadakkum mukkiya nigazhvugal ippagudiyil idamperugindrana. Kovalan matrum Kannagiyin vaazhkaiyil erpadum maatrangalukkum idhu adithalamaaga amaigiradhu."
  },
  {
    id: 8,
    question: "Silappathikaarathin irandaavadhu kaandam edhu?",
    answer: "Silappathikaarathin irandaavadhu kaandam Maduraikkaandam aagum. Idhil Kovalanum Kannagiyum Maduraikku sellum nigazhvugal mukkiyamaaga idamperugindrana. Kovalan aniyaayamaaga kollappaduvadhum, Kannagi Madurai arasanidam neethi ketpadhum ikkaandathin mukkiya nigazhvugalaaga amaigindrana. Kannagiyin neethikkaana poraattam ippagudiyil uchchathai adaigiradhu."
  },
  {
    id: 9,
    question: "Silappathikaarathin moondraavadhu kaandam edhu?",
    answer: "Silappathikaarathin moondraavadhu kaandam Vanjikkaandam aagum. Idhu Chera naattaiyum Chera mannan Senguttuvanaiyum maiyamaaga kondulladhu. Kannagiyin sirappum Paththini vazhipaattin mukkiyathuvamum ikkaandathil eduthuraikkappadugindrana. Idhan moolam Silappathikaarathin kathai niraivup pagudhikku selgiradhu."
  },
  {
    id: 10,
    question: "Silappathikaarathil Kannagi evvaaru sirappikkappadugiraal?",
    answer: "Silappathikaarathil Kannagi karpu, thunivu matrum neethiyin adaiyaalamaaga sirappikkappadugiraal. Than kanavan aniyaayamaaga kollappattadhai arindhavudan, unmaiyai nirupikka arasanidam neradiyaaga sendru neethi ketkiraal. Thanadhu silambin moolam Kovalan kutramatravan enbadhai nirupikkiraal. Idhanaal Kannagi Tamilargalin panpaatil mukkiyamaana pen paaththiramaagavum Paththini theyvamaagavum potrappadugiraal."
  }
];

export const questions = tamilQuestions;
export default questions;
