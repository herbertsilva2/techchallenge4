"""Detecção pré-treinada de aproximação mão-rosto para apoio à triagem.

O detector combina MediaPipe Hand Landmarker e o FaceDetector existente.
Ele identifica proximidade geométrica em imagem 2D; não infere diagnóstico,
violência ou estado emocional.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from src.domain.video_models import ObjectDetection
from src.video.face_detector import FaceDetector


class HandOnFaceDetector:
    """Produz `hand_on_face` após contato/proximidade persistente em dois frames."""

    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        required_consecutive_frames: int = 2,
        face_margin_ratio: float = 0.08,
    ):
        self.required_consecutive_frames = required_consecutive_frames
        self.face_margin_ratio = face_margin_ratio
        self._positive_streak = 0
        project_root = Path(__file__).resolve().parent.parent.parent
        model_path = project_root / "models" / "hand_landmarker.task"
        if not model_path.exists():
            raise FileNotFoundError(
                f"Modelo Hand Landmarker não encontrado: {model_path}. "
                "Baixe o modelo oficial antes de executar o pipeline."
            )

        base_options = python.BaseOptions(model_asset_path=str(model_path))
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_hands=2,
            min_hand_detection_confidence=min_detection_confidence,
            min_hand_presence_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self._hands = vision.HandLandmarker.create_from_options(options)
        self._face_detector = FaceDetector(min_detection_confidence=min_detection_confidence)

    def get_info(self) -> dict:
        return {
            "model_mode": "pretrained_gesture",
            "model_used": "MediaPipe Hand Landmarker + Face Detector",
            "custom_model_trained": False,
            "specialized_gesture_detector": True,
            "limitation": "Proximidade mão-rosto em 2D; requer revisão humana.",
        }

    def detect(self, frame: np.ndarray) -> List[ObjectDetection]:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        hands_result = self._hands.detect(mp_image)
        face_detections = self._face_detector.detect(frame)

        if not hands_result.hand_landmarks or not face_detections:
            self._positive_streak = 0
            return []

        height, width = frame.shape[:2]
        face_boxes = [face.bbox for face in face_detections]
        hand_boxes = []
        for hand in hands_result.hand_landmarks:
            # HandLandmarker retorna List[NormalizedLandmark] para cada mão;
            # diferentemente da API Solutions legada, não há atributo .landmark.
            hand_points = [(point.x * width, point.y * height) for point in hand]
            if self._touches_face(hand_points, face_boxes):
                hand_boxes.append(self._bounding_box(hand_points, width, height))

        if not hand_boxes:
            self._positive_streak = 0
            return []

        self._positive_streak += 1
        if self._positive_streak < self.required_consecutive_frames:
            return []

        confidence = min(0.95, 0.60 + 0.10 * self._positive_streak)
        return [
            ObjectDetection(
                bbox=box,
                confidence=confidence,
                class_name="hand_on_face",
                width=box[2],
                height=box[3],
            )
            for box in hand_boxes
        ]

    def close(self) -> None:
        self._hands.close()
        self._face_detector.close()

    def _touches_face(
        self, hand_points: List[Tuple[float, float]], face_boxes: List[Tuple[int, int, int, int]]
    ) -> bool:
        # Pontas dos dedos, juntas intermediárias e centro da palma são os pontos
        # mais úteis para aproximar contato sem rotular braço ou pessoa inteira.
        contact_indices = (0, 4, 8, 12, 16, 20)
        for x, y in (hand_points[index] for index in contact_indices):
            for face_x, face_y, face_w, face_h in face_boxes:
                margin = max(face_w, face_h) * self.face_margin_ratio
                if face_x - margin <= x <= face_x + face_w + margin and face_y - margin <= y <= face_y + face_h + margin:
                    return True
        return False

    @staticmethod
    def _bounding_box(points: List[Tuple[float, float]], width: int, height: int) -> Tuple[int, int, int, int]:
        xs, ys = zip(*points)
        x1, y1 = max(0, int(min(xs))), max(0, int(min(ys)))
        x2, y2 = min(width, int(max(xs))), min(height, int(max(ys)))
        return x1, y1, max(1, x2 - x1), max(1, y2 - y1)
