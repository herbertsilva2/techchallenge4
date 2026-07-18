from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Any, Dict

class RiskLevel(Enum):
    """Níveis de risco identificados."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

@dataclass
class Evidence:
    """Evidência encontrada em uma das modalidades."""
    modality: str
    description: str
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Evidence':
        return cls(**data)

@dataclass
class FusionResult:
    """Resultado da fusão de todas as modalidades."""
    risk_level: RiskLevel
    evidences: List[Evidence]
    score: float = 0.0
    justifications: List[str] = None
    recommendations: List[str] = None
    timestamp: str = ""

    def __post_init__(self):
        if self.justifications is None:
            self.justifications = []
        if self.recommendations is None:
            self.recommendations = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            'risk_level': self.risk_level.value,
            'score': self.score,
            'evidences': [evidence.to_dict() for evidence in self.evidences],
            'justifications': self.justifications,
            'recommendations': self.recommendations,
            'timestamp': self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FusionResult':
        return cls(
            risk_level=RiskLevel(data['risk_level']),
            evidences=[Evidence.from_dict(e) for e in data.get('evidences', [])],
            score=data.get('score', 0.0),
            justifications=data.get('justifications', []),
            recommendations=data.get('recommendations', []),
            timestamp=data.get('timestamp', "")
        )
