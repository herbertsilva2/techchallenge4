import tempfile
import uuid
import os
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, Callable

from src.services.pipeline_service import PipelineService
from src.services.result_loader import ResultLoader
from src.domain.processing_models import PipelineResult, ProcessingStep

MAX_UPLOAD_SIZE_BYTES = 200 * 1024 * 1024  # 200 MB
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv'}
ALLOWED_AUDIO_EXTENSIONS = {'.wav', '.mp3', '.m4a', '.ogg'}
ALLOWED_EXTENSIONS = ALLOWED_VIDEO_EXTENSIONS | ALLOWED_AUDIO_EXTENSIONS

class DashboardService:
    def __init__(self):
        self.pipeline_service = PipelineService()
        self.result_loader = ResultLoader()

    def validate_upload(self, filename: str, size_bytes: int) -> Tuple[bool, Optional[str]]:
        if size_bytes > MAX_UPLOAD_SIZE_BYTES:
            return False, f"O arquivo excede o limite de 200MB ({size_bytes / (1024*1024):.2f}MB)."
        
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            return False, f"Extensão não permitida: {ext}. Permitidas: {', '.join(ALLOWED_EXTENSIONS)}."
            
        return True, None

    def process_upload(self, uploaded_bytes: bytes, extension: str, callback: Callable[[ProcessingStep, float, str], None]) -> PipelineResult:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            
            # Generate random internal name
            internal_filename = f"{uuid.uuid4().hex}{extension}"
            temp_video_path = temp_dir_path / internal_filename
            
            with open(temp_video_path, "wb") as f:
                f.write(uploaded_bytes)
                
            # Execute pipeline
            result = self.pipeline_service.execute(
                temp_video_path,
                progress_callback=callback,
                input_is_audio=extension.lower() in ALLOWED_AUDIO_EXTENSIONS
            )
            
            # Note: the pipeline writes outputs to OUTPUTS_DIR, not temp_dir, 
            # so the report JSON and MD files are persistent.
            return result

    def load_generated_results(self, pipeline_result: PipelineResult) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        report_data = None
        report_md = None
        
        if pipeline_result.report_json_path:
            try:
                report_data = self.result_loader.load_report(pipeline_result.report_json_path)
            except Exception as e:
                pipeline_result.errors.append(f"Failed to load JSON report: {e}")
                
        if pipeline_result.report_md_path:
            try:
                report_md = self.result_loader.load_markdown(pipeline_result.report_md_path)
            except Exception as e:
                pipeline_result.errors.append(f"Failed to load MD report: {e}")
                
        return report_data, report_md

    def build_view_data(self, pipeline_result: PipelineResult, report_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        # Transforms the pipeline result and report data into a format easy for the UI to consume.
        # This keeps the UI decoupled from complex domain parsing if necessary.
        
        view_data = {
            "status": pipeline_result.status,
            "errors": pipeline_result.errors,
            "messages": pipeline_result.messages,
            "execution_times": [t.to_dict() for t in pipeline_result.execution_times],
        }
        
        if report_data:
            view_data["report"] = report_data
            
        return view_data
