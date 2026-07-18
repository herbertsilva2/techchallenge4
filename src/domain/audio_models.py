from dataclasses import dataclass, asdict
from typing import List, Any, Dict

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
class AudioAnalysis:
    """Análise completa do áudio."""
    audio_info: AudioInfo
    segments: List[SpeechSegment]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'audio_info': self.audio_info.to_dict(),
            'segments': [segment.to_dict() for segment in self.segments]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AudioAnalysis':
        return cls(
            audio_info=AudioInfo.from_dict(data['audio_info']),
            segments=[SpeechSegment.from_dict(s) for s in data.get('segments', [])]
        )
