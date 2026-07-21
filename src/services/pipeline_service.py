import time
from pathlib import Path
from typing import Callable, Optional
from datetime import datetime

from src.utils.config import AZURE_SPEECH_KEY, AZURE_SPEECH_REGION, AZURE_SPEECH_LANGUAGE, AZURE_SPEECH_ENDPOINT, OUTPUTS_DIR
from src.domain.processing_models import PipelineResult, ProcessingStep, ExecutionTime
from src.domain.text_models import Transcript, TextAnalysis
from src.domain.video_models import VideoInfo
from src.domain.report_models import ReportData, ModalityStatus

from src.video.video_loader import VideoLoader
from src.video.video_metadata import VideoMetadata
from src.video.frame_extractor import FrameExtractor
from src.video.audio_extractor import AudioExtractor
from src.video.frame_analyzer import FrameAnalyzer
from src.video.yolo_detector import YOLODetector
from src.audio.azure_speech_transcriber import AzureSpeechTranscriber
from src.audio.transcription_service import TranscriptionService
from src.text.text_analysis_service import TextAnalysisService
from src.fusion.fusion_engine import FusionEngine
from src.fusion.fusion_service import FusionService
from src.report.report_generator import ReportGenerator
from src.report.report_service import ReportService

ProgressCallback = Callable[[ProcessingStep, float, str], None]

