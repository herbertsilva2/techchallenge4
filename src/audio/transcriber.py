from abc import ABC, abstractmethod
from pathlib import Path
from src.domain.text_models import Transcript

class AudioTranscriber(ABC):
    """Interface abstrata para transcritores de áudio."""
    
    @abstractmethod
    def transcribe(self, audio_path: Path) -> Transcript:
        """
        Transcreve o arquivo de áudio especificado.
        
        Args:
            audio_path (Path): O caminho para o arquivo de áudio.
            
        Returns:
            Transcript: O modelo de domínio com o texto transcrito.
        """
        pass
