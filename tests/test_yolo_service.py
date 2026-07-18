import pytest
from unittest.mock import patch, MagicMock
from src.video.yolo_service import YoloService
from pathlib import Path
import numpy as np
import json

@pytest.fixture
def temp_dirs(tmp_path):
    input_dir = tmp_path / "input"
    frames_dir = input_dir / "frames"
    frames_dir.mkdir(parents=True)
    
    (frames_dir / "frame_0001.jpg").touch()
    (frames_dir / "frame_0002.jpg").touch()
    
    output_dir = tmp_path / "output"
    return str(input_dir), str(output_dir)

@patch('src.video.yolo_service.cv2.imread')
@patch('src.video.yolo_service.cv2.imwrite')
@patch('src.video.yolo_service.YOLODetector')
def test_yolo_service_analyze_frames(mock_detector_class, mock_imwrite, mock_imread, temp_dirs):
    input_dir, output_dir = temp_dirs
    
    mock_imread.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
    
    mock_detector_instance = mock_detector_class.return_value
    
    mock_detection = MagicMock()
    mock_detection.to_dict.return_value = {"mock": "detection"}
    
    mock_detector_instance.detect.return_value = [mock_detection]
    mock_detector_instance.annotate_frame.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
    
    service = YoloService(input_dir=input_dir, output_dir=output_dir)
    analysis = service.analyze_frames()
    
    assert analysis is not None
    assert analysis.frames_analyzed == 2
    assert analysis.objects_detected == 2
    assert analysis.frames_with_objects == 2
    
    assert mock_imwrite.call_count == 2
    
    summary_path = Path(output_dir) / "detections.json"
    assert summary_path.exists()
    
    with open(summary_path) as f:
        data = json.load(f)
        assert data["frames_analyzed"] == 2
        assert data["objects_detected"] == 2