class PipelineService:
    def __init__(self):
        pass

    def _safe_callback(self, callback: Optional[ProgressCallback], step: ProcessingStep, progress: float, msg: str, result: PipelineResult):
        if callback:
            try:
                callback(step, max(0.0, min(1.0, progress)), msg)
            except Exception as e:
                result.messages.append(f"Callback error: {str(e)}")

    def execute(self, video_path: Path, progress_callback: Optional[ProgressCallback] = None, output_dir: Optional[Path] = None) -> PipelineResult:
        result = PipelineResult(messages=[], errors=[], execution_times=[])
        out_dir = output_dir or OUTPUTS_DIR

        # Create subdirectories if they don't exist
        transcription_output_dir = out_dir / "transcription"
        text_analysis_output_dir = out_dir / "text_analysis"
        fusion_output_dir = out_dir / "fusion"
        report_output_dir = out_dir / "report"

        transcription_output_dir.mkdir(parents=True, exist_ok=True)
        text_analysis_output_dir.mkdir(parents=True, exist_ok=True)
        fusion_output_dir.mkdir(parents=True, exist_ok=True)
        report_output_dir.mkdir(parents=True, exist_ok=True)

        modalities = {
            'video': ModalityStatus('not_executed', reason='Iniciando processamento...'),
            'audio': ModalityStatus('not_executed', reason='Iniciando processamento...'),
            'transcription': ModalityStatus('not_executed', reason='Aguardando áudio...'),
            'text_analysis': ModalityStatus('not_executed', reason='Aguardando transcrição...'),
            'yolo': ModalityStatus('not_executed', reason='Iniciando análise visual...'),
            'fusion': ModalityStatus('not_executed', reason='Aguardando finalização das análises...')
        }

        try:
            # 1. Validation & Metadata
            step = ProcessingStep.VIDEO_EXTRACTION
            result.current_step = step
            self._safe_callback(progress_callback, step, 0.0, "Validando vídeo e extraindo metadados...", result)
            start_time = time.time()
            
            loader = VideoLoader(str(video_path))
            valid_path = loader.validate()
            metadata = VideoMetadata.get_metadata(str(valid_path))
            result.video_info = VideoInfo(
                width=metadata.width, height=metadata.height, fps=metadata.fps,
                frame_count=metadata.frame_count, duration_seconds=metadata.duration_seconds, codec=metadata.codec
            )
            
            # 2. Extract frames
            self._safe_callback(progress_callback, step, 0.3, "Extraindo frames...", result)
            frame_ext = FrameExtractor(str(valid_path), str(out_dir))
            frames_extracted = frame_ext.extract_frames(interval=30)
            
            # 3. Extract audio
            step = ProcessingStep.AUDIO_EXTRACTION
            result.current_step = step
            self._safe_callback(progress_callback, step, 0.5, "Extraindo áudio...", result)
            audio_ext = AudioExtractor(str(valid_path), str(out_dir))
            audio_path = audio_ext.extract_audio()

            result.execution_times.append(ExecutionTime(step=ProcessingStep.VIDEO_EXTRACTION, duration_seconds=time.time() - start_time))
            result.execution_times.append(ExecutionTime(step=ProcessingStep.AUDIO_EXTRACTION, duration_seconds=time.time() - start_time))

            modalities['audio'] = ModalityStatus(
                'completed' if audio_path else 'unavailable',
                reason=None if audio_path else 'O vídeo processado não possui faixa de áudio.',
                details={'path': audio_path} if audio_path else {}
            )

            # 4. Analyze frames
            step = ProcessingStep.VIDEO_ANALYSIS
            result.current_step = step
            start_time = time.time()
            self._safe_callback(progress_callback, step, 0.6, "Analisando frames (MediaPipe + YOLO)...", result)
            
            yolo_detector = YOLODetector()
            yolo_info = yolo_detector.get_info()
            
            visual_detector_ready = yolo_info.get('custom_model_trained') or yolo_info.get('specialized_gesture_detector')
            modalities['yolo'] = ModalityStatus(
                'completed' if visual_detector_ready else 'partial',
                reason=None if yolo_info.get('custom_model_trained') else 'Detector pré-treinado MediaPipe usado',
                details=yolo_info
            )

            analyzer = FrameAnalyzer(str(out_dir), str(out_dir), yolo_detector=yolo_detector)
            video_analysis = analyzer.analyze_frames()

            if video_analysis:
                result.video_analysis = video_analysis
                # Face missing shouldn't fail
                if video_analysis.faces_detected == 0:
                    modalities['video'] = ModalityStatus('partial', reason='Nenhum rosto detectado.', details={
                        'frames_analyzed': video_analysis.frames_analyzed,
                        'faces_detected': video_analysis.faces_detected,
                        'objects_detected': video_analysis.objects_detected
                    })
                else:
                    modalities['video'] = ModalityStatus('completed', details={
                        'frames_analyzed': video_analysis.frames_analyzed,
                        'faces_detected': video_analysis.faces_detected,
                        'objects_detected': video_analysis.objects_detected
                    })
            else:
                modalities['video'] = ModalityStatus('partial', reason='Erro na análise de frames.')

            result.execution_times.append(ExecutionTime(step=step, duration_seconds=time.time() - start_time))

            # 5. Transcription
            step = ProcessingStep.AUDIO_ANALYSIS
            result.current_step = step
            start_time = time.time()
            
            transcription_result = None
            if not audio_path:
                modalities['transcription'] = ModalityStatus('unavailable', reason='Vídeo sem áudio, impossível transcrever.')
            elif not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
                self._safe_callback(progress_callback, step, 0.7, "Credenciais Azure ausentes. Pulando transcrição...", result)
                modalities['transcription'] = ModalityStatus('partial', reason='Credenciais Azure não configuradas.')
            else:
                self._safe_callback(progress_callback, step, 0.7, "Transcrevendo áudio...", result)
                try:
                    transcriber = AzureSpeechTranscriber(
                        key=AZURE_SPEECH_KEY,
                        region=AZURE_SPEECH_REGION,
                        language=AZURE_SPEECH_LANGUAGE,
                        endpoint=AZURE_SPEECH_ENDPOINT
                    )
                    transcription_service = TranscriptionService(
                        transcriber=transcriber, 
                        output_dir=str(transcription_output_dir)
                    )
                    transcription_result = transcription_service.execute(audio_path)
                    status_str = transcription_result.get("status")
                    
                    if status_str == "concluída":
                        modalities['transcription'] = ModalityStatus('completed', details={
                            'language': transcription_result.get('idioma', 'pt-BR'),
                            'segments': len(transcription_result.get('segmentos', []))
                        })
                    else:
                        modalities['transcription'] = ModalityStatus('partial', reason=transcription_result.get('erro', 'Erro desconhecido.'))
                        transcription_result = None
                except Exception as e:
                    modalities['transcription'] = ModalityStatus('partial', reason=str(e))
                    result.messages.append(f"Azure API Exception: {e}")

            result.execution_times.append(ExecutionTime(step=step, duration_seconds=time.time() - start_time))

            # 6. Text Analysis
            step = ProcessingStep.TEXT_ANALYSIS
            result.current_step = step
            start_time = time.time()

            text_analysis_result = None
            if transcription_result and "transcript_modelo" in transcription_result:
                self._safe_callback(progress_callback, step, 0.8, "Analisando texto...", result)
                try:
                    transcript = Transcript.from_dict(transcription_result['transcript_modelo'])
                    result.transcript = transcript
                    text_service = TextAnalysisService(str(text_analysis_output_dir))
                    text_analysis_result_dict = text_service.execute(transcript)
                    status_str = text_analysis_result_dict.get("status")
                    
                    if status_str == "concluída":
                        text_analysis_result = TextAnalysis.from_dict(text_analysis_result_dict["analise"])
                        result.text_analysis = text_analysis_result
                        modalities['text_analysis'] = ModalityStatus('completed', details={
                            'sentences_analyzed': len(text_analysis_result.transcript.sentences)
                        })
                    else:
                        modalities['text_analysis'] = ModalityStatus('partial', reason='Falha na análise textual.')
                except Exception as e:
                    modalities['text_analysis'] = ModalityStatus('partial', reason=str(e))
            else:
                modalities['text_analysis'] = ModalityStatus('not_executed', reason='Transcrição indisponível.')

            result.execution_times.append(ExecutionTime(step=step, duration_seconds=time.time() - start_time))

            # 7. Fusion
            step = ProcessingStep.FUSION
            result.current_step = step
            start_time = time.time()
            self._safe_callback(progress_callback, step, 0.9, "Executando fusão multimodal...", result)
            
            fusion_engine = FusionEngine()
            fusion_service = FusionService(str(fusion_output_dir), fusion_engine)
            
            audio_analysis = None
            fusion_result_obj = fusion_service.execute(
                video=result.video_analysis,
                audio=audio_analysis,
                text=text_analysis_result
            )
            result.fusion_result = fusion_result_obj
            modalities['fusion'] = ModalityStatus('completed', details={
                'risk_level': fusion_result_obj.risk_level.value,
                'score': fusion_result_obj.score
            })
            result.execution_times.append(ExecutionTime(step=step, duration_seconds=time.time() - start_time))

            # 8. Final Report
            self._safe_callback(progress_callback, step, 0.95, "Gerando relatórios...", result)
            report_data = ReportData(
                timestamp=datetime.utcnow().isoformat() + "Z",
                video_info=result.video_info,
                modalities=modalities,
                fusion_result=fusion_result_obj,
                ethical_warning="ATENÇÃO: O sistema identifica combinações de sinais potencialmente relevantes para apoio à triagem humana. Esta ferramenta não substitui a avaliação de um profissional de saúde qualificado.",
                transcript=result.transcript.full_text if getattr(result, 'transcript', None) else None,
                speech_provider="Azure AI Speech" if transcription_result else None,
                language=transcription_result.get('idioma', 'pt-BR') if transcription_result else None,
                speech_status=modalities['transcription'].status
            )

            report_gen = ReportGenerator(str(report_output_dir))
            report_service = ReportService(report_gen)
            
            json_path, md_path = report_service.execute(report_data)
            result.report_json_path = json_path
            result.report_md_path = md_path

            self._safe_callback(progress_callback, step, 1.0, "Processamento concluído", result)
            yolo_demo_mode = not yolo_info.get('custom_model_trained') and not yolo_info.get('specialized_gesture_detector')
            azure_partial = modalities.get('transcription') and modalities['transcription'].status == 'partial'

            if azure_partial or yolo_demo_mode:
                result.status = "partial"
            else:
                result.status = "completed"

        except Exception as e:
            result.status = "failed"
            result.errors.append(str(e))
            self._safe_callback(progress_callback, ProcessingStep.FUSION, 1.0, f"Falha crítica: {str(e)}", result)

        return result
