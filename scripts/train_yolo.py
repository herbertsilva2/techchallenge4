"""Treina o detector customizado e copia o melhor peso para o caminho do pipeline."""

import argparse
import shutil
from pathlib import Path

from ultralytics import YOLO

from validate_yolo_dataset import validate_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Treinar YOLOv8 para hand_on_face")
    parser.add_argument("--data", default="data/yolo_dataset/dataset.yaml")
    parser.add_argument("--model", default="yolov8n.pt")
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--device", default="cpu", help="cpu, 0 ou outro device aceito pelo Ultralytics")
    parser.add_argument("--project", default="outputs/yolo_training")
    parser.add_argument("--name", default="hand_on_face")
    args = parser.parse_args()

    dataset_dir = Path(args.data).parent
    if not validate_dataset(str(dataset_dir)):
        raise SystemExit("Dataset inválido; corrija os erros antes de treinar.")

    model = YOLO(args.model)
    results = model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        project=args.project,
        name=args.name,
        exist_ok=False,
    )

    trained_weights = Path(results.save_dir) / "weights" / "best.pt"
    target = Path("models/yolo/best.pt")
    target.parent.mkdir(parents=True, exist_ok=True)
    if not trained_weights.exists():
        raise SystemExit(f"Treino concluído sem peso esperado: {trained_weights}")

    shutil.copy2(trained_weights, target)
    print(f"Modelo pronto para o pipeline: {target}")
    print(f"Métricas e artefatos: {results.save_dir}")


if __name__ == "__main__":
    main()
