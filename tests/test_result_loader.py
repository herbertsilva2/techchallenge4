import pytest
from pathlib import Path
import json
import tempfile
from src.services.result_loader import ResultLoader, ReportLoadError, InvalidReportError

def test_loader_missing_json():
    loader = ResultLoader()
    with pytest.raises(ReportLoadError, match="Report file not found"):
        loader.load_report("non_existent_report.json")

def test_loader_invalid_json():
    loader = ResultLoader()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{invalid json")
        temp_path = f.name
        
    try:
        with pytest.raises(InvalidReportError, match="Failed to parse JSON"):
            loader.load_report(temp_path)
    finally:
        Path(temp_path).unlink()

def test_loader_missing_required_fields():
    loader = ResultLoader()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"timestamp": "2023-01-01"}, f) # Missing modalities, fusion_result, ethical_warning
        temp_path = f.name
        
    try:
        with pytest.raises(InvalidReportError, match="Missing required field in report: modalities"):
            loader.load_report(temp_path)
    finally:
        Path(temp_path).unlink()

def test_loader_missing_md():
    loader = ResultLoader()
    with pytest.raises(ReportLoadError, match="Markdown report not found"):
        loader.load_markdown("non_existent_report.md")

def test_loader_utf8_reading():
    loader = ResultLoader()
    content = {"timestamp": "2023-01-01", "modalities": {}, "fusion_result": {}, "ethical_warning": "Atenção: Ação requerida."}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', encoding='utf-8', delete=False) as f:
        json.dump(content, f, ensure_ascii=False)
        temp_path = f.name
        
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', encoding='utf-8', delete=False) as f_md:
        f_md.write("# Relatório com acentuação: Áéîõü")
        temp_md_path = f_md.name
        
    try:
        data = loader.load_report(temp_path)
        assert data['ethical_warning'] == "Atenção: Ação requerida."
        
        md_text = loader.load_markdown(temp_md_path)
        assert md_text == "# Relatório com acentuação: Áéîõü"
    finally:
        Path(temp_path).unlink()
        Path(temp_md_path).unlink()

def test_loader_does_not_recalculate_scores():
    loader = ResultLoader()
    original_data = {
        "timestamp": "2023-01-01", 
        "modalities": {}, 
        "fusion_result": {"score": 42.5, "risk_level": "moderate"}, 
        "ethical_warning": "ATENÇÃO"
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(original_data, f)
        temp_path = f.name
        
    try:
        data = loader.load_report(temp_path)
        assert data["fusion_result"]["score"] == 42.5
        assert data == original_data # Must be exactly the same dict, nothing altered
    finally:
        Path(temp_path).unlink()
