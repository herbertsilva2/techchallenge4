# Coleta e anotação do dataset YOLO — `hand_on_face`

## Finalidade e limites

O dataset treina somente a classe `0: hand_on_face`, usada como **indicador não verbal potencial de desconforto** em triagem. Ela não permite inferir violência, diagnóstico, intenção ou estado psicológico sem avaliação humana.

Use apenas imagens encenadas por participantes adultos com consentimento documentado, imagens sintéticas, ou bases públicas cuja licença permita uso acadêmico e treinamento de modelo. Não colete imagens de pacientes reais, prontuários, ambientes clínicos identificáveis, menores de idade ou pessoas sem consentimento.

## Meta inicial

Monte inicialmente 150 a 250 imagens, com aproximadamente 70% para `train`, 20% para `val` e 10% para `test`. Reserve ao menos 30% como exemplos negativos: pessoas sem a mão no rosto, mãos próximas mas sem contato, braços cruzados e cenas sem pessoa.

Evite que quadros da mesma gravação, da mesma pessoa, da mesma roupa ou do mesmo cenário apareçam em splits diferentes. A divisão deve ser feita por sessão de captura para reduzir vazamento de dados.

## Captura

1. Registre no `metadata_template.csv` uma linha por imagem, usando somente um identificador não pessoal (`sample_id`).
2. Capture variedade de iluminação, ângulo, distância, tonalidade de pele, acessórios e mão esquerda/direita.
3. Para exemplos positivos, a mão deve tocar ou cobrir parte visível do rosto. Para negativos, registre `contains_hand_on_face=no`.
4. Exclua imagens borradas, com rosto identificável sem autorização, ou contexto que revele dado de saúde.
5. Converta para JPEG ou PNG e nomeie como `hoc_<sessao>_<numero>.jpg`.

## Estrutura de arquivos

```
data/yolo_dataset/
├── images/{train,val,test}/
├── labels/{train,val,test}/
├── dataset.yaml
└── metadata_template.csv
```

Cada imagem positiva deve ter um `.txt` de mesmo nome em `labels/<split>/`. Exemplos negativos podem não ter `.txt` ou ter um arquivo vazio. Nunca coloque uma imagem e seu rótulo em splits distintos.

## Rotulagem

Use CVAT, Roboflow Annotate, Label Studio ou ferramenta equivalente para desenhar **uma caixa delimitadora apenas sobre a mão (ou mãos) em contato com o rosto**. Exporte em formato YOLO Detection.

Formato de cada linha:

```
0 x_centro y_centro largura altura
```

As quatro coordenadas são normalizadas entre 0 e 1. Não rotule rosto, braço, pessoa inteira, mão distante do rosto, mão de outra pessoa próxima ao rosto ou contato ambíguo/oculto.

## Revisão e aceite

1. Um segundo anotador revisa 100% de `val` e `test` e uma amostra mínima de 20% de `train`.
2. Registre o identificador não pessoal do revisor no CSV de metadados.
3. Execute `python scripts/validate_yolo_dataset.py` e corrija todos os erros antes do treino.
4. Revise visualmente pelo menos 20 imagens de cada split com as caixas sobrepostas.
5. Congele `test` antes do treinamento: ele só é usado para avaliação final.

## Critérios para treinar

- Todas as imagens possuem origem, licença ou consentimento rastreável no CSV local protegido.
- Não há vazamento de sessões entre splits.
- O validador não aponta erros críticos.
- Há exemplos negativos e variação visual suficiente.
- As métricas de validação e teste serão registradas junto à versão do modelo e à data de treinamento.
