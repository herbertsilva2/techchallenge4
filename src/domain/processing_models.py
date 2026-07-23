from dataclasses import dataclass, field
from enum import Enum
from typing import List, Any, Dict, Optional
from src.domain.video_models import VideoInfo, VideoAnalysis
from src.domain.audio_models import AudioAnalysis
from src.domain.text_models import Transcript, TextAnalysis
from src.domain.fusion_models import FusionResult
from src.domain.alert_models import AlertNotification

class ProcessingStep(Enum):
    """Etapas do pipeline de processamento."""
    VIDEO_EXTRACTION = "VIDEO_EXTRACTION"
    AUDIO_EXTRACTION = "AUDIO_EXTRACTION"
    VIDEO_ANALYSIS = "VIDEO_ANALYSIS"
    AUDIO_ANALYSIS = "AUDIO_ANALYSIS"
    TEXT_ANALYSIS = "TEXT_ANALYSIS"
    FUSION = "FUSION"

@dataclass
class ExecutionTime:
    """Tempo de execução de uma etapa."""
    step: ProcessingStep
    duration_seconds: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            'step': self.step.value,
            'duration_seconds': self.duration_seconds
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExecutionTime':
        return cls(
            step=ProcessingStep(data['step']),
            duration_seconds=data['duration_seconds']
        )

@dataclass
class PipelineResult:
    """Resultado final do pipeline de processamento."""
    status: str = "completed"
    current_step: Optional[ProcessingStep] = None
    video_info: Optional[VideoInfo] = None
    video_analysis: Optional[VideoAnalysis] = None
    audio_analysis: Optional[AudioAnalysis] = None
    transcript: Optional[Transcript] = None
    text_analysis: Optional[TextAnalysis] = None
    fusion_result: Optional[FusionResult] = None
    alert_notification: Optional[AlertNotification] = None
    report_json_path: Optional[str] = None
    report_md_path: Optional[str] = None
    messages: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    execution_times: List[ExecutionTime] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'status': self.status,
            'current_step': self.current_step.value if self.current_step else None,
            'video_info': self.video_info.to_dict() if self.video_info else None,
            'video_analysis': self.video_analysis.to_dict() if self.video_analysis else None,
            'audio_analysis': self.audio_analysis.to_dict() if self.audio_analysis else None,
            'transcript': self.transcript.to_dict() if self.transcript else None,
            'text_analysis': self.text_analysis.to_dict() if self.text_analysis else None,
            'fusion_result': self.fusion_result.to_dict() if self.fusion_result else None,
            'alert_notification': self.alert_notification.to_dict() if self.alert_notification else None,
            'report_json_path': self.report_json_path,
            'report_md_path': self.report_md_path,
            'messages': self.messages,
            'errors': self.errors,
            'execution_times': [time.to_dict() for time in self.execution_times]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PipelineResult':
        return cls(
            status=data.get('status', 'completed'),
            current_step=ProcessingStep(data['current_step']) if data.get('current_step') else None,
            video_info=VideoInfo.from_dict(data['video_info']) if data.get('video_info') else None,
            video_analysis=VideoAnalysis.from_dict(data['video_analysis']) if data.get('video_analysis') else None,
            audio_analysis=AudioAnalysis.from_dict(data['audio_analysis']) if data.get('audio_analysis') else None,
            transcript=Transcript.from_dict(data['transcript']) if data.get('transcript') else None,
            text_analysis=TextAnalysis.from_dict(data['text_analysis']) if data.get('text_analysis') else None,
            fusion_result=FusionResult.from_dict(data['fusion_result']) if data.get('fusion_result') else None,
            alert_notification=AlertNotification.from_dict(data['alert_notification']) if data.get('alert_notification') else None,
            report_json_path=data.get('report_json_path'),
            report_md_path=data.get('report_md_path'),
            messages=data.get('messages', []),
            errors=data.get('errors', []),
            execution_times=[ExecutionTime.from_dict(t) for t in data.get('execution_times', [])]
        )
