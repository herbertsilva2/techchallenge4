from pathlib import Path
from moviepy import AudioFileClip


class AudioNormalizer:
    """Converte entradas aceitas para WAV mono de 16 kHz."""

    def normalize(self, source_path: str | Path, output_dir: str | Path) -> Path:
        source = Path(source_path)
        if not source.exists() or source.stat().st_size == 0:
            raise ValueError("Arquivo de áudio inexistente ou vazio.")
        target_dir = Path(output_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / "normalized_audio.wav"
        clip = AudioFileClip(str(source))
        try:
            clip.write_audiofile(str(target), fps=16000, nbytes=2, codec="pcm_s16le", ffmpeg_params=["-ac", "1"], logger=None)
        finally:
            clip.close()
        return target
