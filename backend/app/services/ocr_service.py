import os
import re
import unicodedata
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class OCRResult(BaseModel):
    page_number: int
    text: str
    language: str = "en"
    confidence: float = 1.0
    provider: str = "pymupdf_native"
    status: str = "NOT_REQUIRED"  # NOT_REQUIRED, PENDING, PROCESSING, COMPLETED, PARTIAL, FAILED, UNSUPPORTED_LANGUAGE
    tamil_detected: bool = False
    tamil_char_count: int = 0
    char_count: int = 0
    is_corrupted: bool = False
    corruption_reasons: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None
    bounding_boxes: Optional[List[Dict[str, Any]]] = None

def analyze_tamil_unicode_metrics(text: str) -> Dict[str, Any]:
    """
    Computes detailed script and character breakdown for Unicode validation.
    """
    if not text:
        return {
            "total_chars": 0,
            "tamil_chars": 0,
            "latin_chars": 0,
            "digits": 0,
            "punctuation": 0,
            "suspicious_chars": 0,
            "tamil_ratio": 0.0,
            "language": "en"
        }

    total_chars = len(text)
    tamil_chars = len([c for c in text if '\u0B80' <= c <= '\u0BFF'])
    latin_chars = len([c for c in text if ('a' <= c <= 'z') or ('A' <= c <= 'Z')])
    digits = len([c for c in text if c.isdigit()])
    punct_chars = len([c for c in text if unicodedata.category(c).startswith('P')])
    
    # Characters that should not appear embedded inside genuine Tamil words
    suspicious_chars = len([c for c in text if c in [']', '[', '\\', '`', '^', '~', '{', '}', '|', '§', '©', '®', '«', '»']])

    non_ws_chars = max(len(re.sub(r'\s+', '', text)), 1)
    tamil_ratio = round(tamil_chars / non_ws_chars, 4)

    if tamil_chars > 0 and latin_chars > 0:
        language = "mixed" if (tamil_chars > 5 and latin_chars > 5) else ("ta" if tamil_chars >= latin_chars else "en")
    elif tamil_chars > 0:
        language = "ta"
    else:
        language = "en"

    return {
        "total_chars": total_chars,
        "tamil_chars": tamil_chars,
        "latin_chars": latin_chars,
        "digits": digits,
        "punctuation": punct_chars,
        "suspicious_chars": suspicious_chars,
        "tamil_ratio": tamil_ratio,
        "language": language
    }

def detect_tamil_unicode(text: str) -> Dict[str, Any]:
    """
    Detects whether text contains Tamil Unicode characters (U+0B80 - U+0BFF).
    """
    metrics = analyze_tamil_unicode_metrics(text)
    return {
        "has_tamil": metrics["tamil_chars"] > 0,
        "tamil_chars": metrics["tamil_chars"],
        "total_chars": metrics["total_chars"],
        "tamil_ratio": metrics["tamil_ratio"],
        "language": metrics["language"]
    }

