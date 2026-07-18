import json
from pathlib import Path
from src.domain.video_models import VideoAnalysis
from src.domain.audio_models import AudioAnalysis
from src.domain.text_models import TextAnalysis
from src.domain.fusion_models import FusionResult
from src.fusion.fusion_engine import FusionEngine

class FusionService:
    """Serviço para execução da fusão multimodal e gravação de resultados."""

    def __init__(self, output_dir: str, engine: FusionEngine):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.engine = engine

    def execute(self, video: VideoAnalysis | None, audio: AudioAnalysis | None, text: TextAnalysis | None) -> FusionResult:
        """Executa a fusão e salva o resultado no disco."""
        result = self.engine.process(video, audio, text)

        output_path = self.output_dir / "fusion_result.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, indent=4, ensure_ascii=False)

        return result
