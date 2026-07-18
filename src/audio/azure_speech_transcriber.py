import time
from pathlib import Path
import azure.cognitiveservices.speech as speechsdk

from src.audio.transcriber import AudioTranscriber
from src.audio.exceptions import (
    AudioTranscriptionError,
    AzureSpeechConfigurationError,
    AzureSpeechServiceError
)
from src.domain.text_models import Transcript, SentenceAnalysis
from src.domain.audio_models import SpeechSegment

class AzureSpeechTranscriber(AudioTranscriber):
    def __init__(self, key: str, region: str, language: str = "pt-BR", endpoint: str = None):
        if not key or not region:
            raise AzureSpeechConfigurationError("Chave ou região do Azure Speech não configuradas.")
        
        self.key = key
        self.region = region
        self.language = language
        self.endpoint = endpoint

    def transcribe(self, audio_path: Path) -> Transcript:
        if not audio_path.exists():
            raise AudioTranscriptionError(f"Arquivo de áudio não encontrado: {audio_path}")
            
        if audio_path.stat().st_size == 0:
            raise AudioTranscriptionError(f"Arquivo de áudio vazio: {audio_path}")
            
        if audio_path.suffix.lower() != '.wav':
            raise AudioTranscriptionError(f"Formato de áudio não suportado, esperado .wav: {audio_path}")

        try:
            if self.endpoint:
                speech_config = speechsdk.SpeechConfig(subscription=self.key, endpoint=self.endpoint)
            else:
                speech_config = speechsdk.SpeechConfig(subscription=self.key, region=self.region)
            speech_config.speech_recognition_language = self.language
            speech_config.output_format = speechsdk.OutputFormat.Detailed
            
            # Requisita tempos
            speech_config.request_word_level_timestamps()

            audio_config = speechsdk.audio.AudioConfig(filename=str(audio_path))
            speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        except Exception as e:
            raise AzureSpeechConfigurationError(f"Erro ao configurar o Azure Speech: {e}")

        done = False
        recognized_texts = []
        segments = []
        has_error = False
        error_msg = ""
        
        def stop_cb(evt: speechsdk.SessionEventArgs):
            nonlocal done
            done = True

        def recognized_cb(evt: speechsdk.SpeechRecognitionEventArgs):
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                text = evt.result.text
                recognized_texts.append(text)
                
                start_sec = evt.result.offset / 1e7
                end_sec = (evt.result.offset + evt.result.duration) / 1e7
                
                segments.append(SpeechSegment(
                    start_time=start_sec,
                    end_time=end_sec,
                    text=text
                ))

        def canceled_cb(evt: speechsdk.SpeechRecognitionCanceledEventArgs):
            nonlocal done, has_error, error_msg
            if evt.reason == speechsdk.CancellationReason.Error:
                has_error = True
                error_msg = f"Serviço cancelado. Error: {evt.error_details}"
            done = True

        speech_recognizer.recognized.connect(recognized_cb)
        speech_recognizer.session_stopped.connect(stop_cb)
        speech_recognizer.canceled.connect(canceled_cb)

        speech_recognizer.start_continuous_recognition()
        
        while not done:
            time.sleep(0.1)

        speech_recognizer.stop_continuous_recognition()

        if has_error:
            raise AzureSpeechServiceError(error_msg)

        if not recognized_texts:
            transcript = Transcript(full_text="", sentences=[])
            transcript.speech_segments = []
            return transcript

        full_text = " ".join(recognized_texts)
        
        sentences = []
        for text in recognized_texts:
            sentences.append(SentenceAnalysis(text=text, sentiment_score=0.0))

        transcript = Transcript(full_text=full_text, sentences=sentences)
        transcript.speech_segments = segments
        
        return transcript