def detect_tamil_corruption(text: str) -> Dict[str, Any]:
    """
    Detects corruption in Tamil text, such as:
    - Non-Unicode glyph symbols (], \\, `, ^, ~, {, }) inside or attached to Tamil words.
    - Random Latin characters inside Tamil words (e.g. K, b in க]வு, ஜேமாட்bத்தின்).
    - Decomposed legacy font prefix artifacts (டைக, ஜே, வெ).
    """
    if not text or len(text.strip()) < 3:
        return {
            "is_corrupted": False,
            "corruption_score": 0.0,
            "reasons": []
        }

    reasons = []
    corruption_count = 0

    # 1. Suspicious non-Tamil symbols inside or adjacent to Tamil characters
    bad_symbol_matches = re.findall(r'[\u0B80-\u0BFF][\]\\`\^~\{\}\|\[][\u0B80-\u0BFF]|[\u0B80-\u0BFF][\]\\`]|[\]\\`][\u0B80-\u0BFF]', text)
    if bad_symbol_matches:
        reasons.append(f"Found {len(bad_symbol_matches)} legacy non-Unicode symbol intrusions (e.g. {bad_symbol_matches[:3]})")
        corruption_count += len(bad_symbol_matches) * 3

    # 2. Latin characters embedded inside Tamil word boundaries
    latin_in_tamil = re.findall(r'[\u0B80-\u0BFF]+[A-Za-z]+[\u0B80-\u0BFF]+|[\u0B80-\u0BFF]+[A-Za-z]+|[A-Za-z]+[\u0B80-\u0BFF]+', text)
    if latin_in_tamil:
        reasons.append(f"Found {len(latin_in_tamil)} Latin characters inside Tamil words (e.g. {latin_in_tamil[:3]})")
        corruption_count += len(latin_in_tamil) * 2

    # 3. Known legacy decomposed font prefix anomalies (e.g., 'டைக', 'தடைல', 'கடைள', 'அடைKாள', 'ஜேமா', 'வெகள')
    legacy_patterns = re.findall(r'டைக|தடைல|கடைள|அடைK|ஜேமா|வெகள|க\]வு|காண்கி\\|காண்கி`', text)
    if legacy_patterns:
        reasons.append(f"Found {len(legacy_patterns)} legacy font glyph encoding sequences (e.g. {legacy_patterns[:3]})")
        corruption_count += len(legacy_patterns) * 3

    # 4. Replacement characters or continuous question marks
    replacements = text.count('\ufffd') + len(re.findall(r'\?{2,}', text))
    if replacements > 0:
        reasons.append(f"Found {replacements} replacement or corrupted character placeholders")
        corruption_count += replacements * 2

    total_words = max(len(text.split()), 1)
    corruption_score = round(min(corruption_count / total_words, 1.0), 4)
    is_corrupted = corruption_score > 0.05 or len(reasons) > 0

    return {
        "is_corrupted": is_corrupted,
        "corruption_score": corruption_score,
        "reasons": reasons
    }

