from dataclasses import dataclass, asdict, field
from typing import Dict, Any, Optional
from src.domain.video_models import VideoInfo
from src.domain.fusion_models import FusionResult
from src.domain.audio_models import AudioAnalysis
from src.domain.alert_models import AlertNotification

@dataclass
class ModalityStatus:
    status: str  # completed, not_executed, unavailable, failed, partial
    reason: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result = {'status': self.status}
        if self.reason:
            result['reason'] = self.reason
        if self.details:
            result.update(self.details)
        return result

@dataclass
class ReportData:
    timestamp: str
    video_info: Optional[VideoInfo]
    modalities: Dict[str, ModalityStatus]
    fusion_result: Optional[FusionResult]
    ethical_warning: str
    transcript: Optional[str] = None
    speech_provider: Optional[str] = None
    language: Optional[str] = None
    speech_status: Optional[str] = None
    audio_analysis: Optional[AudioAnalysis] = None
    alert_notification: Optional[AlertNotification] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'timestamp': self.timestamp,
            'video_info': self.video_info.to_dict() if self.video_info else None,
            'modalities': {k: v.to_dict() for k, v in self.modalities.items()},
            'fusion_result': self.fusion_result.to_dict() if self.fusion_result else None,
            'ethical_warning': self.ethical_warning
        }
        if self.transcript is not None:
            result['transcript'] = self.transcript
        if self.speech_provider is not None:
            result['speech_provider'] = self.speech_provider
        if self.language is not None:
            result['language'] = self.language
        if self.speech_status is not None:
            result['speech_status'] = self.speech_status
        if self.audio_analysis is not None:
            result['audio_analysis'] = self.audio_analysis.to_dict()
        if self.alert_notification is not None:
            result['alert_notification'] = self.alert_notification.to_dict()
        return result
