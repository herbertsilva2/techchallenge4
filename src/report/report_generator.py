import json
import os
from pathlib import Path
from typing import Tuple
from src.domain.report_models import ReportData

class ReportGenerator:
    """Gera relatórios em JSON e Markdown."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, data: ReportData) -> Tuple[Path, Path]:
        """Gera os relatórios e retorna os caminhos dos arquivos JSON e Markdown."""
        json_path = self.output_dir / "report.json"
        md_path = self.output_dir / "report.md"

        self._generate_json(data, json_path)
        self._generate_markdown(data, md_path)

        return json_path, md_path

    def _generate_json(self, data: ReportData, path: Path):
        """Gera o arquivo JSON."""
        # Ensure we only serialize standard types, not arbitrary Python objects
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data.to_dict(), f, indent=4, ensure_ascii=False)

    def _generate_markdown(self, data: ReportData, path: Path):
        """Gera o arquivo Markdown."""
        lines = []
        lines.append("# Relatório de Análise Multimodal")
        lines.append(f"**Data/Hora:** {data.timestamp}\n")

        lines.append("## Aviso Ético")
        lines.append(f"> {data.ethical_warning}\n")

        if data.video_info:
            lines.append("## Informações do Vídeo")
            lines.append(f"- Resolução: {data.video_info.width}x{data.video_info.height}")
            lines.append(f"- FPS: {data.video_info.fps}")
            lines.append(f"- Duração: {data.video_info.duration_seconds}s")
            lines.append(f"- Total de Frames: {data.video_info.frame_count}\n")

        lines.append("## Status das Modalidades")
        for mod_name, mod_status in data.modalities.items():
            lines.append(f"### {mod_name.upper()}")
            lines.append(f"- **Status:** {mod_status.status}")
            if mod_status.reason:
                lines.append(f"- **Motivo:** {mod_status.reason}")
            if mod_status.details:
                lines.append("- **Detalhes:**")
                for k, v in mod_status.details.items():
                    lines.append(f"  - {k}: {v}")
            lines.append("")

        if data.transcript:
            lines.append("## Transcrição")
            lines.append(f"**Provedor:** {data.speech_provider or 'N/A'}")
            lines.append(f"**Idioma:** {data.language or 'N/A'}")
            lines.append(f"**Status:** {data.speech_status or 'N/A'}\n")
            lines.append(f"{data.transcript}\n")

        if data.audio_analysis:
            lines.append("## Indicadores Vocais (não diagnósticos)")
            lines.append("> Estes indicadores acústicos não permitem inferir ou diagnosticar ansiedade, trauma, fadiga vocal ou qualquer condição de saúde.\n")
            quality = data.audio_analysis.quality or {}
            lines.append(f"- **Qualidade:** {quality.get('status', 'N/A')}")
            if quality.get('reason'):
                lines.append(f"- **Observação:** {quality['reason']}")
            metrics = data.audio_analysis.vocal_metrics
            if metrics:
                for label, value in metrics.to_dict().items():
                    if value is not None:
                        lines.append(f"- **{label}:** {value}")
            lines.append("")

        if data.fusion_result:
            lines.append("## Resultado da Fusão")
            lines.append(f"- **Nível de Risco:** {data.fusion_result.risk_level.value}")
            lines.append(f"- **Score:** {data.fusion_result.score}\n")

            if data.fusion_result.evidences:
                lines.append("### Evidências")
                for e in data.fusion_result.evidences:
                    lines.append(f"- [{e.modality}] {e.description} (Confiança: {e.confidence:.2f})")
                lines.append("")
            
            if data.fusion_result.justifications:
                lines.append("### Justificativas")
                for j in data.fusion_result.justifications:
                    lines.append(f"- {j}")
                lines.append("")

            if data.fusion_result.recommendations:
                lines.append("### Recomendações")
                for r in data.fusion_result.recommendations:
                    lines.append(f"- {r}")
                lines.append("")

        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
