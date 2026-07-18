import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.services.pipeline_service import PipelineService
from src.domain.processing_models import ProcessingStep, PipelineResult
from src.domain.video_models import VideoInfo
from src.domain.fusion_models import FusionResult, RiskLevel

@pytest.fixture
def mock_dependencies():
    with patch('src.services.pipeline_service.VideoLoader') as mock_vl, \
         patch('src.services.pipeline_service.VideoMetadata') as mock_vm, \
         patch('src.services.pipeline_service.FrameExtractor') as mock_fe, \
         patch('src.services.pipeline_service.AudioExtractor') as mock_ae, \
         patch('src.services.pipeline_service.YOLODetector') as mock_yd, \
         patch('src.services.pipeline_service.FrameAnalyzer') as mock_fa, \
         patch('src.services.pipeline_service.AzureSpeechTranscriber') as mock_ast, \
         patch('src.services.pipeline_service.TranscriptionService') as mock_ts, \
         patch('src.services.pipeline_service.TextAnalysisService') as mock_tas, \
         patch('src.services.pipeline_service.FusionEngine') as mock_fe_eng, \
         patch('src.services.pipeline_service.FusionService') as mock_fs, \
         patch('src.services.pipeline_service.ReportGenerator') as mock_rg, \
         patch('src.services.pipeline_service.ReportService') as mock_rs, \
         patch('src.services.pipeline_service.AZURE_SPEECH_KEY', 'dummy_key'), \
         patch('src.services.pipeline_service.AZURE_SPEECH_REGION', 'dummy_region'):
        
        # Mocks setup
        mock_vl.return_value.validate.return_value = Path("test.mp4")
        mock_vm.get_metadata.return_value = MagicMock(width=1920, height=1080, fps=30.0, frame_count=300, duration_seconds=10.0, codec="h264")
        mock_ae.return_value.extract_audio.return_value = "test.wav"
        
        mock_yd.return_value.get_info.return_value = {'custom_model_trained': True, 'model': 'best.pt'}
        
        mock_fa.return_value.analyze_frames.return_value = MagicMock(frames_analyzed=10, faces_detected=5, objects_detected=2)
        
        mock_ts.return_value.execute.return_value = {"status": "concluída", "idioma": "pt-BR", "segmentos": [], "transcript_modelo": {"full_text": "teste", "sentences": []}}
        mock_tas.return_value.execute.return_value = {"status": "concluída", "analise": {"transcript": {"full_text": "teste", "sentences": []}, "overall_sentiment": 0.5}}
        
        mock_fs.return_value.execute.return_value = FusionResult(score=0.8, risk_level=RiskLevel.MEDIUM, evidences=[])
        mock_rs.return_value.execute.return_value = ("report.json", "report.md")
        
        yield {
            'vl': mock_vl, 'vm': mock_vm, 'fe': mock_fe, 'ae': mock_ae, 'yd': mock_yd,
            'fa': mock_fa, 'ast': mock_ast, 'ts': mock_ts, 'tas': mock_tas,
            'fe_eng': mock_fe_eng, 'fs': mock_fs, 'rg': mock_rg, 'rs': mock_rs
        }

def test_pipeline_complete_result(mock_dependencies):
    service = PipelineService()
    callbacks = []
    def callback(step, prog, msg):
        callbacks.append(prog)
        
    result = service.execute(Path("test.mp4"), callback)
    
    assert result.status == "completed"
    assert result.video_info is not None
    assert result.fusion_result is not None
    assert result.report_json_path == "report.json"
    assert result.report_md_path == "report.md"
    assert len(callbacks) > 0
    assert callbacks[0] == 0.0
    assert callbacks[-1] == 1.0

def test_pipeline_callback_exception(mock_dependencies):
    service = PipelineService()
    
    def callback(step, prog, msg):
        raise ValueError("Callback falhou")
        
    result = service.execute(Path("test.mp4"), callback)
    
    # Exceção no callback não deve interromper o pipeline
    assert result.status == "completed"
    assert any("Callback error:" in m for m in result.messages)

@patch('src.services.pipeline_service.AZURE_SPEECH_KEY', None)
def test_pipeline_partial_without_azure(mock_dependencies):
    service = PipelineService()
    result = service.execute(Path("test.mp4"))
    
    assert result.status == "partial"

def test_pipeline_yolo_demo(mock_dependencies):
    mock_dependencies['yd'].return_value.get_info.return_value = {'custom_model_trained': False, 'model': 'yolov8n.pt'}
    service = PipelineService()
    result = service.execute(Path("test.mp4"))
    assert result.status == "partial"

def test_pipeline_critical_error(mock_dependencies):
    mock_dependencies['vl'].return_value.validate.side_effect = Exception("Erro Fatal")
    service = PipelineService()
    result = service.execute(Path("test.mp4"))
    assert result.status == "failed"
    assert "Erro Fatal" in result.errors[0]

def test_pipeline_custom_output_dir(mock_dependencies, tmp_path):
    service = PipelineService()
    result = service.execute(Path("test.mp4"), output_dir=tmp_path)
    assert result.status == "completed"
