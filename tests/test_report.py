import pytest
import json
from pathlib import Path
from src.domain.report_models import ReportData, ModalityStatus
from src.domain.video_models import VideoInfo
from src.domain.fusion_models import FusionResult, RiskLevel, Evidence
from src.report.report_generator import ReportGenerator
from src.report.report_service import ReportService
from src.fusion.risk_rules import RiskRules

@pytest.fixture
def sample_report_data():
    return ReportData(
        timestamp="2026-07-15T00:00:00Z",
        video_info=VideoInfo(width=1920, height=1080, fps=30.0, frame_count=100, duration_seconds=3.33, codec="h264"),
        modalities={
            "video": ModalityStatus("completed", details={"frames_analyzed": 100}),
            "yolo": ModalityStatus("partial", reason="Modelo customizado não encontrado", details={"model_mode": "demo", "model_used": "yolov8n.pt", "custom_model_trained": False}),
            "audio": ModalityStatus("unavailable", reason="O vídeo processado não possui faixa de áudio.")
        },
        fusion_result=FusionResult(risk_level=RiskLevel.LOW, evidences=[], score=0.0, recommendations=["Teste Sem Evidencia"]),
        ethical_warning="AVISO ÉTICO TESTE"
    )

def test_report_generator_creates_files(tmp_path, sample_report_data):
    gen = ReportGenerator(str(tmp_path))
    json_path, md_path = gen.generate(sample_report_data)
    
    assert json_path.exists()
    assert md_path.exists()

def test_report_service_dependency_injection(tmp_path, sample_report_data):
    gen = ReportGenerator(str(tmp_path))
    service = ReportService(gen)
    json_path, md_path = service.execute(sample_report_data)
    
    assert json_path.exists()
    assert md_path.exists()

def test_json_serialization_and_reasons(tmp_path, sample_report_data):
    gen = ReportGenerator(str(tmp_path))
    json_path, _ = gen.generate(sample_report_data)
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    assert data["timestamp"] == "2026-07-15T00:00:00Z"
    assert data["ethical_warning"] == "AVISO ÉTICO TESTE"
    assert data["modalities"]["video"]["status"] == "completed"
    assert "reason" not in data["modalities"]["video"]
    assert data["modalities"]["yolo"]["status"] == "partial"
    assert data["modalities"]["yolo"]["reason"] == "Modelo customizado não encontrado"
    assert data["modalities"]["yolo"]["model_mode"] == "demo"
    
    # Check invalid python objects are not serialized
    # If the json dump works without errors, it's valid JSON

def test_markdown_ethical_warning_and_status(tmp_path, sample_report_data):
    gen = ReportGenerator(str(tmp_path))
    _, md_path = gen.generate(sample_report_data)
    
    content = md_path.read_text(encoding='utf-8')
    assert "## Aviso Ético" in content
    assert "> AVISO ÉTICO TESTE" in content
    assert "### YOLO" in content
    assert "- **Status:** partial" in content
    assert "- **Motivo:** Modelo customizado não encontrado" in content

def test_low_recommendations_with_evidence():
    recs = RiskRules.get_recommendations(RiskLevel.LOW, has_evidences=True)
    assert any("Sinais pontuais" in r for r in recs)

def test_low_recommendations_without_evidence():
    recs = RiskRules.get_recommendations(RiskLevel.LOW, has_evidences=False)
    assert any("Nenhum sinal relevante" in r for r in recs)
