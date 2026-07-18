import pytest
from src.domain.text_models import Transcript, SentenceAnalysis
from src.text.text_analyzer import TextAnalyzer

def test_text_analyzer_empty():
    analyzer = TextAnalyzer()
    transcript = Transcript(full_text="", sentences=[])
    result = analyzer.analyze(transcript)
    
    assert result.overall_sentiment == 0.0
    assert len(result.transcript.sentences) == 0

def test_text_analyzer_single_sentence():
    analyzer = TextAnalyzer()
    transcript = Transcript(full_text="Estou com muito medo.", sentences=[])
    result = analyzer.analyze(transcript)
    
    assert len(result.transcript.sentences) == 1
    s = result.transcript.sentences[0]
    assert s.keyword_count == 1
    assert "MEDO" in s.categories
    assert s.risk_level == "moderado"

def test_text_analyzer_multiple_sentences():
    analyzer = TextAnalyzer()
    transcript = Transcript(full_text="Tudo bem. Ele me empurrou e bateu. Socorro! O que eu faço?", sentences=[])
    result = analyzer.analyze(transcript)
    
    assert len(result.transcript.sentences) == 4
    
    s0 = result.transcript.sentences[0]
    assert s0.keyword_count == 0
    assert len(s0.categories) == 0
    assert s0.risk_level == "baixo"

    s1 = result.transcript.sentences[1]
    assert s1.keyword_count == 2 # empurrou, bateu
    assert "VIOLÊNCIA" in s1.categories
    assert s1.risk_level == "moderado"

    s2 = result.transcript.sentences[2]
    assert s2.keyword_count == 1 # socorro
    assert "AJUDA" in s2.categories

def test_text_analyzer_no_keywords():
    analyzer = TextAnalyzer()
    transcript = Transcript(full_text="O dia está ensolarado. Fui ao mercado comprar pão.", sentences=[])
    result = analyzer.analyze(transcript)
    
    assert len(result.transcript.sentences) == 2
    for s in result.transcript.sentences:
        assert s.keyword_count == 0
        assert len(s.categories) == 0
        assert s.risk_level == "baixo"

def test_text_analyzer_multiple_categories():
    analyzer = TextAnalyzer()
    transcript = Transcript(full_text="Tenho muito medo porque ele me bateu.", sentences=[])
    result = analyzer.analyze(transcript)
    
    s = result.transcript.sentences[0]
    assert "MEDO" in s.categories
    assert "VIOLÊNCIA" in s.categories
    assert s.keyword_count == 2
    assert s.risk_level == "moderado"

def test_text_analyzer_high_risk():
    analyzer = TextAnalyzer()
    transcript = Transcript(full_text="Sinto pavor e terror constante, muito medo.", sentences=[])
    result = analyzer.analyze(transcript)
    
    s = result.transcript.sentences[0]
    assert s.keyword_count == 3
    assert s.risk_level == "alto"

def test_text_analyzer_serialization():
    analyzer = TextAnalyzer()
    transcript = Transcript(full_text="Medo! Socorro!", sentences=[])
    result = analyzer.analyze(transcript)
    
    data = result.to_dict()
    assert "transcript" in data
    assert len(data["transcript"]["sentences"]) == 2
    
    s0 = data["transcript"]["sentences"][0]
    assert "MEDO" in s0["categories"]
