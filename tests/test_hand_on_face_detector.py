from types import SimpleNamespace

import numpy as np

from src.domain.video_models import FaceDetection
from src.video.hand_on_face_detector import HandOnFaceDetector


def test_touching_face_when_a_fingertip_is_inside_expanded_face_box():
    detector = HandOnFaceDetector.__new__(HandOnFaceDetector)
    detector.face_margin_ratio = 0.08
    hand_points = [(0.0, 0.0)] * 21
    hand_points[8] = (55.0, 60.0)

    assert detector._touches_face(hand_points, [(50, 50, 40, 40)]) is True


def test_not_touching_face_when_all_contact_points_are_distant():
    detector = HandOnFaceDetector.__new__(HandOnFaceDetector)
    detector.face_margin_ratio = 0.08
    hand_points = [(5.0, 5.0)] * 21

    assert detector._touches_face(hand_points, [(50, 50, 40, 40)]) is False


def test_detect_reads_hand_landmarker_list_and_confirms_persistent_proximity():
    detector = HandOnFaceDetector.__new__(HandOnFaceDetector)
    detector.face_margin_ratio = 0.08
    detector.required_consecutive_frames = 2
    detector._positive_streak = 0

    landmarks = [SimpleNamespace(x=0.05, y=0.05) for _ in range(21)]
    landmarks[8] = SimpleNamespace(x=0.55, y=0.55)
    detector._hands = SimpleNamespace(
        detect=lambda _: SimpleNamespace(hand_landmarks=[landmarks])
    )
    detector._face_detector = SimpleNamespace(
        detect=lambda _: [FaceDetection(bbox=(50, 50, 40, 40), confidence=0.9, width=40, height=40)]
    )

    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    assert detector.detect(frame) == []

    detections = detector.detect(frame)
    assert len(detections) == 1
    assert detections[0].class_name == "hand_on_face"
