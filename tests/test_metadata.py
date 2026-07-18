import cv2
import pytest
import numpy as np
from pathlib import Path
from src.video.video_metadata import VideoMetadata

@pytest.fixture
def dummy_video(tmp_path):
    video_path = tmp_path / "dummy.mp4"
    width, height = 640, 480
    fps = 30
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(video_path), fourcc, fps, (width, height))
    
    # Write 10 frames
    for _ in range(10):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        out.write(frame)
        
    out.release()
    return video_path

def test_get_metadata_valid_video(dummy_video):
    metadata = VideoMetadata.get_metadata(str(dummy_video))
    
    assert metadata.width == 640
    assert metadata.height == 480
    assert metadata.fps == 30.0
    assert metadata.frame_count == 10
    # Allow some tolerance for floating point calculations
    assert abs(metadata.duration_seconds - (10 / 30.0)) < 0.01

def test_get_metadata_invalid_video():
    with pytest.raises(RuntimeError, match="Não foi possível abrir o vídeo"):
        VideoMetadata.get_metadata("non_existent_video_for_metadata.mp4")
