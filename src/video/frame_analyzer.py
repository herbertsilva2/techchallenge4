import cv2
import json
import time
from pathlib import Path
from src.video.face_detector import FaceDetector
from src.domain.video_models import VideoAnalysis

class FrameAnalyzer:
    def __init__(self, input_dir: str, output_dir: str, yolo_detector=None):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.detector = FaceDetector()
        self.yolo_detector = yolo_detector

    def analyze_frames(self) -> VideoAnalysis | None:
        frames_dir = self.input_dir / "frames"
        annotated_dir = self.output_dir / "annotated_frames"
        annotated_dir.mkdir(parents=True, exist_ok=True)

        summary_path = self.output_dir / "video_analysis_summary.json"
        face_summary_path = self.output_dir / "face_detection_summary.json"
        yolo_dir = self.output_dir / "yolo"
        yolo_dir.mkdir(parents=True, exist_ok=True)
        yolo_summary_path = yolo_dir / "detections.json"

        total_frames = 0
        frames_com_rosto = 0
        frames_sem_rosto = 0
        total_faces_detectadas = 0
        
        frames_com_objetos = 0
        total_objetos_detectados = 0
        
        frames_list = []

        if not frames_dir.exists():
            return None

        if not self.yolo_detector:
            from src.video.yolo_detector import YOLODetector
            self.yolo_detector = YOLODetector()

        start_time = time.time()
        for frame_path in sorted(frames_dir.glob("*.jpg")):
            total_frames += 1
            frame = cv2.imread(str(frame_path))
            if frame is None:
                continue

            face_detections = self.detector.detect(frame)
            object_detections = self.yolo_detector.detect(frame)

            if len(face_detections) > 0:
                frames_com_rosto += 1
                total_faces_detectadas += len(face_detections)
                annotated_frame = self.detector.annotate_frame(frame, face_detections)
            else:
                frames_sem_rosto += 1
                annotated_frame = frame.copy()
                
            if len(object_detections) > 0:
                frames_com_objetos += 1
                total_objetos_detectados += len(object_detections)
                annotated_frame = self.yolo_detector.annotate_frame(annotated_frame, object_detections)

            cv2.imwrite(str(annotated_dir / frame_path.name), annotated_frame)
            
            from src.domain.video_models import FrameAnalysis, FrameInfo
            frame_info = FrameInfo(frame_number=total_frames, timestamp=0.0)
            frames_list.append(FrameAnalysis(
                frame_info=frame_info,
                faces=face_detections,
                objects=object_detections
            ))

        end_time = time.time()
        tempo_medio = (end_time - start_time) / total_frames if total_frames > 0 else 0
        media_faces_por_frame = total_faces_detectadas / total_frames if total_frames > 0 else 0

        analysis = VideoAnalysis(
            video_info=None,
            frames_analyzed=total_frames,
            faces_detected=total_faces_detectadas,
            average_faces_per_frame=media_faces_por_frame,
            average_processing_time=tempo_medio,
            frames_with_faces=frames_com_rosto,
            frames_without_faces=frames_sem_rosto,
            objects_detected=total_objetos_detectados,
            frames_with_objects=frames_com_objetos,
            frames=frames_list
        )

        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(analysis.to_dict(), f, indent=4, ensure_ascii=False)
            
        with open(face_summary_path, "w", encoding="utf-8") as f:
            json.dump({'faces_detected': analysis.faces_detected}, f, indent=4)
            
        with open(yolo_summary_path, "w", encoding="utf-8") as f:
            json.dump({'objects_detected': analysis.objects_detected}, f, indent=4)

        return analysis
