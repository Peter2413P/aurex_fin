import pytest
import os
import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.evidence_grading_service import get_evidence_grading_service, EvidenceChunk

def test_evidence_gate_with_strong_evidence():
    grader = get_evidence_grading_service()
    chunks = [
        EvidenceChunk(
            content="தீர்க்கதரிசி நூலை எழுதியவர் கலீல் ஜிப்ரான். (தமிழாக்கம் : நலங்கிள்ளி)",
            source_name="Dheerkadharisi_A4.pdf",
            score=0.1,
            page=2
        )
    ]
    assessment = grader.grade_evidence("தீர்க்கதரிசி நூலை எழுதியவர் யார்?", chunks)
    assert assessment.grade in ["strong", "moderate"]
    assert assessment.confidence_score >= 0.50
    assert 0 in assessment.supporting_chunk_indices

def test_evidence_gate_refuses_insufficient_evidence():
    grader = get_evidence_grading_service()
    chunks = [
        EvidenceChunk(
            content="The weather today is warm and sunny with scattered clouds.",
            source_name="WeatherReport.txt",
            score=1.8,
            page=1
        )
    ]
    assessment = grader.grade_evidence("What is the author of The Prophet?", chunks)
    assert assessment.grade == "insufficient"
    assert assessment.confidence_score < 0.35

def test_evidence_gate_empty_chunks():
    grader = get_evidence_grading_service()
    assessment = grader.grade_evidence("Who is the author?", [])
    assert assessment.grade == "insufficient"
    assert assessment.confidence_score == 0.0
