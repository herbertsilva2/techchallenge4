# Dataset YOLOv8 - MVP Fase 4

## Definição das Classes

Para o MVP do Tech Challenge Fase 4, adotamos três classes customizadas para identificação de sinais visuais relevantes em contexto de entrevista, consulta ou triagem:
- `0: hand_on_face`
- `1: razor_blade`
- `2: box_cutter`

A classe `hand_on_face` representa uma pessoa com uma das mãos (ou ambas) tocando ou cobrindo parcialmente o rosto. O gesto é tratado como sinal não verbal potencialmente associado a desconforto, vergonha, medo, hesitação ou receio.

As classes `razor_blade` e `box_cutter` representam objetos cortantes que podem ser relevantes para triagem humana quando aparecem em contexto de monitoramento assistido. O sistema não conclui risco de automutilação; ele apenas registra evidências visuais para revisão por profissional habilitado.

### Exemplos Positivos (Devem ser anotados)
- Mão cobrindo o rosto (ex: de nervosismo ou tensão).
- Mão tocando a testa, olhos, nariz, boca ou bochecha.
- O gesto deve ser claramente visível e delimitável.
- Lâmina de barbear/gilete claramente visível.
- Estilete/box cutter claramente visível.

### Exclusões (Não devem ser anotados)
- Mão distante do rosto.
- Pessoa apenas cruzando os braços sem tocar o rosto.
- Rosto sem mão visível.
- Imagem sem pessoa.
- Mão de outra pessoa próxima ao rosto.
- Contato muito ambíguo, parcialmente oculto ou fora de contexto.
- Objetos cortantes muito distantes, borrados ou impossíveis de distinguir.
- Objetos parecidos com gilete/estilete sem confirmação visual suficiente.

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
