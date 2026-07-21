import re
from pathlib import Path
from typing import Optional

import librosa
import numpy as np

from src.domain.audio_models import AudioAnalysis, AudioInfo, SpeechSegment, VocalMetrics


class VocalAnalysisService:
    """Extrai indicadores acústicos, sem inferir emoções ou condições de saúde."""
    PAUSE_SECONDS = 0.5
    FILLER_PATTERN = re.compile(r"\b(?:é+|eh+|hum+|ahn+|ahn|tipo)\b", re.IGNORECASE)

    def analyze(self, audio_path: str | Path, transcript: Optional[str] = None, segments: Optional[list[SpeechSegment]] = None) -> AudioAnalysis:
        samples, sample_rate = librosa.load(str(audio_path), sr=16000, mono=True)
        duration = len(samples) / sample_rate if sample_rate else 0.0
        quality = {"status": "completed", "reason": None, "duration_seconds": round(duration, 3)}
        if duration < 1.0:
            quality.update(status="unavailable", reason="Áudio curto demais para análise vocal (mínimo de 1 segundo).")
            return AudioAnalysis(AudioInfo(sample_rate, 1, duration), segments or [], quality=quality)

        rms = librosa.feature.rms(y=samples)[0]
        if not np.any(rms > 1e-4):
            quality.update(status="unavailable", reason="Áudio silencioso; não há fala analisável.")
            return AudioAnalysis(AudioInfo(sample_rate, 1, duration), segments or [], quality=quality)

        intervals = librosa.effects.split(samples, top_db=35, frame_length=2048, hop_length=512)
        speech_intervals = [{"start_time": round(start / sample_rate, 3), "end_time": round(end / sample_rate, 3)} for start, end in intervals]
        speech_duration = sum((end - start) / sample_rate for start, end in intervals)
        if speech_duration < 0.5:
            quality.update(status="unavailable", reason="Fala insuficiente para métricas vocais confiáveis.")
            return AudioAnalysis(AudioInfo(sample_rate, 1, duration), segments or [], quality=quality, speech_intervals=speech_intervals)

        pauses = []
        for previous, current in zip(intervals, intervals[1:]):
            gap = (current[0] - previous[1]) / sample_rate
            if gap >= self.PAUSE_SECONDS:
                pauses.append(gap)
        voiced = np.concatenate([samples[start:end] for start, end in intervals])
        pitch = librosa.yin(voiced, fmin=65, fmax=400, sr=sample_rate)
        pitch = pitch[np.isfinite(pitch)]
        intensity_db = librosa.amplitude_to_db(np.maximum(rms, 1e-10), ref=1.0)
        words = re.findall(r"\b[\wÀ-ÿ'-]+\b", transcript or "")
        metrics = VocalMetrics(
            speech_duration_seconds=round(float(speech_duration), 3),
            pause_count=len(pauses), total_pause_seconds=round(float(sum(pauses)), 3),
            average_pause_seconds=round(float(np.mean(pauses)), 3) if pauses else None,
            longest_pause_seconds=round(float(max(pauses)), 3) if pauses else None,
            words_per_minute=round(len(words) / speech_duration * 60, 1) if words else None,
            filler_count=len(self.FILLER_PATTERN.findall(transcript or "")) if transcript is not None else None,
            pitch_mean_hz=round(float(np.mean(pitch)), 1) if len(pitch) else None,
            pitch_std_hz=round(float(np.std(pitch)), 1) if len(pitch) else None,
            intensity_mean_db=round(float(np.mean(intensity_db)), 1),
            intensity_std_db=round(float(np.std(intensity_db)), 1),
        )
        return AudioAnalysis(AudioInfo(sample_rate, 1, duration), segments or [], metrics, quality, speech_intervals)
