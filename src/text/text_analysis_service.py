import json
from pathlib import Path
from src.domain.text_models import Transcript
from src.text.text_analyzer import TextAnalyzer

class TextAnalysisService:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.analyzer = TextAnalyzer()

    def execute(self, transcript: Transcript) -> dict:
        output_file = self.output_dir / "text_analysis.json"
        
        try:
            analysis = self.analyzer.analyze(transcript)
            
            result_dict = analysis.to_dict()
            
            result = {
                "status": "concluída",
                "analise": result_dict
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
                
            return result
        except Exception as e:
            result = {
                "status": "erro",
                "motivo": str(e)
            }
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
            raise
