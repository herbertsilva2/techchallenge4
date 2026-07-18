import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from src.video.yolo_detector import YOLODetector

@pytest.fixture
def mock_yolo():
    with patch('src.video.yolo_detector.YOLO') as mock:
        # Configurar o mock para retornar um resultado simulado
        mock_result = MagicMock()
        mock_box = MagicMock()
        mock_box.conf = [0.8]
        mock_xyxy = MagicMock()
        mock_xyxy.tolist.return_value = [10.0, 20.0, 110.0, 120.0]
        mock_box.xyxy = [mock_xyxy]
        mock_box.cls = [0]
        mock_result.boxes = [mock_box]
        
        mock_instance = mock.return_value
        mock_instance.return_value = [mock_result]
        mock_instance.names = {0: "hand_on_face", 1: "defensive_posture"}
        
        yield mock

def test_yolo_detector_init_demo_mode(mock_yolo, tmp_path):
    # Passando um caminho que não existe para forçar MODO DEMO
    detector = YOLODetector(model_path=str(tmp_path / "nao_existe.pt"))
    mock_yolo.assert_called_with('yolov8n.pt')

def test_yolo_detector_init_best_model(mock_yolo, tmp_path):
    # Criando um arquivo best.pt falso
    model_path = tmp_path / "best.pt"
    model_path.touch()
    
    detector = YOLODetector(model_path=str(model_path))
    mock_yolo.assert_called_with(str(model_path))

def test_yolo_detector_detect(mock_yolo):
    detector = YOLODetector(model_path="dummy_path_to_trigger_demo.pt")
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    detections = detector.detect(frame)
    
    assert len(detections) == 1
    assert detections[0].class_name == "hand_on_face"
    assert detections[0].confidence == 0.8
    assert detections[0].bbox == (10, 20, 100, 100)
