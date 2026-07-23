from unittest.mock import MagicMock, patch

import cv2
import numpy as np

from src.domain.video_models import ObjectDetection
from src.video.frame_analyzer import FrameAnalyzer


def _sharp(confidence):
    return ObjectDetection(
        bbox=(10, 10, 20, 20), confidence=confidence, class_name="sharp_object", width=20, height=20,
    )


def test_sharp_object_requires_two_candidates_in_three_frames(tmp_path):
    frames_dir = tmp_path / "frames"
    frames_dir.mkdir()
    for index in range(3):
        cv2.imwrite(str(frames_dir / f"frame_{index:06d}.jpg"), np.zeros((40, 40, 3), dtype=np.uint8))

    detector = MagicMock()
    detector.detect.side_effect = [[_sharp(0.129)], [_sharp(0.103)], []]
    detector.annotate_frame.side_effect = lambda frame, _: frame

    with patch("src.video.frame_analyzer.FaceDetector") as face_detector:
        face_detector.return_value.detect.return_value = []
        analysis = FrameAnalyzer(str(tmp_path), str(tmp_path), yolo_detector=detector).analyze_frames()

    assert analysis.sharp_object_candidate_frames == 2
    assert analysis.confirmed_sharp_object_frames == 1
    assert analysis.max_sharp_object_confidence == 0.129
    assert analysis.objects_detected == 1
    assert analysis.frames[0].objects == []
    assert analysis.frames[1].objects[0].class_name == "sharp_object"


def test_isolated_sharp_object_candidate_does_not_become_evidence(tmp_path):
    frames_dir = tmp_path / "frames"
    frames_dir.mkdir()
    for index in range(3):
        cv2.imwrite(str(frames_dir / f"frame_{index:06d}.jpg"), np.zeros((40, 40, 3), dtype=np.uint8))

    detector = MagicMock()
    detector.detect.side_effect = [[_sharp(0.129)], [], []]
    detector.annotate_frame.side_effect = lambda frame, _: frame

    with patch("src.video.frame_analyzer.FaceDetector") as face_detector:
        face_detector.return_value.detect.return_value = []
        analysis = FrameAnalyzer(str(tmp_path), str(tmp_path), yolo_detector=detector).analyze_frames()

    assert analysis.sharp_object_candidate_frames == 1
    assert analysis.confirmed_sharp_object_frames == 0
    assert analysis.objects_detected == 0
