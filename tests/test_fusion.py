import pytest
from src.fusion.fusion_engine import FusionEngine
from src.domain.video_models import VideoAnalysis, FrameAnalysis, FaceDetection, ObjectDetection, FrameInfo, VideoInfo
from src.domain.text_models import TextAnalysis, Transcript, SentenceAnalysis
from src.domain.fusion_models import RiskLevel, FusionResult

@pytest.fixture
def engine():
    return FusionEngine()

def test_absence_of_data(engine):
    """Testa ausência total de dados e ausência de AudioAnalysis."""
    result = engine.process(video=None, audio=None, text=None)
    assert result.score == 0.0
    assert result.risk_level == RiskLevel.LOW
    assert len(result.evidences) == 0

def test_visual_only_low_risk(engine):
    """Testa somente análise visual com baixo risco."""
    # Video com muitos rostos e sem YOLO de risco
    frame_info = FrameInfo(1, 0.0)
    frame = FrameAnalysis(
        frame_info=frame_info,
        faces=[FaceDetection((0,0,10,10), 0.9, 10, 10)],
        objects=[ObjectDetection((0,0,10,10), 0.9, "person", 10, 10)]
    )
    video = VideoAnalysis(
        video_info=None, frames_analyzed=10, faces_detected=10, 
        average_faces_per_frame=1.0, average_processing_time=0.1, 
        frames_with_faces=10, frames_without_faces=0, 
        frames=[frame]*10, objects_detected=1, frames_with_objects=1
    )
    
    result = engine.process(video, None, None)
    assert result.score == 0.0
    assert result.risk_level == RiskLevel.LOW

def test_text_only_high_risk(engine):
    """Testa somente análise textual com risco alto."""
    sentence1 = SentenceAnalysis("texto", 0.0, ["VIOLÊNCIA"], 1, "alto")
    transcript = Transcript("texto", [sentence1])
    text = TextAnalysis(transcript, 0.0)
    
    result = engine.process(None, None, text)
    # VIOLÊNCIA (+30) + risk_level alto (+15) = 45 -> Wait, 45 is MODERATE.
    # We want HIGH risk, so we need > 60. Let's add more.
    sentence2 = SentenceAnalysis("texto2", 0.0, ["AJUDA", "COERÇÃO"], 2, "alto")
    transcript = Transcript("texto texto2", [sentence1, sentence2])
    text = TextAnalysis(transcript, 0.0)
    
    result = engine.process(None, None, text)
    # VIOLÊNCIA (30) + risk_level alto (15) + AJUDA (25) + COERÇÃO (20) = 90
    assert result.score == 90.0
    assert result.risk_level == RiskLevel.HIGH

def test_moderate_risk(engine):
    """Testa risco moderado."""
    sentence = SentenceAnalysis("texto", 0.0, ["MEDO"], 1, "baixo")
    transcript = Transcript("texto", [sentence])
    text = TextAnalysis(transcript, 0.0)
    
    result = engine.process(None, None, text)
    # MEDO (15) -> LOW
    # We need 30 to 59 for MODERATE
    sentence2 = SentenceAnalysis("texto", 0.0, ["AJUDA"], 1, "baixo")
    transcript = Transcript("texto", [sentence, sentence2])
    text = TextAnalysis(transcript, 0.0)
    
    result = engine.process(None, None, text)
    # MEDO (15) + AJUDA (25) = 40 -> MODERATE
    assert result.score == 40.0
    assert result.risk_level == RiskLevel.MEDIUM

def test_multiple_modalities(engine):
    """Testa evidências em múltiplas modalidades gerando pontuação extra."""
    # Text: MEDO (15)
    sentence = SentenceAnalysis("texto", 0.0, ["MEDO"], 1, "baixo")
    text = TextAnalysis(Transcript("texto", [sentence]), 0.0)
    
    # Video: defensive_posture (20)
    frame = FrameAnalysis(
        FrameInfo(1, 0.0),
        [FaceDetection((0,0,10,10), 0.9, 10, 10)],
        [ObjectDetection((0,0,10,10), 0.9, "defensive_posture", 10, 10)]
    )
    video = VideoAnalysis(
        video_info=None, frames_analyzed=1, faces_detected=1, 
        average_faces_per_frame=1.0, average_processing_time=0.1, 
        frames_with_faces=1, frames_without_faces=0, 
        frames=[frame], objects_detected=1, frames_with_objects=1
    )
    
    result = engine.process(video, None, text)
    # MEDO (15) + defensive_posture (20) + MULTIMODAL (10) = 45 -> MODERATE
    assert result.score == 45.0
    assert result.risk_level == RiskLevel.MEDIUM

