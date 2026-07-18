import pytest
import numpy as np
from src.video.face_detector import FaceDetector, FaceDetection

def test_face_detector_initialization():
    detector = FaceDetector()
    assert detector is not None
    assert detector.detector is not None

def test_annotate_frame_returns_valid_image():
    detector = FaceDetector()
    # Criar uma imagem preta 100x100
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    detections = [
        FaceDetection(bbox=(10, 10, 20, 20), confidence=0.95, width=20, height=20)
    ]
    annotated = detector.annotate_frame(frame, detections)
    
    assert annotated is not None
    assert annotated.shape == (100, 100, 3)
    # A imagem deve ter sido modificada (desenhou um retângulo verde)
    # Verificar se há algum pixel verde
    # O retângulo é desenhado em verde: (0, 255, 0)
    assert np.any(annotated[:, :, 1] > 0) # Canal G tem valores maiores que 0

def test_detection_on_empty_image_does_not_raise_exception():
    detector = FaceDetector()
    # Criar uma imagem preta 100x100
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    
    # Executar detecção não deve lançar exceção
    try:
        detections = detector.detect(frame)
        assert isinstance(detections, list)
        assert len(detections) == 0 # Nenhuma face em imagem preta
    except Exception as e:
        pytest.fail(f"A detecção lançou uma exceção inesperada: {e}")