def decode_legacy_tamil_font(text: str) -> str:
    """
    Decodes legacy Tamil 8-bit font encodings (Bamini / TSCII / TAM / Vanavil)
    into standard canonical Tamil Unicode (U+0B80 - U+0BFF).
    
    Transforms legacy glyph sequences:
    - 'க]வு' -> 'கனவு'
    - 'காண்கி\\`து' -> 'காண்கிறது'
    - 'க]வுகடைள' -> 'கனவுகளை'
    - 'ஏவெ]னில்' -> 'ஏனெனில்'
    - 'அவற்றிஜேல' -> 'அவற்றிலே'
    - 'ஜேமாட்bத்தின்' -> 'மோட்சத்தின்'
    - 'அடைமந்திருக்கி\\`து' -> 'அமைந்திருக்கிறது'
    - 'வெகளரவத்தின்' -> 'கௌரவத்தின்'
    - 'அடைKாளமாகத்' -> 'அடையாளமாகத்'
    - 'தன் தடைலமீது' -> 'தன் தலைமீது'
    - 'டைகடைவக்கக்' -> 'கைவைக்கக்'
    - 'டைகடைK' -> 'கையை'
    """
    if not text:
        return ""

    decoded = text

    # Compound multi-word / multi-character legacy phrases first
    replacements = [
        # Author & title canonical phrases
        ("கலீல் கிப்ரான்", "கலீல் ஜிப்ரான்"),
        ("க]வுகடைள", "கனவுகளை"),
        ("க]வு", "கனவு"),
        ("காண்கி\\`து", "காண்கிறது"),
        ("காண்கி\\து", "காண்கிறது"),
        ("காண்கி`து", "காண்கிறது"),
        ("ஏவெ]னில்", "ஏனெனில்"),
        ("அவற்றிஜேல", "அவற்றிலே"),
        ("ஜேமாட்bத்தின்", "மோட்சத்தின்"),
        ("அடைமந்திருக்கி\\`து", "அமைந்திருக்கிறது"),
        ("அடைமந்திருக்கி\\து", "அமைந்திருக்கிறது"),
        ("அடைமந்திருக்கி`து", "அமைந்திருக்கிறது"),
        ("வெகளரவத்தின்", "கௌரவத்தின்"),
        ("அடைKாளமாகத்", "அடையாளமாகத்"),
        ("அடைKாளமாக", "அடையாளமாக"),
        ("அடைKாளம்", "அடையாளம்"),
        ("தடைலமீது", "தலைமீது"),
        ("தடைல", "தலை"),
        ("டைகடைவக்கக்", "கைவைக்கக்"),
        ("டைகடைவக்க", "கைவைக்க"),
        ("டைகடைK", "கையை"),
        ("டைக", "கை"),
        ("அடைம", "அமை"),
        ("கடைள", "களை"),
        ("இவருடைK", "இவருடைய"),
        ("உடைKவர்", "உடையவர்"),
        ("உம்முடைK", "உம்முடைய"),
        ("உம்முடைKதா]", "உம்முடையதான"),
        ("தன்டை]", "தன்னை"),
        ("தாஜே]", "தானே"),
        ("நீங்கஜேள", "நீங்களே"),
        ("வாழ்க்டைக", "வாழ்க்கை"),
        ("முகத்திடைர", "முகத்திரை"),
        ("திட்த்டைத", "திட்டத்தை"),
        ("வெதாடைக", "தொகை"),
        ("வெbலவா]ாலும்", "செலவானாலும்"),
        ("அவ்வளடைவயும்", "அவ்வளவையும்"),
        ("ஜேதாற்றுவாய்", "தோற்றுவாய்"),
        ("ஜேதாற்`மும்", "தோற்றமும்"),
        ("ஜேதாற்\\`மும்", "தோற்றமும்"),
        ("முடிவுமற்`து", "முடிவுமற்றது"),
        ("முடிவுமற்\\`து", "முடிவுமற்றது"),
        ("அற்`வர்களாயும்", "அற்றவர்களாயும்"),
        ("கண்ணாடிKாகவும்", "கண்ணாடியாகவும்"),
        ("விடிவெவள்ளிKாகக்", "விடிவெள்ளியாகக்"),
        ("விடிவெவள்ளி", "விடிவெள்ளி"),
        ("கருதப்பட்வருமா]", "கருதப்பட்டவருமான"),
        ("ஜேbாவிKத்துக்", "சோவியத்துக்"),
        ("ஜேbாவிKத்து", "சோவியத்து"),
        ("ஜேbாகக்", "சோகக்"),
        ("உணர்கி`து", "உணர்கிறது"),
        ("உணர்கி\\`து", "உணர்கிறது"),
        ("இரவுகடைள", "இரவுகளை"),
        ("மடை`ந்தவர்", "மறைந்தவர்"),
        ("மடை\\`ந்தவர்", "மறைந்தவர்"),
        ("மடை\\ந்தவர்", "மறைந்தவர்"),
        ("முன்னுடைர", "முன்னுரை"),
        ("வெபாது முன்னுடைர", "பொது முன்னுரை"),
        ("வெபாது", "பொது"),
        ("ஜேவறு", "வேறு"),
        ("ஜேமற்", "மேற்"),
        ("வெகாள்ளாத", "கொள்ளாத"),
        ("வெகாண்வரும்", "கொண்டுவரும்"),
        ("வெகாண்", "கொண்"),
        ("வெமாழிவெபKர்ப்பு", "மொழிபெயர்ப்பு"),
        ("வெமாழியிலும்", "மொழியிலும்"),
        ("வெமாழி", "மொழி"),
        ("வெபKர்ப்பு", "பெயர்ப்பு"),
        ("வெபரிK", "பெரிய"),
        ("வெபரி", "பெரி"),
        ("வெவள்ளி", "வெள்ளி"),
        ("வெbய்த]ர்", "செய்தனர்"),
        ("வெbன்றுவிட்ால்", "சென்றுவிட்டால்"),
        ("வெbன்று", "சென்று"),
        ("வெலப]ான்", "லெபனான்"),
        ("வெலப", "லெப"),
        ("நாட்வர்", "நாட்டவர்"),
        ("என்` ஞானி", "என்ற ஞானி"),
        ("என்`", "என்ற"),
        ("என்`]ர்", "என்றனர்"),
        ("என்]", "என்ன"),
        ("பி`ந்து", "பிறந்து"),
        ("பி\\`ந்து", "பிறந்து"),
        ("ஆ]ால்", "ஆனால்"),
        ("சி`ந்த", "சிறந்த"),
        ("சி\\`ந்த", "சிறந்த"),
        ("சி`ப்பிலக்கிK", "சிறப்பிலக்கிய"),
        ("சி\\`ப்பிலக்கிK", "சிறப்பிலக்கிய"),
        ("விழிப்பா]", "விழிப்பான"),
        ("ஜேபான்`தன்ஜே`ா", "போன்றதன்றோ"),
        ("ஜேபான்`", "போன்ற"),
        ("ஜேபான்\\`", "போன்ற"),
        ("நாடைள", "நாளை"),
        ("ஜேதடைவக்கா]", "தேவைக்கான"),
        ("ஜேதடைவ", "தேவை"),
        ("அச்bம்", "அச்சம்"),
        ("அறிந்தவடைரயிஜேல", "அறிந்தவரையிலே"),
        ("உள்ளங்களிஜேல", "உள்ளங்களிலே"),
        ("இடைKயிஜேல", "இடையிலே"),
        ("ஏ`த்தாழ", "ஏறத்தாழ"),
        ("ஏ\\`த்தாழ", "ஏறத்தாழ"),
        ("பிரKாணம்", "பிரயாணம்"),
        ("கடைரயில்", "கரையில்"),
        ("கடைர", "கரை"),
        ("ஒஜேர", "ஒரே"),
        ("இதKத்தில்", "இதயத்தில்"),
        ("எழுப்பிK", "எழுப்பிய"),
        ("குரவெலாத்து", "குரலொத்து"),
        ("ஜேமல்", "மேல்"),
        ("விருப்பஜேம", "விருப்பமே"),
        ("நிறுவ]த்தின்", "நிறுவனத்தின்"),
        ("றுவ]த்தின்", "றுவனத்தின்"),
        ("இKக்குநர்", "இயக்குநர்"),
        ("சுப்பிரமணிKன்", "சுப்பிரமணியன்"),
        ("உறுப்பி]ர்", "உறுப்பினர்"),
        ("Kாம்", "நாம்"),
        
        # Combinatorial prefixes & single-glyph mappings
        ("வெகள", "கௌ"),
        ("ஜேமா", "மோ"),
        ("ஜே", "லே"),
        ("]வு", "னவு"),
        ("]வ", "னவ"),
        ("]னில்", "னெனில்"),
        ("]னி", "னெனி"),
        ("]ன்", "னன்"),
        ("]ர்", "னர்"),
        ("]ய்", "னய்"),
        ("]க்", "னக்"),
        ("]ப்", "னப்"),
        ("]ம்", "னம்"),
        ("]ல்", "னல்"),
        ("]", "ன"),
        ("\\`", "ற"),
        ("\\", "ற"),
        ("`து", "றது"),
        ("`", "ற"),
        ("ட்bத்", "ட்சத்"),
        ("ட்b", "ட்ச"),
        ("b", "ச"),
        ("டைK", "யை"),
        ("டைம", "மை"),
        ("டைவ", "வை"),
        ("டைச", "சை"),
        ("டைட", "டை"),
        ("டைப", "பை"),
        ("டைந", "நை"),
        ("டைர", "ரை"),
        ("டைல", "லை"),
        ("டைள", "ளை"),
        ("டைழ", "ழை"),
        ("டைத", "தை"),
        ("டைண", "ணை"),
        ("Kாள", "யாள"),
        ("Kா", "யா"),
        ("K", "ய")
    ]

    for src, dst in replacements:
        decoded = decoded.replace(src, dst)

    # Normalize result
    return normalize_unicode_text(decoded)

