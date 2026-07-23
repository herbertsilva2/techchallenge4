# Relatório Técnico: MVP Multimodal

## Introdução

Este documento descreve as decisões técnicas, a arquitetura, os resultados verificáveis e as limitações do MVP desenvolvido para o Tech Challenge Fase 4. O sistema produz evidências para **apoio à triagem humana**; não emite diagnóstico, não infere intenção e não substitui a avaliação de um profissional capacitado.

## Arquitetura do Sistema

O sistema adota uma arquitetura modular orientada a pipelines. Dados extraídos de um vídeo (frames e áudio) são analisados por motores de inferência independentes e consolidados por regras determinísticas.

### Módulos principais

1. **Vídeo/visual (OpenCV, MediaPipe e YOLOv8):** extrai frames, identifica rostos e procura sinais visuais e objetos de interesse.
2. **Áudio e transcrição (Azure Speech):** extrai o áudio e obtém o conteúdo falado.
3. **Análise textual:** classifica a transcrição em categorias predefinidas.
4. **Fusão multimodal:** pondera evidências das modalidades por regras simples e auditáveis.

## Resultados obtidos e métricas

O repositório contém o registro de um treinamento YOLOv8 para as classes `hand_on_face` e `sharp_object`. A execução utilizou `yolov8n` pré-treinado, 50 épocas, imagens de 640 pixels e lote (*batch*) de 8, conforme [`runs/detect/hand_safety_yolov8n/args.yaml`](../runs/detect/hand_safety_yolov8n/args.yaml).

As maiores métricas de validação registradas no histórico de treinamento são:

| Métrica | Melhor valor registrado |
| --- | ---: |
| Precisão | 0,782 |
| Recall | 0,762 |
| mAP@50 | 0,302 |
| mAP@50–95 | 0,259 |

Os valores foram extraídos de [`runs/detect/hand_safety_yolov8n/results.csv`](../runs/detect/hand_safety_yolov8n/results.csv). Eles são picos por métrica em épocas distintas, e não devem ser interpretados como uma única medição de um modelo final. Em especial, os valores de mAP ainda são baixos para uso operacional. O treinamento demonstra que o fluxo técnico foi executado e gerou pesos, mas não valida o detector para uso real.

## Exemplos concretos de anomalias e regras de decisão

Os seguintes cenários são reprodutíveis nos testes automatizados e descrevem como o MVP transforma sinais em evidências de triagem:

- **Mão no rosto recorrente:** duas detecções `hand_on_face` em frames diferentes são consolidadas pela fusão como uma única categoria visual; no cenário de teste, ela contribui com 10 pontos ao escore, sem duplicar o peso pelo número de frames. Veja `test_deduplication` em [`tests/test_fusion.py`](../tests/test_fusion.py).
- **Objeto cortante confirmado:** um candidato `sharp_object` só passa a ser registrado como evidência se estiver presente em pelo menos 2 dos últimos 3 frames analisados. O teste simula candidatos com confiança 0,129 e 0,103 em frames consecutivos e confirma uma evidência no segundo frame. Veja `test_sharp_object_requires_two_candidates_in_three_frames` em [`tests/test_sharp_object_confirmation.py`](../tests/test_sharp_object_confirmation.py).
- **Detecção isolada descartada:** um único candidato `sharp_object`, seguido por dois frames sem candidato, não é convertido em evidência. Esse cenário é coberto por `test_isolated_sharp_object_candidate_does_not_become_evidence`.

Esses exemplos verificam regras de decisão do software, não a acurácia do modelo em pessoas ou situações reais. Uma detecção permanece uma evidência potencial, sujeita à revisão humana e ao contexto.

## Lacunas da avaliação experimental

Embora existam 48, 14 e 7 arquivos de rótulo nos *splits* de treino, validação e teste, respectivamente, os diretórios de imagens versionados contêm somente arquivos `.gitkeep`. Portanto, não é possível reproduzir no estado atual do repositório uma avaliação independente sobre imagens rotuladas.

Por esse motivo, este relatório não apresenta métricas por classe, matriz de confusão, exemplos visuais de acerto/erro ou resultados ponta a ponta em vídeos reais. Tais resultados não foram inferidos a partir dos testes unitários nem fabricados a partir do histórico de treinamento.

## Implementação do Dashboard Streamlit

Nesta fase, a orquestração terminal (`main.py`) foi adaptada para uma interface visual interativa (`app.py`), isolando o fluxo de dados na camada `src/services/` (`DashboardService`, `PipelineService` e `ResultLoader`).

### Principais desafios superados

1. **Processamento síncrono e limites seguros:** o Streamlit executa cada interação de forma síncrona. O dashboard atualiza elementos nativos (`st.empty` e `st.progress`) e limita os arquivos a 200 MB, sugerindo vídeos de até três minutos para evitar esgotamento de recursos.
2. **Tolerância a falhas:** `PipelineResult` possui o estado `completed`, `partial` ou `failed`. Assim, indisponibilidade de credenciais Azure, ausência de detecção YOLO ou vídeos sem áudio não impedem as modalidades restantes de produzirem resultados.
3. **Gerenciamento de arquivos em memória:** `DashboardService` usa `tempfile` para hospedar o vídeo temporariamente, sanitiza o nome por UUID e remove o arquivo após o processamento, reduzindo a persistência de mídia sensível.

O gráfico de pizza de contribuição multimodal permanece removido temporariamente, pois a fusão atual depende majoritariamente de pesos textuais agregados na ausência de paridade preditiva entre as modalidades. O frontend é iniciado com `streamlit run app.py`.

## Limitações e próximos passos

- A transcrição requer credenciais Azure válidas e conectividade com a internet; logo, o pipeline não é integralmente offline.
- A detecção de `hand_on_face` combina um detector customizado, quando disponível, com MediaPipe Hands + Face Mesh para sinalizar proximidade persistente mão-rosto. Essa proximidade geométrica não constitui diagnóstico e não substitui a validação do YOLO customizado.
- A fusão multimodal usa regras heurísticas; não foi treinado um modelo estatístico de fusão nesta fase.
- Para uma avaliação conclusiva, a próxima iteração deve: (1) versionar ou referenciar de forma segura mídias autorizadas e seus manifestos; (2) executar um teste separado e preservado contra dados de treino; (3) publicar precisão, recall e mAP por classe, além de matriz de confusão; e (4) anexar exemplos anonimizados de acertos e falhas, com revisão humana documentada.
