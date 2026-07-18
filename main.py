import sys
import argparse
from pathlib import Path
from src.services.pipeline_service import PipelineService

def main():
    parser = argparse.ArgumentParser(description="Processa um vídeo para o Tech Challenge Fase 4")
    parser.add_argument("video_path", type=str, help="Caminho para o arquivo de vídeo")
    args = parser.parse_args()

    video_path = Path(args.video_path)
    
    if not video_path.exists():
        print(f"Erro: Arquivo não encontrado: {video_path}")
        sys.exit(1)

    print(f"Iniciando processamento do vídeo: {video_path}")
    
    pipeline_service = PipelineService()
    
    def progress_callback(step, progress, msg):
        print(f"[{progress*100:3.0f}%] {step.value}: {msg}")

    result = pipeline_service.execute(
        video_path=video_path,
        progress_callback=progress_callback
    )

    print("\n=================================")
    print(f"PROCESSAMENTO CONCLUÍDO - Status: {result.status.upper()}")
    
    if result.status == "failed":
        print("Erros Críticos:")
        for err in result.errors:
            print(f"- {err}")
        print("=================================")
        sys.exit(1)

    if result.messages:
        print("Mensagens e Alertas:")
        for msg in result.messages:
            print(f"- {msg}")
            
    if result.report_json_path and result.report_md_path:
        print(f"Relatório JSON: {result.report_json_path}")
        print(f"Relatório MD: {result.report_md_path}")
        
    print("=================================")
    sys.exit(0)

if __name__ == "__main__":
    main()