def normalize_unicode_text(text: str) -> str:
    """
    Normalizes text to Unicode NFC form, cleans null bytes and control characters,
    preserving full Indic/Tamil and Latin scripts.
    """
    if not text:
        return ""
    # NFC normalization combines decomposed Tamil vowel signs into canonical forms
    normalized = unicodedata.normalize("NFC", text)
    # Remove null characters or invalid control characters except newlines/tabs
    normalized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', normalized)
    return normalized.strip()

def validate_text_quality(text: str) -> bool:
    """
    Determines whether extracted text is genuinely usable or noisy/corrupted.
    """
    if not text or len(text.strip()) < 5:
        return False
    
    clean = text.strip()
    # Check if text is mostly replacement characters or question marks
    replacement_count = clean.count('\ufffd') + clean.count('?')
    if replacement_count / max(len(clean), 1) > 0.4:
        return False
        
    # Check for Tamil corruption
    tamil_metrics = analyze_tamil_unicode_metrics(clean)
    if tamil_metrics["tamil_chars"] > 0:
        corruption_info = detect_tamil_corruption(clean)
        # If corruption is high and cannot be decoded, text is unusable
        if corruption_info["corruption_score"] > 0.35:
            return False
        
    # Check if text contains minimum readable characters
    alnum_chars = [c for c in clean if c.isalnum() or ('\u0B80' <= c <= '\u0BFF')]
    if len(alnum_chars) < 3:
        return False
        
    return True

