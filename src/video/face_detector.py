import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
from typing import List, Tuple
from pathlib import Path
from src.domain.video_models import FaceDetection

class FaceDetector:
    def __init__(self, min_detection_confidence: float = 0.5):
        # Usando a Tasks API mais moderna do MediaPipe
        model_path = Path("models/blaze_face_short_range.tflite")
        if not model_path.exists():
            raise FileNotFoundError(f"Modelo não encontrado em: {model_path}")
            
        base_options = python.BaseOptions(model_asset_path=str(model_path))
        options = vision.FaceDetectorOptions(
            base_options=base_options,
            min_detection_confidence=min_detection_confidence
        )
        self.detector = vision.FaceDetector.create_from_options(options)

    def detect(self, frame: np.ndarray) -> List[FaceDetection]:
        # MediaPipe requires RGB images
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        
        results = self.detector.detect(mp_image)

        detections = []
        for detection in results.detections:
            bbox = detection.bounding_box
            x = int(bbox.origin_x)
            y = int(bbox.origin_y)
            width = int(bbox.width)
            height = int(bbox.height)
            confidence = float(detection.categories[0].score)

            detections.append(FaceDetection(
                bbox=(x, y, width, height),
                confidence=confidence,
                width=width,
                height=height
            ))
        return detections

    def annotate_frame(self, frame: np.ndarray, detections: List[FaceDetection]) -> np.ndarray:
        annotated_frame = frame.copy()
        for det in detections:
            x, y, w, h = det.bbox
            # Desenha a bounding box
            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # Desenha a confidence
            text = f"{det.confidence:.2f}"
            cv2.putText(annotated_frame, text, (x, max(10, y - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return annotated_frame
