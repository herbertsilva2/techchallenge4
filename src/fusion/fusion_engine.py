from datetime import datetime, timezone
from src.domain.video_models import VideoAnalysis
from src.domain.audio_models import AudioAnalysis
from src.domain.text_models import TextAnalysis
from src.domain.fusion_models import FusionResult
from src.fusion.risk_rules import RiskRules

class FusionEngine:
    """Mecanismo central de fusão de dados multimodais."""
    
    def __init__(self):
        self.rules = RiskRules()
        
    def process(self, video: VideoAnalysis | None, audio: AudioAnalysis | None, text: TextAnalysis | None) -> FusionResult:
        """
        Executa as regras de fusão sobre as análises disponíveis.
        
        Args:
            video: Resultado da análise de vídeo (Face + YOLO).
            audio: Resultado da análise de áudio.
            text: Resultado da análise de texto.
            
        Returns:
            FusionResult: Resultado consolidado com score, evidências, nível de risco.
        """
        score, evidences, justifications = self.rules.evaluate(video, audio, text)
        risk_level = self.rules.get_risk_level(score)
        recommendations = self.rules.get_recommendations(risk_level, len(evidences) > 0)
        
        # Gera o timestamp ISO 8601 UTC
        timestamp = datetime.now(timezone.utc).isoformat()
        
        return FusionResult(
            risk_level=risk_level,
            evidences=evidences,
            score=score,
            justifications=justifications,
            recommendations=recommendations,
            timestamp=timestamp
        )
