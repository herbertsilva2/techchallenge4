# Treinamento YOLOv8 Customizado

## Objetivo

Treinar um modelo YOLOv8 customizado para complementar o `yolov8n.pt` base com classes especificas do Tech Challenge Fase 4:

- `hand_on_face`: gesto nao verbal associado a desconforto, medo, vergonha, hesitacao ou receio.
- `sharp_object`: objeto cortante ou suspeito potencialmente relevante para triagem humana.

As classes `knife` e `scissors` ja existem no modelo COCO usado pelo `yolov8n.pt`, mas tambem podem aparecer dentro do conceito customizado `sharp_object` quando o objetivo for treinar uma categoria funcional unica de objeto cortante.

## Estrutura Esperada

```text
data/yolo_dataset/
├── dataset.yaml
├── images/
│   ├── train/
│   ├── val/
│   └── test/
└── labels/
    ├── train/
    ├── val/
    └── test/
```

Cada imagem deve ter um arquivo `.txt` correspondente no mesmo split:

```text
images/train/exemplo_001.jpg
labels/train/exemplo_001.txt
```

Formato da anotacao:

```text
class_id x_center y_center width height
```

Todos os valores de coordenadas devem estar normalizados entre `0` e `1`.

## Classes

```yaml
names:
  0: hand_on_face
  1: sharp_object
```

## Coleta e Anotacao

Para aderencia academica e privacidade, prefira imagens encenadas, imagens proprias ou fontes publicas com licenca compativel.

Quantidade minima recomendada para MVP:

- Treino: 100 a 200 imagens
- Validacao: 30 a 50 imagens
- Teste: 20 a 30 imagens

Ferramentas sugeridas:

- Roboflow
- CVAT
- Label Studio
- makesense.ai

Exporte as anotacoes no formato YOLO.

## Validacao Local

```bash
source .venv/bin/activate
python scripts/validate_yolo_dataset.py
```

Para gerar imagens de conferencia das bounding boxes:

```bash
python scripts/preview_yolo_annotations.py --limit 30
```

As previews serao salvas em:

```text
outputs/dataset_preview/
```

## Treinamento

Localmente ou no Google Colab com GPU:

```bash
python scripts/train_yolo_custom.py \
  --data data/yolo_dataset/dataset.yaml \
  --base-model yolov8n.pt \
  --epochs 50 \
  --imgsz 640 \
  --batch 16 \
  --name hand_safety_yolov8n
```

O melhor peso sera gerado em:

```text
runs/detect/hand_safety_yolov8n/weights/best.pt
```

Copie para:

```text
models/yolo/best.pt
```

## Evidencias Para Entrega

Salvar no projeto:

```text
models/yolo/best.pt
docs/assets/yolo_results/results.png
docs/assets/yolo_results/confusion_matrix.png
docs/assets/yolo_results/PR_curve.png
docs/assets/yolo_results/val_batch0_pred.jpg
```

Registrar no relatorio tecnico:

- origem/licenca do dataset
- quantidade de imagens por split
- classes treinadas
- precision
- recall
- mAP50
- mAP50-95
- exemplos de deteccao
- limitacoes eticas e tecnicas
