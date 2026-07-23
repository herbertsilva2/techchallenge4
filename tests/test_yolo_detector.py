import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from src.video.yolo_detector import YOLODetector

@pytest.fixture
def mock_detectors():
    with patch('src.video.yolo_detector.YOLO') as mock_yolo, \
         patch('src.video.yolo_detector.HandOnFaceDetector') as mock_hand_on_face:
        # Configurar o mock para retornar um resultado simulado
        mock_result = MagicMock()
        mock_box = MagicMock()
        mock_box.conf = [0.8]
        mock_xyxy = MagicMock()
        mock_xyxy.tolist.return_value = [10.0, 20.0, 110.0, 120.0]
        mock_box.xyxy = [mock_xyxy]
        mock_box.cls = [0]
        mock_result.boxes = [mock_box]
        
        mock_instance = mock_yolo.return_value
        mock_instance.return_value = [mock_result]
        mock_instance.names = {0: "hand_on_face", 1: "defensive_posture"}
        mock_hand_on_face.return_value.get_info.return_value = {
            "specialized_gesture_detector": True,
            "model_mode": "pretrained_gesture",
            "model_used": "MediaPipe Hands + Face Mesh",
        }
        
        yield mock_yolo, mock_hand_on_face

def test_yolo_detector_init_uses_pretrained_gesture_detector_when_custom_model_is_missing(mock_detectors, tmp_path):
    mock_yolo, mock_hand_on_face = mock_detectors
    detector = YOLODetector(model_path=str(tmp_path / "nao_existe.pt"))
    mock_yolo.assert_not_called()
    mock_hand_on_face.assert_called_once()
    assert detector.get_info()['model_mode'] == 'pretrained_gesture'

def test_yolo_detector_init_best_model(mock_detectors, tmp_path):
    mock_yolo, _ = mock_detectors
    # Criando um arquivo best.pt falso
    model_path = tmp_path / "best.pt"
    model_path.touch()
    
    detector = YOLODetector(model_path=str(model_path))
    mock_yolo.assert_called_with(str(model_path))

def test_yolo_detector_detect_with_custom_model(mock_detectors, tmp_path):
    _, _ = mock_detectors
    model_path = tmp_path / "best.pt"
    model_path.touch()
    detector = YOLODetector(model_path=str(model_path))
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    detections = detector.detect(frame)
    
    assert len(detections) == 1
    assert detections[0].class_name == "hand_on_face"
    assert detections[0].confidence == 0.8
    assert detections[0].bbox == (10, 20, 100, 100)

def test_yolo_detector_accepts_lower_threshold_only_for_sharp_object(mock_detectors, tmp_path):
    mock_yolo, _ = mock_detectors
    model_path = tmp_path / "best.pt"
    model_path.touch()
    model = mock_yolo.return_value
    box = model.return_value[0].boxes[0]
    box.conf = [0.129]
    box.cls = [1]
    model.names = {0: "hand_on_face", 1: "sharp_object"}

    detector = YOLODetector(model_path=str(model_path), min_confidence=0.25, sharp_object_min_confidence=0.10)
    detections = detector.detect(np.zeros((480, 640, 3), dtype=np.uint8))

    assert len(detections) == 1
    assert detections[0].class_name == "sharp_object"

    box.cls = [0]
    detections = detector.detect(np.zeros((480, 640, 3), dtype=np.uint8))
    assert detections == []