def test_deduplication(engine):
    """Testa deduplicação de categorias textuais e classes YOLO."""
    # Text: MEDO repetido em duas sentenças
    sentence1 = SentenceAnalysis("texto", 0.0, ["MEDO"], 1, "baixo")
    sentence2 = SentenceAnalysis("texto2", 0.0, ["MEDO"], 1, "baixo")
    text = TextAnalysis(Transcript("texto texto2", [sentence1, sentence2]), 0.0)
    
    # Video: hand_on_face repetido em dois frames
    frame1 = FrameAnalysis(
        FrameInfo(1, 0.0),
        [FaceDetection((0,0,10,10), 0.9, 10, 10)],
        [ObjectDetection((0,0,10,10), 0.9, "hand_on_face", 10, 10)]
    )
    frame2 = FrameAnalysis(
        FrameInfo(2, 0.0),
        [FaceDetection((0,0,10,10), 0.9, 10, 10)],
        [ObjectDetection((0,0,10,10), 0.9, "hand_on_face", 10, 10)]
    )
    video = VideoAnalysis(
        video_info=None, frames_analyzed=2, faces_detected=2, 
        average_faces_per_frame=1.0, average_processing_time=0.1, 
        frames_with_faces=2, frames_without_faces=0, 
        frames=[frame1, frame2], objects_detected=2, frames_with_objects=2
    )
    
    result = engine.process(video, None, text)
    # MEDO (15, pontuado apenas 1x) + hand_on_face (10, pontuado apenas 1x) + MULTIMODAL (10) = 35
    assert result.score == 35.0

def test_max_score_limit(engine):
    """Testa limite máximo de 100 no score."""
    sentence1 = SentenceAnalysis("texto", 0.0, ["VIOLÊNCIA", "AJUDA", "COERÇÃO", "MEDO"], 1, "alto")
    text = TextAnalysis(Transcript("texto", [sentence1]), 0.0)
    
    frame = FrameAnalysis(
        FrameInfo(1, 0.0),
        [],
        [ObjectDetection((0,0,10,10), 0.9, "defensive_posture", 10, 10),
         ObjectDetection((0,0,10,10), 0.9, "hand_on_face", 10, 10)]
    )
    # 100% sem rosto (+5)
    video = VideoAnalysis(
        video_info=None, frames_analyzed=1, faces_detected=0, 
        average_faces_per_frame=0.0, average_processing_time=0.1, 
        frames_with_faces=0, frames_without_faces=1, 
        frames=[frame], objects_detected=2, frames_with_objects=1
    )
    
    result = engine.process(video, None, text)
    # VIOLÊNCIA (30) + AJUDA (25) + COERÇÃO (20) + MEDO (15) + HIGH (15) + NO_FACE (5) + DEFENSIVE (20) + HAND (10) + MULTI (10) = 150
    # Deve ser limitado a 100
    assert result.score == 100.0

def test_serialization(engine):
    """Testa serialização e desserialização do FusionResult."""
    sentence = SentenceAnalysis("texto", 0.0, ["MEDO"], 1, "baixo")
    text = TextAnalysis(Transcript("texto", [sentence]), 0.0)
    
    result = engine.process(None, None, text)
    
    result_dict = result.to_dict()
    assert "score" in result_dict
    assert "timestamp" in result_dict
    
    restored = FusionResult.from_dict(result_dict)
    assert restored.score == result.score
    assert restored.risk_level == result.risk_level
    assert restored.timestamp == result.timestamp
    assert len(restored.evidences) == len(result.evidences)
