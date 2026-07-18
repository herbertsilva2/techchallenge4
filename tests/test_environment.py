import pytest
import sys
from pathlib import Path

def test_project_root_exists():
    from src.utils.config import PROJECT_ROOT
    assert PROJECT_ROOT.exists()
    assert PROJECT_ROOT.is_dir()

def test_main_directories_exist():
    from src.utils.config import DATA_DIR, MODELS_DIR, DOCS_DIR
    assert DATA_DIR.exists()
    assert MODELS_DIR.exists()
    assert DOCS_DIR.exists()

def test_outputs_directory_is_available():
    from src.utils.config import OUTPUTS_DIR
    assert OUTPUTS_DIR.exists()
    assert OUTPUTS_DIR.is_dir()

def test_opencv_can_be_imported():
    try:
        import cv2
    except ImportError as e:
        pytest.fail(f"OpenCV cannot be imported: {e}")

def test_numpy_can_be_imported():
    try:
        import numpy as np
    except ImportError as e:
        pytest.fail(f"NumPy cannot be imported: {e}")

def test_moviepy_can_be_imported():
    try:
        import moviepy
    except ImportError as e:
        pytest.fail(f"MoviePy cannot be imported: {e}")

def test_config_loaded_correctly():
    from src.utils.config import PROJECT_ROOT, SAMPLES_DIR
    assert SAMPLES_DIR == PROJECT_ROOT / "data" / "samples"
    assert SAMPLES_DIR.exists()
