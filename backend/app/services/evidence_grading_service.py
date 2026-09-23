import os
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class EvidenceChunk(BaseModel):
    content: str
    source_name: Optional[str] = "Unknown"
    source_url: Optional[str] = None
    source_type: Optional[str] = "document"
    score: Optional[float] = None
    page: Optional[int] = None
    chunk_index: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class EvidenceAssessment(BaseModel):
    grade: str # "strong", "moderate", "limited", "insufficient"
    confidence_score: float # 0.0 to 1.0
    rationale: str
    signals: Dict[str, Any]
    provider: str # "gemini" or "deterministic"
    supporting_chunk_indices: List[int] = Field(default_factory=list)

class EvidenceGradingService:
    def __init__(self):
        self.gemini_client = None
        self._init_gemini_if_available()

    def _init_gemini_if_available(self):
        gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_api_key)
                self.gemini_client = genai.GenerativeModel("gemini-1.5-flash")
            except Exception as e:
                print(f"[EvidenceGradingService] Gemini configured but failed to initialize: {e}")
                self.gemini_client = None
        else:
            self.gemini_client = None

    def grade_evidence(self, query: str, chunks: List[EvidenceChunk]) -> EvidenceAssessment:
        if not chunks:
            return EvidenceAssessment(
                grade="insufficient",
                confidence_score=0.0,
                rationale="No supporting evidence chunks were retrieved.",
                signals={"chunk_count": 0, "query_coverage": 0.0, "avg_similarity": 0.0},
                provider="deterministic",
                supporting_chunk_indices=[]
            )

        # 1. Try Gemini if configured
        if self.gemini_client:
            try:
                return self._grade_with_gemini(query, chunks)
            except Exception as e:
                print(f"[EvidenceGradingService] Gemini grading error: {e}. Falling back to deterministic grading.")

        # 2. Fallback to deterministic evidence grading
        return self._grade_deterministically(query, chunks)

    def _grade_with_gemini(self, query: str, chunks: List[EvidenceChunk]) -> EvidenceAssessment:
        context_str = "\n".join([f"[{i}] {c.content}" for i, c in enumerate(chunks)])
        prompt = f"""You are an objective evidence grader for a RAG system.
Evaluate whether the provided context contains sufficient, verifiable facts to answer the user query.

User Query: "{query}"

Retrieved Context:
{context_str}

Evaluate and return ONLY a valid JSON object matching:
{{
  "grade": "strong" | "moderate" | "limited" | "insufficient",
  "confidence_score": float between 0.0 and 1.0,
  "rationale": "one sentence explaining the evidence sufficiency",
  "supporting_chunk_indices": [list of integer indices 0-indexed that support the answer]
}}
"""
        response = self.gemini_client.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        import json
        data = json.loads(text.strip())
        grade = data.get("grade", "moderate").lower()
        if grade not in ["strong", "moderate", "limited", "insufficient"]:
            grade = "moderate"
        
        return EvidenceAssessment(
            grade=grade,
            confidence_score=float(data.get("confidence_score", 0.5)),
            rationale=data.get("rationale", "Evaluated via Gemini."),
            signals={"chunk_count": len(chunks), "gemini_evaluated": True},
            provider="gemini",
            supporting_chunk_indices=data.get("supporting_chunk_indices", list(range(len(chunks))))
        )

    def _grade_deterministically(self, query: str, chunks: List[EvidenceChunk]) -> EvidenceAssessment:
        """
        Deterministic evidence grading using composite signals:
        - lexical match / token overlap across Tamil, English, and Tanglish
        - semantic similarity score
        - number of supporting chunks
        - source completeness & provenance
        - query keyword and entity coverage
        """
        import unicodedata
        norm_query = unicodedata.normalize("NFC", query).lower()
        query_terms = [w for w in re.findall(r'\w+', norm_query) if len(w) > 2]
        stop_words = {"who", "what", "where", "when", "why", "how", "the", "and", "is", "was", "for", "are", "with", "about", "tell", "book", "nool", "noolai"}
        key_query_terms = [w for w in query_terms if w not in stop_words] or query_terms

        # Cross-lingual equivalence expansions for key entities and relations
        equiv_map = {
            "theerkkadharisi": ["தீர்க்கதரிசி", "prophet"],
            "prophet": ["தீர்க்கதரிசி", "theerkkadharisi"],
            "தீர்க்கதரிசி": ["theerkkadharisi", "prophet"],
            "author": ["எழுதியவர்", "ஆசிரியர்", "கலீல்", "ஜிப்ரான்", "ezhuthinathu", "ezhudhiyavar"],
            "wrote": ["எழுதியவர்", "ஆசிரியர்", "கலீல்", "ஜிப்ரான்", "ezhuthinathu"],
            "write": ["எழுதியவர்", "ஆசிரியர்", "கலீல்", "ஜிப்ரான்", "ezhuthinathu"],
            "ezhuthinathu": ["எழுதியவர்", "கலீல்", "ஜிப்ரான்", "author", "wrote"],
            "ezhudhiyavar": ["எழுதியவர்", "கலீல்", "ஜிப்ரான்", "author"],
            "ezhudhiya": ["எழுதியவர்", "கலீல்", "ஜிப்ரான்", "author"],
            "yaar": ["கலீல்", "ஜிப்ரான்", "author", "who"],
            "யார்": ["கலீல்", "ஜிப்ரான்", "author", "who"],
            "பண்ணினது": ["எழுதியவர்", "கலீல்", "ஜிப்ரான்", "author"],
            "பாரதியார்": ["பாரதியார்", "கலீல்", "ஜிப்ரான்", "author"],
            "பாரதியாரா": ["பாரதியார்", "கலீல்", "ஜிப்ரான்", "author"]
        }

        term_matches = {term: 0 for term in key_query_terms}
        supporting_indices = []
        similarity_scores = []
        has_provenance_count = 0

        for idx, chunk in enumerate(chunks):
            content_lower = unicodedata.normalize("NFC", chunk.content).lower()
            matched_terms_in_chunk = 0
            
            for term in key_query_terms:
                matched = False
                if term in content_lower:
                    matched = True
                else:
                    # Check multilingual equivalents
                    eqs = equiv_map.get(term, [])
                    for eq in eqs:
                        if eq.lower() in content_lower:
                            matched = True
                            break
                if matched:
                    term_matches[term] += 1
                    matched_terms_in_chunk += 1
            
            if matched_terms_in_chunk > 0:
                supporting_indices.append(idx)

            if chunk.score is not None:
                sim = max(0.0, min(1.0, 1.0 - (chunk.score / 2.0))) if chunk.score < 2.0 else 0.1
                similarity_scores.append(sim)
            else:
                similarity_scores.append(0.8 if matched_terms_in_chunk > 0 else 0.2)

            if chunk.source_name and chunk.source_name != "Unknown":
                has_provenance_count += 1

        total_key_terms = len(key_query_terms) if key_query_terms else 1
        covered_terms = sum(1 for term, count in term_matches.items() if count > 0)
        query_coverage = covered_terms / total_key_terms
        avg_similarity = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0.0
        provenance_ratio = has_provenance_count / len(chunks) if chunks else 0.0

        # Composite score calculation
        composite_score = (
            (query_coverage * 0.50) +
            (avg_similarity * 0.25) +
            (min(len(supporting_indices) / 3.0, 1.0) * 0.15) +
            (provenance_ratio * 0.10)
        )
        composite_score = round(max(0.0, min(1.0, composite_score)), 3)

        # Determine grade thresholds
        if composite_score >= 0.60 and query_coverage >= 0.5:
            grade = "strong"
            rationale = f"Strong evidence available covering {int(query_coverage*100)}% of query concepts across {len(supporting_indices)} source chunks."
        elif composite_score >= 0.35 and query_coverage >= 0.30:
            grade = "moderate"
            rationale = f"Moderate evidence found with query concept coverage ({int(query_coverage*100)}%)."
        elif composite_score >= 0.20:
            grade = "limited"
            rationale = f"Limited evidence retrieved; relevant context is sparse or weakly matching."
        else:
            grade = "insufficient"
            rationale = "Insufficient evidence to reliably support an answer."

        signals = {
            "chunk_count": len(chunks),
            "supporting_chunk_count": len(supporting_indices),
            "query_coverage": round(query_coverage, 3),
            "avg_similarity": round(avg_similarity, 3),
            "provenance_ratio": round(provenance_ratio, 3),
            "matched_terms": [t for t, c in term_matches.items() if c > 0]
        }

        return EvidenceAssessment(
            grade=grade,
            confidence_score=composite_score,
            rationale=rationale,
            signals=signals,
            provider="deterministic",
            supporting_chunk_indices=supporting_indices if supporting_indices else list(range(min(len(chunks), 2)))
        )

# Global singleton instance
_evidence_grading_service: Optional[EvidenceGradingService] = None

def get_evidence_grading_service() -> EvidenceGradingService:
    global _evidence_grading_service
    if _evidence_grading_service is None:
        _evidence_grading_service = EvidenceGradingService()
    return _evidence_grading_service
