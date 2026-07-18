import cv2
import argparse
import os
from pathlib import Path

def draw_bboxes(img_path: Path, label_path: Path, output_path: Path):
    if not label_path.exists():
        return False
        
    img = cv2.imread(str(img_path))
    if img is None:
        return False
        
    h, w = img.shape[:2]
    
    with open(label_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 5:
                continue
                
            try:
                cls_id = int(parts[0])
                xc = float(parts[1])
                yc = float(parts[2])
                bw = float(parts[3])
                bh = float(parts[4])
                
                # Convert YOLO format (center x, center y, width, height) normalized
                # to OpenCV format (x1, y1, x2, y2) absolute pixels
                
                box_w = int(bw * w)
                box_h = int(bh * h)
                center_x = int(xc * w)
                center_y = int(yc * h)
                
                x1 = int(center_x - box_w / 2)
                y1 = int(center_y - box_h / 2)
                x2 = x1 + box_w
                y2 = y1 + box_h
                
                color = (0, 255, 0) # Green for hand_on_face
                cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                
                label_text = f"cls:{cls_id}"
                cv2.putText(img, label_text, (x1, max(10, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
            except ValueError:
                continue
                
    cv2.imwrite(str(output_path), img)
    return True

def main():
    parser = argparse.ArgumentParser(description="Preview YOLO dataset annotations")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of images to preview")
    parser.add_argument("--dataset", type=str, default="data/yolo_dataset", help="Path to dataset root")
    parser.add_argument("--output", type=str, default="outputs/dataset_preview", help="Path to save previews")
    
    args = parser.parse_args()
    
    dataset_path = Path(args.dataset)
    output_path = Path(args.output)
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    allowed_exts = {'.jpg', '.jpeg', '.png'}
    splits = ['train', 'val', 'test']
    
    count = 0
    
    for split in splits:
        if count >= args.limit:
            break
            
        images_dir = dataset_path / 'images' / split
        labels_dir = dataset_path / 'labels' / split
        
        if not images_dir.exists() or not labels_dir.exists():
            continue
            
        for img_file in images_dir.iterdir():
            if count >= args.limit:
                break
                
            if img_file.is_file() and img_file.suffix.lower() in allowed_exts:
                label_file = labels_dir / f"{img_file.stem}.txt"
                out_file = output_path / f"{split}_{img_file.name}"
                
                if draw_bboxes(img_file, label_file, out_file):
                    print(f"Saved preview: {out_file}")
                    count += 1

    print(f"\nGenerated {count} previews in {output_path}/")

if __name__ == "__main__":
    main()
