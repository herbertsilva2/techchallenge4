# Documentação do Pipeline Multimodal

O Pipeline Multimodal é responsável pelo processamento assíncrono dos artefatos (vídeo) de ponta a ponta.

## Fluxo de Processamento

```mermaid
sequenceDiagram
    participant User
    participant PipelineService
    participant VideoLoader
    participant AzureSpeech
    participant TextAnalyzer
    participant FusionEngine

    User->>PipelineService: process(video.mp4)
    PipelineService->>VideoLoader: extract_audio()
    PipelineService->>VideoLoader: extract_frames()
    
    par Visão
        VideoLoader->>VideoLoader: MediaPipe Face
        VideoLoader->>VideoLoader: YOLO Objects
    and Áudio
        VideoLoader-->>AzureSpeech: audio.wav
        AzureSpeech-->>TextAnalyzer: Transcript
        TextAnalyzer-->>TextAnalyzer: Sentiment Analysis
    end
    
    PipelineService->>FusionEngine: process_fusion(vision, text)
    FusionEngine-->>User: ReportJSON
```

## Etapas de Falha
Se a API Azure estiver inacessível, o status do componente transcrição entra em `failed` (ou usa um fallback) mas o Pipeline continua a execução da visão de forma isolada, gerando um relatório em modo *PARTIAL*.
