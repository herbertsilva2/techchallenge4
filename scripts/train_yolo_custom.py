import argparse
from pathlib import Path

from ultralytics import YOLO


def main():
    parser = argparse.ArgumentParser(description="Treina YOLOv8 customizado para o Tech Challenge Fase 4.")
    parser.add_argument("--data", default="data/yolo_dataset/dataset.yaml", help="Caminho do dataset.yaml.")
    parser.add_argument("--base-model", default="yolov8n.pt", help="Modelo base do Ultralytics.")
    parser.add_argument("--epochs", type=int, default=50, help="Numero de epocas.")
    parser.add_argument("--imgsz", type=int, default=640, help="Tamanho das imagens.")
    parser.add_argument("--batch", type=int, default=16, help="Batch size.")
    parser.add_argument("--name", default="hand_safety_yolov8n", help="Nome da execucao em runs/detect.")
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        raise FileNotFoundError(f"dataset.yaml nao encontrado: {data_path}")

    model = YOLO(args.base_model)
    model.train(
        data=str(data_path),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        name=args.name,
    )

    print("\nTreino finalizado.")
    print(f"Melhor peso esperado em: runs/detect/{args.name}/weights/best.pt")
    print("Copie esse arquivo para: models/yolo/best.pt")


if __name__ == "__main__":
    main()
