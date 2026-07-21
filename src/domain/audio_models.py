from dataclasses import dataclass, asdict, field
from typing import List, Any, Dict, Optional

@dataclass
class AudioInfo:
    """Informações sobre o arquivo de áudio."""
    sample_rate: int
    channels: int
    duration_seconds: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AudioInfo':
        return cls(**data)

@dataclass
class SpeechSegment:
    """Um segmento de fala identificado no áudio."""
    start_time: float
    end_time: float
    text: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SpeechSegment':
        return cls(**data)

@dataclass
class VocalMetrics:
    """Métricas acústicas observáveis; não representam diagnóstico clínico."""
    speech_duration_seconds: float = 0.0
    pause_count: int = 0
    total_pause_seconds: float = 0.0
    average_pause_seconds: Optional[float] = None
    longest_pause_seconds: Optional[float] = None
    words_per_minute: Optional[float] = None
    filler_count: Optional[int] = None
    pitch_mean_hz: Optional[float] = None
    pitch_std_hz: Optional[float] = None
    intensity_mean_db: Optional[float] = None
    intensity_std_db: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VocalMetrics':
        return cls(**data)

@dataclass
class AudioAnalysis:
    """Análise completa do áudio."""
    audio_info: AudioInfo
    segments: List[SpeechSegment]
    vocal_metrics: Optional[VocalMetrics] = None
    quality: Dict[str, Any] = field(default_factory=dict)
    speech_intervals: List[Dict[str, float]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'audio_info': self.audio_info.to_dict(),
            'segments': [segment.to_dict() for segment in self.segments],
            'vocal_metrics': self.vocal_metrics.to_dict() if self.vocal_metrics else None,
            'quality': self.quality or {},
            'speech_intervals': self.speech_intervals or []
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AudioAnalysis':
        return cls(
            audio_info=AudioInfo.from_dict(data['audio_info']),
            segments=[SpeechSegment.from_dict(s) for s in data.get('segments', [])],
            vocal_metrics=VocalMetrics.from_dict(data['vocal_metrics']) if data.get('vocal_metrics') else None,
            quality=data.get('quality') or {},
            speech_intervals=data.get('speech_intervals') or []
        )
