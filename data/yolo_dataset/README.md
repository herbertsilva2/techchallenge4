# Dataset YOLOv8 - MVP Fase 4

## Definição da Classe

Para o MVP do Tech Challenge Fase 4, adotamos uma única classe para identificação de desconforto/tensão na imagem:
- `0: hand_on_face`

Esta classe representa uma pessoa com uma das mãos (ou ambas) tocando ou cobrindo parcialmente o rosto.

### Exemplos Positivos (Devem ser anotados)
- Mão cobrindo o rosto (ex: de nervosismo ou tensão).
- Mão tocando a testa, olhos, nariz, boca ou bochecha.
- O gesto deve ser claramente visível e delimitável.

### Exclusões (Não devem ser anotados)
- Mão distante do rosto.
- Pessoa apenas cruzando os braços sem tocar o rosto.
- Rosto sem mão visível.
- Imagem sem pessoa.
- Mão de outra pessoa próxima ao rosto.
- Contato muito ambíguo, parcialmente oculto ou fora de contexto.

## Formato das Anotações
As anotações seguem o formato padrão do YOLO, onde cada imagem tem um arquivo `.txt` correspondente contendo:
`<class_id> <x_center> <y_center> <width> <height>`

Todas as coordenadas e dimensões estão normalizadas entre 0 e 1.

## Divisão Recomendada do Dataset
- **70%** Treinamento (train)
- **20%** Validação (val)
- **10%** Teste (test)

*Nota: A meta técnica mínima para experimentos é de 60 imagens. Para o MVP, é recomendado obter entre 100 e 150 imagens para aumentar a variabilidade.*

## Origem e Licença das Imagens
Atualmente o dataset encontra-se em fase de preparação. As imagens devem provir de:
- Imagens sintéticas geradas ou encenadas pelos próprios alunos.
- Datasets públicos com licença de uso permitida para fins acadêmicos.
- Nenhuma imagem de pacientes reais ou com dados pessoais identificáveis não autorizados será incluída.

## Limitações e Possíveis Vieses
- Como o dataset é focado em recortes específicos (gestos), pode haver viés em relação a condições de iluminação, variabilidade de gênero/etnia e ângulos da câmera.
- A quantidade reduzida de imagens (MVP) não garantirá generalização perfeita e alta performance no mundo real, mas servirá para validação da arquitetura e fluxo técnico.
