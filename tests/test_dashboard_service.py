import pytest
import os
from unittest.mock import patch, MagicMock
from src.services.dashboard_service import DashboardService, MAX_UPLOAD_SIZE_BYTES
from src.domain.processing_models import PipelineResult

@pytest.fixture
def dashboard_service():
    return DashboardService()

def test_validate_upload_allowed_extension(dashboard_service):
    is_valid, err = dashboard_service.validate_upload("video.mp4", 1000)
    assert is_valid is True
    assert err is None

def test_validate_upload_invalid_extension(dashboard_service):
    is_valid, err = dashboard_service.validate_upload("video.gif", 1000)
    assert is_valid is False
    assert "Extensão não permitida" in err

def test_validate_upload_size_limit(dashboard_service):
    is_valid, err = dashboard_service.validate_upload("video.mp4", MAX_UPLOAD_SIZE_BYTES + 1)
    assert is_valid is False
    assert "excede o limite" in err

def test_process_upload_flow(dashboard_service):
    mock_pipeline = MagicMock()
    mock_pipeline.execute.return_value = PipelineResult()
    dashboard_service.pipeline_service = mock_pipeline
    
    # Run process_upload
    result = dashboard_service.process_upload(b"testbytes", ".mp4", lambda s,p,m: None)
    
    assert isinstance(result, PipelineResult)
    mock_pipeline.execute.assert_called_once()
    
    # Assert temp file name is random and not just .mp4
    called_path = mock_pipeline.execute.call_args[0][0]
    assert called_path.name != ".mp4"
    assert called_path.suffix == ".mp4"
    
    # Assert temp file is removed after function returns
    assert not called_path.exists()

def test_load_generated_results(dashboard_service):
    mock_loader = MagicMock()
    mock_loader.load_report.return_value = {"status": "ok"}
    mock_loader.load_markdown.return_value = "# Report"
    dashboard_service.result_loader = mock_loader
    
    result = PipelineResult(report_json_path="fake.json", report_md_path="fake.md")
    
    report_data, report_md = dashboard_service.load_generated_results(result)
    
    assert report_data == {"status": "ok"}
    assert report_md == "# Report"
