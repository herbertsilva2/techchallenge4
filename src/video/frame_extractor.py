import cv2
from pathlib import Path

class FrameExtractor:
    def __init__(self, video_path: str, output_directory: str):
        self.video_path = Path(video_path)
        self.output_directory = Path(output_directory)

    def extract_frames(self, interval: int = 1) -> int:
        """
        Extract frames from the video.
        
        :param interval: Extract one frame every 'interval' frames. 1 means all frames.
        :return: Number of frames extracted.
        """
        frames_dir = self.output_directory / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)

        cap = cv2.VideoCapture(str(self.video_path))
        if not cap.isOpened():
            raise RuntimeError(f"Não foi possível abrir o vídeo para extração de frames: {self.video_path}")

        extracted_count = 0
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % interval == 0:
                extracted_count += 1
                frame_filename = f"frame_{extracted_count:06d}.jpg"
                frame_path = frames_dir / frame_filename
                cv2.imwrite(str(frame_path), frame)

            frame_idx += 1

        cap.release()
        return extracted_count
