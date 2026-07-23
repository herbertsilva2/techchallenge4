from dataclasses import dataclass, asdict, field
from typing import List, Tuple, Any, Dict, Optional

@dataclass
class VideoInfo:
    """Informações sobre o vídeo."""
    width: int
    height: int
    fps: float
    frame_count: int
    duration_seconds: float
    codec: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VideoInfo':
        return cls(**data)

@dataclass
class FaceDetection:
    """Informações sobre uma face detectada."""
    bbox: Tuple[int, int, int, int]
    confidence: float
    width: int
    height: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FaceDetection':
        if 'bbox' in data and isinstance(data['bbox'], list):
            data = data.copy()
            data['bbox'] = tuple(data['bbox'])
        return cls(**data)

@dataclass
class FrameInfo:
    """Informações sobre um frame específico."""
    frame_number: int
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FrameInfo':
        return cls(**data)

@dataclass
class FrameAnalysis:
    """Análise de um frame individual."""
    frame_info: FrameInfo
    faces: List[FaceDetection]
    objects: List['ObjectDetection'] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'frame_info': self.frame_info.to_dict(),
            'faces': [face.to_dict() for face in self.faces],
            'objects': [obj.to_dict() for obj in self.objects]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FrameAnalysis':
        return cls(
            frame_info=FrameInfo.from_dict(data['frame_info']),
            faces=[FaceDetection.from_dict(face) for face in data['faces']],
            objects=[ObjectDetection.from_dict(obj) for obj in data.get('objects', [])]
        )

@dataclass
class ObjectDetection:
    """Informações sobre um objeto detectado (YOLO)."""
    bbox: Tuple[int, int, int, int]
    confidence: float
    class_name: str
    width: int
    height: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ObjectDetection':
        if 'bbox' in data and isinstance(data['bbox'], list):
            data = data.copy()
            data['bbox'] = tuple(data['bbox'])
        return cls(**data)

@dataclass
class VideoAnalysis:
    """Resultado final da análise do vídeo."""
    video_info: Optional[VideoInfo]
    frames_analyzed: int
    faces_detected: int
    average_faces_per_frame: float
    average_processing_time: float
    frames_with_faces: int
    frames_without_faces: int
    frames: List[FrameAnalysis]
    objects_detected: int = 0
    frames_with_objects: int = 0
    sharp_object_candidate_frames: int = 0
    confirmed_sharp_object_frames: int = 0
    max_sharp_object_confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'video_info': self.video_info.to_dict() if self.video_info else None,
            'frames_analyzed': self.frames_analyzed,
            'faces_detected': self.faces_detected,
            'average_faces_per_frame': self.average_faces_per_frame,
            'average_processing_time': self.average_processing_time,
            'frames_with_faces': self.frames_with_faces,
            'frames_without_faces': self.frames_without_faces,
            'objects_detected': self.objects_detected,
            'frames_with_objects': self.frames_with_objects,
            'sharp_object_candidate_frames': self.sharp_object_candidate_frames,
            'confirmed_sharp_object_frames': self.confirmed_sharp_object_frames,
            'max_sharp_object_confidence': self.max_sharp_object_confidence,
            'frames': [frame.to_dict() for frame in self.frames]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VideoAnalysis':
        return cls(
            video_info=VideoInfo.from_dict(data['video_info']) if data.get('video_info') else None,
            frames_analyzed=data['frames_analyzed'],
            faces_detected=data['faces_detected'],
            average_faces_per_frame=data['average_faces_per_frame'],
            average_processing_time=data['average_processing_time'],
            frames_with_faces=data.get('frames_with_faces', 0),
            frames_without_faces=data.get('frames_without_faces', 0),
            objects_detected=data.get('objects_detected', 0),
            frames_with_objects=data.get('frames_with_objects', 0),
            sharp_object_candidate_frames=data.get('sharp_object_candidate_frames', 0),
            confirmed_sharp_object_frames=data.get('confirmed_sharp_object_frames', 0),
            max_sharp_object_confidence=data.get('max_sharp_object_confidence', 0.0),
            frames=[FrameAnalysis.from_dict(f) for f in data.get('frames', [])]
        )
