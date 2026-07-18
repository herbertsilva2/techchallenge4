import pytest
from src.domain.video_models import VideoInfo, FaceDetection, FrameInfo, FrameAnalysis, VideoAnalysis
from src.domain.audio_models import AudioInfo, SpeechSegment, AudioAnalysis
from src.domain.text_models import SentenceAnalysis, Transcript, TextAnalysis
from src.domain.fusion_models import Evidence, RiskLevel, FusionResult
from src.domain.processing_models import ProcessingStep, ExecutionTime, PipelineResult

def test_video_info_serialization():
    v1 = VideoInfo(width=1920, height=1080, fps=30.0, frame_count=300, duration_seconds=10.0, codec="mp4v")
    data = v1.to_dict()
    assert data['width'] == 1920
    assert data['codec'] == "mp4v"
    
    v2 = VideoInfo.from_dict(data)
    assert v1 == v2

def test_face_detection_serialization():
    f1 = FaceDetection(bbox=(10, 20, 100, 100), confidence=0.95, width=100, height=100)
    data = f1.to_dict()
    assert data['confidence'] == 0.95
    assert data['bbox'] == (10, 20, 100, 100)
    
    # Simulate JSON list for tuple
    data['bbox'] = [10, 20, 100, 100]
    f2 = FaceDetection.from_dict(data)
    assert f1 == f2

def test_video_analysis_serialization():
    v_info = VideoInfo(width=1280, height=720, fps=24.0, frame_count=240, duration_seconds=10.0, codec="avc1")
    f_det = FaceDetection(bbox=(0, 0, 50, 50), confidence=0.9, width=50, height=50)
    f_info = FrameInfo(frame_number=1, timestamp=0.04)
    f_analysis = FrameAnalysis(frame_info=f_info, faces=[f_det])
    
    analysis = VideoAnalysis(
        video_info=v_info,
        frames_analyzed=1,
        faces_detected=1,
        average_faces_per_frame=1.0,
        average_processing_time=0.1,
        frames_with_faces=1,
        frames_without_faces=0,
        frames=[f_analysis]
    )
    
    data = analysis.to_dict()
    assert data['video_info']['width'] == 1280
    assert data['frames'][0]['faces'][0]['confidence'] == 0.9
    
    # Since from_dict converts lists to tuples for bbox
    data['frames'][0]['faces'][0]['bbox'] = [0, 0, 50, 50]
    
    analysis2 = VideoAnalysis.from_dict(data)
    assert analysis == analysis2

def test_audio_models_serialization():
    a_info = AudioInfo(sample_rate=16000, channels=1, duration_seconds=5.0)
    seg = SpeechSegment(start_time=0.0, end_time=2.0, text="Olá")
    a_analysis = AudioAnalysis(audio_info=a_info, segments=[seg])
    
    data = a_analysis.to_dict()
    assert data['audio_info']['sample_rate'] == 16000
    assert len(data['segments']) == 1
    
    a_analysis2 = AudioAnalysis.from_dict(data)
    assert a_analysis == a_analysis2

def test_text_models_serialization():
    sent = SentenceAnalysis(text="Estou triste", sentiment_score=-0.8)
    trans = Transcript(full_text="Estou triste", sentences=[sent])
    t_analysis = TextAnalysis(transcript=trans, overall_sentiment=-0.8)
    
    data = t_analysis.to_dict()
    assert data['transcript']['sentences'][0]['sentiment_score'] == -0.8
    
    t_analysis2 = TextAnalysis.from_dict(data)
    assert t_analysis == t_analysis2

def test_fusion_models_serialization():
    ev = Evidence(modality="TEXT", description="Sentiment score is low", confidence=0.9)
    result = FusionResult(risk_level=RiskLevel.HIGH, evidences=[ev])
    
    data = result.to_dict()
    assert data['risk_level'] == "HIGH"
    
    result2 = FusionResult.from_dict(data)
    assert result == result2
    assert result2.risk_level == RiskLevel.HIGH

def test_processing_models_serialization():
    t1 = ExecutionTime(step=ProcessingStep.VIDEO_EXTRACTION, duration_seconds=1.5)
    t2 = ExecutionTime(step=ProcessingStep.FUSION, duration_seconds=0.1)
    
    ev = Evidence(modality="TEXT", description="test", confidence=0.5)
    f_res = FusionResult(risk_level=RiskLevel.LOW, evidences=[ev])
    
    pipe = PipelineResult(
        execution_times=[t1, t2],
        fusion_result=f_res
    )
    
    data = pipe.to_dict()
    assert len(data['execution_times']) == 2
    assert data['execution_times'][0]['step'] == "VIDEO_EXTRACTION"
    assert data['fusion_result']['risk_level'] == "LOW"
    assert data['video_analysis'] is None
    
    pipe2 = PipelineResult.from_dict(data)
    assert pipe == pipe2
    assert pipe2.execution_times[0].step == ProcessingStep.VIDEO_EXTRACTION
