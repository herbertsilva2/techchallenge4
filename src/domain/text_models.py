from dataclasses import dataclass, asdict, field
from typing import List, Any, Dict

@dataclass
class SentenceAnalysis:
    """Análise de uma sentença de texto."""
    text: str
    sentiment_score: float
    categories: List[str] = field(default_factory=list)
    keyword_count: int = 0
    risk_level: str = "baixo"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SentenceAnalysis':
        # Safely extract fields with defaults for backwards compatibility
        return cls(
            text=data.get('text', ''),
            sentiment_score=data.get('sentiment_score', 0.0),
            categories=data.get('categories', []),
            keyword_count=data.get('keyword_count', 0),
            risk_level=data.get('risk_level', 'baixo')
        )

@dataclass
class Transcript:
    """Transcrição de texto."""
    full_text: str
    sentences: List[SentenceAnalysis]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'full_text': self.full_text,
            'sentences': [sentence.to_dict() for sentence in self.sentences]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transcript':
        return cls(
            full_text=data.get('full_text', ''),
            sentences=[SentenceAnalysis.from_dict(s) for s in data.get('sentences', [])]
        )

@dataclass
class TextAnalysis:
    """Análise completa do texto."""
    transcript: Transcript
    overall_sentiment: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            'transcript': self.transcript.to_dict(),
            'overall_sentiment': self.overall_sentiment
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TextAnalysis':
        return cls(
            transcript=Transcript.from_dict(data['transcript']),
            overall_sentiment=data.get('overall_sentiment', 0.0)
        )
