import numpy as np
import soundfile as sf

from src.audio.vocal_analysis_service import VocalAnalysisService


def _write_signal(path, samples, sample_rate=16000):
    sf.write(path, samples.astype(np.float32), sample_rate)


def test_vocal_metrics_detect_pause_and_text_hesitation(tmp_path):
    sample_rate = 16000
    t = np.arange(sample_rate) / sample_rate
    voice = 0.2 * np.sin(2 * np.pi * 180 * t)
    path = tmp_path / "voice.wav"
    _write_signal(path, np.concatenate([voice, np.zeros(sample_rate), voice]))

    analysis = VocalAnalysisService().analyze(path, "hum eu estou bem")

    assert analysis.quality['status'] == 'completed'
    assert analysis.vocal_metrics.pause_count == 1
    assert analysis.vocal_metrics.longest_pause_seconds >= 0.5
    assert analysis.vocal_metrics.words_per_minute is not None
    assert analysis.vocal_metrics.filler_count == 1


def test_vocal_metrics_marks_silence_unavailable(tmp_path):
    path = tmp_path / "silent.wav"
    _write_signal(path, np.zeros(16000 * 2))

    analysis = VocalAnalysisService().analyze(path)

    assert analysis.quality['status'] == 'unavailable'
    assert analysis.vocal_metrics is None
