import cv2
from src.domain.video_models import VideoInfo

class VideoMetadata:
    @staticmethod
    def get_metadata(video_path: str) -> VideoInfo:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise RuntimeError(f"Não foi possível abrir o vídeo para leitura de metadados: {video_path}")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        duration_seconds = frame_count / fps if fps > 0 else 0.0

        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
        try:
            codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
        except Exception:
            codec = "Unknown"

        cap.release()

        return VideoInfo(
            width=width,
            height=height,
            fps=fps,
            frame_count=frame_count,
            duration_seconds=duration_seconds,
            codec=codec
        )
