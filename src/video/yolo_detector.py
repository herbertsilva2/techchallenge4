import cv2
import numpy as np
from typing import List
from pathlib import Path
from ultralytics import YOLO

from src.domain.video_models import ObjectDetection
from src.video.hand_on_face_detector import HandOnFaceDetector

class YOLODetector:
    def __init__(self, model_path: str = "models/yolo/best.pt", min_confidence: float = 0.25):
        self.model_path = Path(model_path)
        self.min_confidence = min_confidence
        
        # Sem peso customizado, usa detector pré-treinado de gesto em vez de
        # YOLO COCO genérico, que não possui a classe hand_on_face.
        self.is_demo_mode = not self.model_path.exists()
        if self.is_demo_mode:
            print(f"Modelo {self.model_path} não encontrado. Usando MediaPipe Hands + Face Mesh.")
            self.model_used = "MediaPipe Hands + Face Mesh"
            self.model = HandOnFaceDetector()
        else:
            self.model_used = str(self.model_path)
            self.model = YOLO(self.model_used)

    def get_info(self) -> dict:
        info = {
            'model_mode': 'pretrained_gesture' if self.is_demo_mode else 'custom',
            'model_used': self.model_used,
            'custom_model_trained': not self.is_demo_mode
        }
        if self.is_demo_mode:
            info.update(self.model.get_info())
        return info

    def detect(self, frame: np.ndarray) -> List[ObjectDetection]:
        if self.is_demo_mode:
            return self.model.detect(frame)

        # YOLOv8 aceita BGR do OpenCV diretamente
        results = self.model(frame, verbose=False)
        detections = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                confidence = float(box.conf[0])
                if confidence >= self.min_confidence:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    width = int(x2 - x1)
                    height = int(y2 - y1)
                    class_id = int(box.cls[0])
                    class_name = self.model.names[class_id]
                    
                    detections.append(ObjectDetection(
                        bbox=(int(x1), int(y1), width, height),
                        confidence=confidence,
                        class_name=class_name,
                        width=width,
                        height=height
                    ))
                    
        return detections

    def annotate_frame(self, frame: np.ndarray, detections: List[ObjectDetection]) -> np.ndarray:
        annotated_frame = frame.copy()
        for det in detections:
            x, y, w, h = det.bbox
            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            label = f"{det.class_name}: {det.confidence:.2f}"
            cv2.putText(annotated_frame, label, (x, max(10, y - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        return annotated_frame
