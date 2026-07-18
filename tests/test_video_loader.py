import pytest
from pathlib import Path
from src.video.video_loader import VideoLoader

def test_video_loader_file_not_found():
    loader = VideoLoader("non_existent_video.mp4")
    with pytest.raises(FileNotFoundError, match="Arquivo de vídeo não encontrado"):
        loader.validate()

def test_video_loader_invalid_extension(tmp_path):
    # Create a dummy file with an invalid extension
    invalid_file = tmp_path / "video.txt"
    invalid_file.touch()
    
    loader = VideoLoader(str(invalid_file))
    with pytest.raises(ValueError, match="Extensão inválida"):
        loader.validate()

def test_video_loader_valid_file(tmp_path):
    # Create a dummy valid file
    valid_file = tmp_path / "video.mp4"
    valid_file.touch()
    
    loader = VideoLoader(str(valid_file))
    path = loader.validate()
    assert isinstance(path, Path)
    assert path.name == "video.mp4"
