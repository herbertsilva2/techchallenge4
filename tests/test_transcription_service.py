import pytest
import json
from pathlib import Path
from src.audio.transcription_service import TranscriptionService
from src.audio.transcriber import AudioTranscriber
from src.domain.text_models import Transcript, SentenceAnalysis
from src.domain.audio_models import SpeechSegment

class FakeTranscriber(AudioTranscriber):
    def __init__(self, language="pt-BR"):
        self.language = language

    def transcribe(self, audio_path: Path) -> Transcript:
        sentences = [SentenceAnalysis(text="teste", sentiment_score=0.0)]
        transcript = Transcript(full_text="teste", sentences=sentences)
        transcript.speech_segments = [SpeechSegment(0.0, 1.0, "teste")]
        return transcript

class FakeErrorTranscriber(AudioTranscriber):
    def transcribe(self, audio_path: Path) -> Transcript:
        raise Exception("Erro forçado")

def test_transcription_service_success(tmp_path):
    transcriber = FakeTranscriber()
    service = TranscriptionService(transcriber, str(tmp_path))
    
    audio_path = tmp_path / "test.wav"
    audio_path.touch()
    
    result = service.execute(audio_path)
    
    assert result["status"] == "concluída"
    assert result["texto_completo"] == "teste"
    assert "transcript_modelo" in result
    
    json_path = tmp_path / "transcript.json"
    assert json_path.exists()
    
    with open(json_path, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)
        assert saved_data["status"] == "concluída"
        assert saved_data["texto_completo"] == "teste"

def test_transcription_service_error(tmp_path):
    transcriber = FakeErrorTranscriber()
    service = TranscriptionService(transcriber, str(tmp_path))
    
    audio_path = tmp_path / "test.wav"
    audio_path.touch()
    
    with pytest.raises(Exception):
        service.execute(audio_path)
        
    json_path = tmp_path / "transcript.json"
    assert json_path.exists()
    
    with open(json_path, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)
        assert saved_data["status"] == "erro"
        assert saved_data["motivo"] == "Erro forçado"
