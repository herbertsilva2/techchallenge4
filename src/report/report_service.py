from pathlib import Path
from typing import Tuple
from src.domain.report_models import ReportData
from src.report.report_generator import ReportGenerator

class ReportService:
    """Serviço para gerenciar a geração de relatórios."""

    def __init__(self, generator: ReportGenerator):
        self.generator = generator

    def execute(self, data: ReportData) -> Tuple[Path, Path]:
        """Executa a geração do relatório delegando para o ReportGenerator."""
        return self.generator.generate(data)
