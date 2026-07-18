import pytest
from pathlib import Path
from src.audio.azure_speech_transcriber import AzureSpeechTranscriber
from src.audio.exceptions import AudioTranscriptionError, AzureSpeechConfigurationError

def test_azure_speech_missing_credentials():
    with pytest.raises(AzureSpeechConfigurationError):
        AzureSpeechTranscriber(key="", region="eastus")
        
    with pytest.raises(AzureSpeechConfigurationError):
        AzureSpeechTranscriber(key="key", region="")

def test_azure_speech_invalid_file(tmp_path):
    transcriber = AzureSpeechTranscriber(key="fake", region="fake")
    
    # Arquivo inexistente
    with pytest.raises(AudioTranscriptionError, match="não encontrado"):
        transcriber.transcribe(tmp_path / "missing.wav")

    # Arquivo vazio
    empty_file = tmp_path / "empty.wav"
    empty_file.touch()
    with pytest.raises(AudioTranscriptionError, match="vazio"):
        transcriber.transcribe(empty_file)

    # Extensão inválida
    invalid_file = tmp_path / "test.mp3"
    with open(invalid_file, 'wb') as f:
        f.write(b'fake data')
        
    with pytest.raises(AudioTranscriptionError, match="Formato de áudio não suportado"):
        transcriber.transcribe(invalid_file)
