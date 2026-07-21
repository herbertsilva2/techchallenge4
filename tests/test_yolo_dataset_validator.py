import pytest
import os
from pathlib import Path
from scripts.validate_yolo_dataset import validate_dataset

@pytest.fixture
def temp_dataset(tmp_path):
    dataset_dir = tmp_path / "data" / "yolo_dataset"
    
    splits = ['train', 'val', 'test']
    for split in splits:
        (dataset_dir / "images" / split).mkdir(parents=True, exist_ok=True)
        (dataset_dir / "labels" / split).mkdir(parents=True, exist_ok=True)
        
    return dataset_dir

def create_pair(dataset_dir, split, name, label_content):
    img_path = dataset_dir / "images" / split / f"{name}.jpg"
    lbl_path = dataset_dir / "labels" / split / f"{name}.txt"
    
    # Create empty image file
    with open(img_path, 'wb') as f:
        f.write(b'\x00' * 10)
        
    with open(lbl_path, 'w') as f:
        f.write(label_content)

def test_valid_dataset(temp_dataset):
    create_pair(temp_dataset, 'train', 'img1', '0 0.5 0.5 0.2 0.2\n')
    create_pair(temp_dataset, 'val', 'img2', '0 0.2 0.2 0.1 0.1\n')
    create_pair(temp_dataset, 'test', 'img3', '0 0.9 0.9 0.05 0.05\n')
    
    assert validate_dataset(str(temp_dataset)) is True

def test_image_without_label_is_a_valid_negative_example(temp_dataset):
    # Uma imagem sem objeto da classe pode não ter arquivo de label no YOLO.
    img_path = temp_dataset / "images" / "train" / "img_no_lbl.jpg"
    with open(img_path, 'wb') as f:
        f.write(b'\x00' * 10)
        
    assert validate_dataset(str(temp_dataset)) is True

def test_label_without_image(temp_dataset):
    # Label exists, but image does not
    lbl_path = temp_dataset / "labels" / "train" / "lbl_no_img.txt"
    with open(lbl_path, 'w') as f:
        f.write("0 0.5 0.5 0.2 0.2\n")
        
    assert validate_dataset(str(temp_dataset)) is False

def test_invalid_class_id(temp_dataset):
    # class_id != 0
    create_pair(temp_dataset, 'train', 'img_inv_cls', '1 0.5 0.5 0.2 0.2\n')
    assert validate_dataset(str(temp_dataset)) is False

def test_coordinate_out_of_range(temp_dataset):
    # x > 1.0
    create_pair(temp_dataset, 'train', 'img_out_bounds', '0 1.5 0.5 0.2 0.2\n')
    assert validate_dataset(str(temp_dataset)) is False

def test_empty_label_is_a_valid_negative_example(temp_dataset):
    # Arquivo de label vazio também representa exemplo negativo.
    create_pair(temp_dataset, 'train', 'img_empty', '')
    assert validate_dataset(str(temp_dataset)) is True

def test_data_leakage(temp_dataset):
    # Same name in train and val
    create_pair(temp_dataset, 'train', 'leak_img', '0 0.5 0.5 0.2 0.2\n')
    create_pair(temp_dataset, 'val', 'leak_img', '0 0.5 0.5 0.2 0.2\n')
    assert validate_dataset(str(temp_dataset)) is False
