import json
from pathlib import Path
from src.audio.transcriber import AudioTranscriber
from src.audio.exceptions import AudioTranscriptionError

class TranscriptionService:
    def __init__(self, transcriber: AudioTranscriber, output_dir: str):
        self.transcriber = transcriber
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def execute(self, audio_path: str | Path) -> dict:
        audio_path = Path(audio_path)
        output_file = self.output_dir / "transcript.json"
        
        try:
            transcript = self.transcriber.transcribe(audio_path)
            
            segments = getattr(transcript, 'speech_segments', [])
            duration = segments[-1].end_time if segments else 0.0
            
            result = {
                "status": "concluída",
                "idioma": getattr(self.transcriber, 'language', 'desconhecido'),
                "arquivo_origem": str(audio_path),
                "duracao_segundos": duration,
                "texto_completo": transcript.full_text,
                "segmentos": [s.to_dict() for s in segments],
                "transcript_modelo": transcript.to_dict()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
                
            return result
            
        except Exception as e:
            result = {
                "status": "erro",
                "motivo": str(e),
                "arquivo_origem": str(audio_path)
            }
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
                
            raise