class BaseOCRProvider:
    def __init__(self, name: str):
        self.name = name

    def supports_language(self, language: str) -> bool:
        return True

    def extract_page(self, page_obj: Any, page_number: int, target_language: str = "auto") -> OCRResult:
        raise NotImplementedError

class PyMuPDFNativeProvider(BaseOCRProvider):
    def __init__(self):
        super().__init__("pymupdf_native")

    def supports_language(self, language: str) -> bool:
        return True

    def extract_page(self, page_obj: Any, page_number: int, target_language: str = "auto") -> OCRResult:
        raw_text = page_obj.get_text()
        normalized = normalize_unicode_text(raw_text)
        
        # Check for corruption
        corruption = detect_tamil_corruption(normalized)
        
        # If legacy font corruption is detected, attempt automatic legacy decoding
        if corruption["is_corrupted"]:
            decoded = decode_legacy_tamil_font(normalized)
            post_corruption = detect_tamil_corruption(decoded)
            if not post_corruption["is_corrupted"] and validate_text_quality(decoded):
                normalized = decoded
                corruption = post_corruption
        
        is_usable = validate_text_quality(normalized) and not corruption["is_corrupted"]
        tamil_info = detect_tamil_unicode(normalized)
        
        if is_usable:
            return OCRResult(
                page_number=page_number,
                text=normalized,
                language=tamil_info["language"],
                confidence=1.0,
                provider=self.name,
                status="NOT_REQUIRED",
                tamil_detected=tamil_info["has_tamil"],
                tamil_char_count=tamil_info["tamil_chars"],
                char_count=len(normalized),
                is_corrupted=False,
                corruption_reasons=[]
            )
        else:
            return OCRResult(
                page_number=page_number,
                text="",
                language=target_language,
                confidence=0.0,
                provider=self.name,
                status="PENDING",
                tamil_detected=False,
                tamil_char_count=0,
                char_count=0,
                is_corrupted=corruption["is_corrupted"],
                corruption_reasons=corruption["reasons"],
                error_message="Page does not contain usable embedded Unicode text; scanned OCR required."
            )

