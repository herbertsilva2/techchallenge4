import json
from pathlib import Path
from typing import Dict, Any

class ReportLoadError(Exception):
    pass

class InvalidReportError(Exception):
    pass

class ResultLoader:
    def __init__(self):
        pass

    def load_report(self, report_json_path: str) -> Dict[str, Any]:
        path = Path(report_json_path)
        if not path.exists():
            raise ReportLoadError(f"Report file not found: {report_json_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise InvalidReportError(f"Failed to parse JSON: {e}")
        except Exception as e:
            raise ReportLoadError(f"Error reading report: {e}")

        # Ensure required fields exist based on instructions:
        # report.json: execution, modalities, fusion, ethical_warning
        # Wait, the current ReportData only generates: timestamp, video_info, modalities, fusion_result, ethical_warning.
        # "execution" might be related to metadata or timestamp. Let's validate the current schema.
        
        required_fields = ['modalities', 'fusion_result', 'ethical_warning']
        # The prompt says: "report.json: - execution; - modalities; - fusion; - ethical_warning."
        # If execution is meant, it could be execution context. I will check for 'timestamp' as execution representation or 'execution_times' if that was added.
        
        for field in required_fields:
            if field not in data:
                raise InvalidReportError(f"Missing required field in report: {field}")
                
        # If they meant execution info, I'll allow both 'execution' or 'timestamp' just in case.
        if 'execution' not in data and 'timestamp' not in data:
            raise InvalidReportError("Missing required field in report: execution/timestamp")

        return data

    def load_markdown(self, report_md_path: str) -> str:
        path = Path(report_md_path)
        if not path.exists():
            raise ReportLoadError(f"Markdown report not found: {report_md_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise ReportLoadError(f"Error reading markdown report: {e}")
