# Relatório Técnico: MVP Multimodal

## Introdução
Este documento detalha as decisões técnicas, a arquitetura e as limitações do MVP desenvolvido para o Tech Challenge Fase 4.

## Arquitetura do Sistema
O sistema adota uma arquitetura modular focada em pipelines de processamento, onde dados extraídos de um vídeo (frames e áudio) são analisados por diferentes motores de inferência.

### Módulos Principais
1. **Video/Visual (OpenCV, MediaPipe, YOLOv8):** Extrai frames, identifica rostos e detecta objetos de interesse.
2. **Áudio/Transcrição (Azure Speech):** Extrai áudio e obtém a transcrição do conteúdo falado.
3. **Análise Textual:** Classifica o texto transcrito em categorias predefinidas.
4. **Fusão Multimodal:** Consistência e ponderação de evidências baseada em regras determinísticas simples.

## Restrições e Avisos
O sistema identifica combinações de sinais potencialmente relevantes para apoio à triagem humana.
Não se trata de uma ferramenta diagnóstica. Todo o output gerado deve ser analisado por um profissional capacitado para tomada de decisão. A validação das evidências em múltiplos contextos requer avaliação humana especializada.

## Limitações do MVP
- O sistema opera offline, mas a transcrição depende de credenciais da Azure ativas e conectividade com a internet.
- A detecção YOLO depende de treinamento customizado para eficácia na classe definida para o MVP (`hand_on_face`). A preparação e validação do dataset foram concluídas na etapa atual, porém o treinamento será realizado em etapas futuras.
- A fusão multimodal atual emprega regras heurísticas. Um modelo de aprendizado estatístico não foi treinado para esse fim devido às restrições desta fase.

## Implementação do Dashboard Streamlit
Nesta fase, a orquestração terminal (`main.py`) foi adaptada em um ambiente visual interativo (`app.py`), isolando lógicas de fluxo de dados na camada `src/services/` (DashboardService, PipelineService, ResultLoader).

### Principais Desafios Superados
1. **Processamento Síncrono e Limites Seguros**: Streamlit executa cada interação de forma síncrona, bloqueando a thread principal. Foi necessário instanciar callbacks que atualizassem elementos (`st.empty`, `st.progress`) nativamente. Adicionalmente, limitamos os arquivos em 200MB (sugerindo $\le$ 3 minutos) para evitar estourar o limite padrão do servidor ou travar o socket.
2. **Tolerância a Falhas (Fallback)**: O `PipelineResult` foi estendido com a propriedade `status` (`completed`, `partial`, `failed`). Isso garante que ausência de credenciais Azure, YOLO no modo `yolov8n.pt` ou vídeos mudos não inviabilizem a análise visual ou textual paralela, permitindo ao DashboardService exibir alertas ao invés de interrupção drástica.
3. **Gerenciamento de Arquivos em Memória**: O `DashboardService` emprega `tempfile` para hospedar o buffer de vídeo sem persistir dados, garantindo sanitização por *uuid* e exclusão após processamento, alinhado às diretrizes de privacidade.

A limitação notada foi a remoção temporária do gráfico de pizza de contribuição multimodal (pois no momento o sistema depende majoritariamente de pesos textuais agregados na ausência da paridade preditiva estrita do áudio individual). Pode ser iniciado o frontend com: `streamlit run app.py`.
