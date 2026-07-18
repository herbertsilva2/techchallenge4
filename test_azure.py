import sys
from pathlib import Path
from src.utils.config import AZURE_SPEECH_KEY, AZURE_SPEECH_REGION, AZURE_SPEECH_LANGUAGE, AZURE_SPEECH_ENDPOINT
from src.audio.azure_speech_transcriber import AzureSpeechTranscriber

def main():
    try:
        transcriber = AzureSpeechTranscriber(
            key=AZURE_SPEECH_KEY,
            region=AZURE_SPEECH_REGION,
            language=AZURE_SPEECH_LANGUAGE,
            endpoint=AZURE_SPEECH_ENDPOINT
        )
        audio_path = Path("data/samples/test_audio.wav")
        if not audio_path.exists():
            print("Audio test file not found.")
            sys.exit(1)
        transcript = transcriber.transcribe(audio_path)
        print("Autenticação no Azure: SUCESSO")
        print(f"Transcrição Obtida: {transcript.full_text}")
    except Exception as e:
        print(f"Erro na autenticação ou transcrição: {e}")

if __name__ == "__main__":
    main()
