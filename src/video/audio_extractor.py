import warnings
from pathlib import Path
from moviepy import VideoFileClip

class AudioExtractor:
    def __init__(self, video_path: str, output_directory: str):
        self.video_path = Path(video_path)
        self.output_directory = Path(output_directory)

    def extract_audio(self) -> str | None:
        """
        Extract audio from the video.
        
        :return: The path to the saved audio file, or None if no audio.
        """
        audio_dir = self.output_directory / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        audio_path = audio_dir / "audio.wav"

        try:
            video_clip = VideoFileClip(str(self.video_path))
            if video_clip.audio is None:
                warnings.warn(f"O vídeo não possui áudio: {self.video_path}")
                video_clip.close()
                return None
            
            video_clip.audio.write_audiofile(str(audio_path), logger=None)
            video_clip.close()
            
            return str(audio_path)
        except Exception as e:
            warnings.warn(f"Erro ao extrair áudio: {e}")
            return None
