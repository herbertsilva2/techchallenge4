import sys
import os
from pathlib import Path
from typing import List, Dict, Set

VALID_CLASS_IDS = {0, 1}
CLASS_NAMES = {
    0: "hand_on_face",
    1: "sharp_object",
}

def validate_dataset(dataset_dir: str = "data/yolo_dataset") -> bool:
    print("=== YOLO Dataset Validation ===")
    root_path = Path(dataset_dir)
    has_critical_error = False

    splits = ['train', 'val', 'test']
    images_dir = root_path / 'images'
    labels_dir = root_path / 'labels'
    
    # 1. Check directories
    for split in splits:
        for p in [images_dir / split, labels_dir / split]:
            if not p.exists():
                print(f"ERROR: Directory missing: {p}")
                has_critical_error = True

    if has_critical_error:
        return False

    allowed_exts = {'.jpg', '.jpeg', '.png'}
    
    all_images_across_splits: Dict[str, str] = {} # filename without ext -> split name
    
    counts: Dict[str, int] = {'train': 0, 'val': 0, 'test': 0}

    for split in splits:
        print(f"\n--- Checking split: {split} ---")
        img_split_dir = images_dir / split
        lbl_split_dir = labels_dir / split
        
        # Gather images
        images = [f for f in img_split_dir.iterdir() if f.is_file() and f.suffix.lower() in allowed_exts]
        labels = [f for f in lbl_split_dir.iterdir() if f.is_file() and f.suffix.lower() == '.txt']
        
        img_stems = {img.stem for img in images}
        lbl_stems = {lbl.stem for lbl in labels}
        
        counts[split] = len(images)
        
        if len(images) == 0:
            print(f"WARNING: No images found in {split} split.")
            
        # Cross-split leakage check
        for img in images:
            if img.stem in all_images_across_splits:
                print(f"ERROR: Image '{img.name}' in {split} also exists in {all_images_across_splits[img.stem]}! (Data leakage)")
                has_critical_error = True
            all_images_across_splits[img.stem] = split

        # A imagem pode não ter label: isso representa um exemplo negativo
        # (sem hand_on_face), comportamento aceito pelo Ultralytics/YOLO.
        images_without_labels = img_stems - lbl_stems
        orphan_labels = lbl_stems - img_stems
        
        if images_without_labels:
            print(f"INFO: Found {len(images_without_labels)} negative image(s) without labels in {split}.")
            
        if orphan_labels:
            print(f"ERROR: Found {len(orphan_labels)} orphan labels (no corresponding image) in {split}.")
            has_critical_error = True

        # Label content validation. Empty files are valid negative examples.
        for lbl_path in labels:
            if not lbl_path.stat().st_size:
                continue

            with open(lbl_path, 'r') as f:
                lines = f.readlines()
                for line_idx, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split()
                    if len(parts) != 5:
                        print(f"ERROR: Invalid format in {lbl_path.name} (line {line_idx+1})")
                        has_critical_error = True
                        continue
                        
                    try:
                        cls_id = int(parts[0])
                        x = float(parts[1])
                        y = float(parts[2])
                        w = float(parts[3])
                        h = float(parts[4])
                        
                        if cls_id not in VALID_CLASS_IDS:
                            valid_ids = ", ".join(str(i) for i in sorted(VALID_CLASS_IDS))
                            print(f"ERROR: Invalid class_id {cls_id} in {lbl_path.name} (Expected one of: {valid_ids})")
                            has_critical_error = True
                            
                        for val in [x, y, w, h]:
                            if not (0.0 <= val <= 1.0):
                                print(f"ERROR: Coordinate out of bounds [0, 1] in {lbl_path.name}: {val}")
                                has_critical_error = True
                                
                        if w <= 0 or h <= 0:
                            print(f"ERROR: Width or height <= 0 in {lbl_path.name}: w={w}, h={h}")
                            has_critical_error = True
                            
                    except ValueError:
                        print(f"ERROR: Non-numeric value in {lbl_path.name} (line {line_idx+1})")
                        has_critical_error = True

    print("\n=== Summary ===")
    total_images = sum(counts.values())
    print(f"Total images: {total_images}")
    for split in splits:
        print(f"  {split}: {counts[split]}")
        
    if total_images == 0:
        print("ERROR: Dataset is completely empty. Please add images before training.")
        has_critical_error = True

    if has_critical_error:
        print("\n[!] Validation FAILED. Critical errors found.")
        return False
        
    print("\n[+] Validation PASSED.")
    return True

if __name__ == "__main__":
    success = validate_dataset()
    if not success:
        sys.exit(1)