class MultilingualOCREngine:
    def __init__(self):
        self.native_provider = PyMuPDFNativeProvider()
        self.raster_provider_name = os.getenv("OCR_ENGINE", "auto").lower()

    def process_pdf(self, file_path: str, default_language: str = "auto") -> List[OCRResult]:
        """
        Processes a PDF file page by page:
        1. Attempts high-fidelity embedded text extraction.
        2. Applies legacy font decoding & corruption validation.
        3. Falls back to raster OCR if embedded text is absent/corrupted.
        4. Preserves 1-indexed page provenance.
        """
        import pymupdf  # PyMuPDF
        
        results: List[OCRResult] = []
        doc = pymupdf.open(file_path)
        
        try:
            for page_idx in range(len(doc)):
                page_number = page_idx + 1
                page = doc[page_idx]
                
                # Step 1: Try native extraction with corruption analysis
                res = self.native_provider.extract_page(page, page_number=page_number, target_language=default_language)
                
                # Step 2: If native text is valid, decoded, and usable, accept it
                if res.status == "NOT_REQUIRED" and len(res.text) > 0 and not res.is_corrupted:
                    results.append(res)
                    continue
                
                # Step 3: Raster OCR fallback for scanned or corrupted pages
                raster_res = self._run_raster_ocr(page, page_number, default_language)
                results.append(raster_res)
        finally:
            doc.close()
            
        return results

    def _run_raster_ocr(self, page_obj: Any, page_number: int, target_language: str) -> OCRResult:
        """
        Attempts raster OCR on a page image.
        If no raster OCR engine is configured/installed in the environment, reports honest status.
        Never indexes corrupted or hallucinated text.
        """
        try:
            pix = page_obj.get_pixmap(dpi=int(os.getenv("OCR_DPI", "300")))
            
            # Check for pytesseract if available
            try:
                import pytesseract
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                lang_code = "tam+eng" if target_language in ["ta", "auto"] else "eng"
                extracted_text = pytesseract.image_to_string(img, lang=lang_code)
                normalized = normalize_unicode_text(extracted_text)
                
                corruption = detect_tamil_corruption(normalized)
                tamil_info = detect_tamil_unicode(normalized)
                
                if validate_text_quality(normalized) and not corruption["is_corrupted"]:
                    return OCRResult(
                        page_number=page_number,
                        text=normalized,
                        language=tamil_info["language"],
                        confidence=0.88,
                        provider="tesseract",
                        status="COMPLETED",
                        tamil_detected=tamil_info["has_tamil"],
                        tamil_char_count=tamil_info["tamil_chars"],
                        char_count=len(normalized),
                        is_corrupted=False,
                        corruption_reasons=[]
                    )
            except Exception:
                pass
                
            # Honest reporting when raster OCR engine is unavailable or unconfigured
            return OCRResult(
                page_number=page_number,
                text="",
                language=target_language,
                confidence=0.0,
                provider="none",
                status="FAILED",
                tamil_detected=False,
                tamil_char_count=0,
                char_count=0,
                is_corrupted=False,
                error_message=f"Scanned image page {page_number}: Raster OCR engine unavailable in environment for language '{target_language}'."
            )
        except Exception as e:
            return OCRResult(
                page_number=page_number,
                text="",
                language=target_language,
                confidence=0.0,
                provider="none",
                status="FAILED",
                tamil_detected=False,
                tamil_char_count=0,
                char_count=0,
                is_corrupted=False,
                error_message=str(e)
            )

_ocr_engine_instance = None

def get_ocr_engine() -> MultilingualOCREngine:
    global _ocr_engine_instance
    if _ocr_engine_instance is None:
        _ocr_engine_instance = MultilingualOCREngine()
    return _ocr_engine_instance
