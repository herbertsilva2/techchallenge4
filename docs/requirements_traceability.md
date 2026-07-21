# Matriz de Rastreabilidade de Requisitos

Abaixo está o estado de entrega dos requisitos definidos para o MVP Multimodal:

| Requisito / Funcionalidade | Status | Observações |
| :--- | :--- | :--- |
| **Análise de Vídeo** | Atendido | Framework base operante. |
| **Detecção Facial** | Atendido | MediaPipe integrado com sucesso para rastreio de faces por frame. |
| **Extração de Áudio** | Atendido | Extração via ffmpeg e pydub validada. |
| **Azure Speech** | Parcialmente atendido | Código de integração pronto, mas pendente de execução real com credenciais válidas na nuvem. |
| **Análise Textual** | Atendido | Extração de categorias e cálculo de risco funcionando simuladamente nas dependências e dados transcritos. |
| **Fusão Multimodal** | Atendido | Motor de regras e agregação de score e evidências construído e testado. |
| **YOLOv8 Customizado** | Parcialmente atendido | Estrutura, validação e documentação do dataset para a classe `hand_on_face` finalizados. O pipeline usa MediaPipe Hands + Face Mesh para sinalizar proximidade persistente mão-rosto; isso não substitui a validação do YOLO customizado. |
| **Relatório Automático** | Atendido | Geração de report consolidado em JSON e Markdown configurada. Validação completa nos testes. |
| **Dashboard** | Atendido | Interface gráfica Streamlit validada, abas, fallbacks, limites. |
| **Vídeo de Demonstração** | Não atendido | Pendente, não gravado/registrado ainda. |
| **Execução Geral Atual** | Parcial | Processamento funcional porém bloqueado parcialmente pela ausência de credenciais Azure e treinamento do modelo YOLO. |

## Refatoração e Dashboard (Fase Final)
- [x] O `PipelineResult` foi atualizado sem duplicidade de modelos.
- [x] Refatoração da arquitetura de serviços em `src/services/` (`pipeline_service.py`, `dashboard_service.py`, `result_loader.py`).
- [x] Construção de `app.py` aderente às restrições sem dependência cíclica, modularizado por tabs em `src/ui/components/`.
- [x] Atualização da documentação sobre falhas graciosas, restrições e comportamento UI.
