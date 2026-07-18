import cv2
import json
import time
from pathlib import Path
from src.video.yolo_detector import YOLODetector
from src.domain.video_models import VideoAnalysis, FrameAnalysis, FrameInfo

class YoloService:
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.detector = YOLODetector()

    def analyze_frames(self) -> VideoAnalysis | None:
        frames_dir = self.input_dir / "frames"
        annotated_dir = self.output_dir / "annotated_frames"
        annotated_dir.mkdir(parents=True, exist_ok=True)

        summary_path = self.output_dir / "detections.json"

        total_frames = 0
        frames_com_objetos = 0
        frames_sem_objetos = 0
        total_objetos_detectados = 0

        if not frames_dir.exists():
            return None

        frames_analysis = []
        start_time = time.time()
        
        for frame_path in sorted(frames_dir.glob("*.jpg")):
            total_frames += 1
            frame = cv2.imread(str(frame_path))
            if frame is None:
                continue

            detections = self.detector.detect(frame)

            if len(detections) > 0:
                frames_com_objetos += 1
                total_objetos_detectados += len(detections)
                annotated_frame = self.detector.annotate_frame(frame, detections)
            else:
                frames_sem_objetos += 1
                annotated_frame = frame.copy()

            cv2.imwrite(str(annotated_dir / frame_path.name), annotated_frame)

            frame_info = FrameInfo(frame_number=total_frames, timestamp=0.0)
            frames_analysis.append(FrameAnalysis(
                frame_info=frame_info,
                faces=[],
                objects=detections
            ))

        end_time = time.time()
        tempo_medio = (end_time - start_time) / total_frames if total_frames > 0 else 0
        
        analysis = VideoAnalysis(
            video_info=None,
            frames_analyzed=total_frames,
            faces_detected=0,
            average_faces_per_frame=0.0,
            average_processing_time=tempo_medio,
            frames_with_faces=0,
            frames_without_faces=total_frames,
            objects_detected=total_objetos_detectados,
            frames_with_objects=frames_com_objetos,
            frames=frames_analysis
        )

        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(analysis.to_dict(), f, indent=4, ensure_ascii=False)

        return analysis
