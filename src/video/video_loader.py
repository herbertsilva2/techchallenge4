import os
from pathlib import Path

class VideoLoader:
    VALID_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv'}

    def __init__(self, video_path: str):
        self.video_path = Path(video_path)

    def validate(self) -> Path:
        if not self.video_path.exists():
            raise FileNotFoundError(f"Arquivo de vídeo não encontrado: {self.video_path}")
        if not self.video_path.is_file():
            raise ValueError(f"O caminho fornecido não é um arquivo: {self.video_path}")
        if self.video_path.suffix.lower() not in self.VALID_EXTENSIONS:
            raise ValueError(f"Extensão inválida. Permitidas: {', '.join(self.VALID_EXTENSIONS)}")
        return self.video_path
