# Documentação de Arquitetura

Este documento descreve a organização de alto nível do sistema Tech Challenge Fase 4.

## Diagrama de Componentes

O sistema adota uma separação de responsabilidades inspirada em Clean Architecture, onde os processos de extração pesada operam na borda e reportam para os modelos de domínio imutáveis no núcleo (Fusion Engine).

```mermaid
graph TD
    subgraph UI Layer
      StreamlitApp[Dashboard Streamlit]
      CLI[CLI Main]
    end

    subgraph Orchestration Layer
      PS[Pipeline Service]
      DS[Dashboard Service]
    end

    subgraph Analysis Services
      VS[Video/YOLO/Face Service]
      AS[Audio/Azure Service]
      TS[Text Analysis Service]
    end

    subgraph Core Logic
      FE[Fusion Engine]
      RM[Risk Rules]
    end

    StreamlitApp --> DS
    CLI --> PS
    DS --> PS
    PS --> VS
    PS --> AS
    AS --> TS
    VS --> FE
    TS --> FE
    FE --> RM
```

## Decisões de Design
1. **Isolamento de Nuvem**: Todas as requisições ao Azure Speech estão confinadas ao `azure_speech_transcriber.py`.
2. **Interfaces Únicas**: Módulos de detecção gráfica não conhecem texto, o `Fusion Engine` é o único a conhecer ambos.
