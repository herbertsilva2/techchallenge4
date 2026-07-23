import streamlit as st
import json
from src.services.dashboard_service import DashboardService, CONSENT_NOTICE
from src.domain.processing_models import ProcessingStep
from src.ui.components.video_player import render_video_player
from src.ui.components.metrics_panel import render_metrics_panel
from src.ui.components.visual_tab import render_visual_tab
from src.ui.components.audio_text_tab import render_audio_text_tab
from src.ui.components.fusion_tab import render_fusion_tab
from src.ui.components.report_tab import render_report_tab
from src.ui.components.about_tab import render_about_tab
import uuid
from src.ui.components.theme import apply_apple_theme

# Configuração da Página
st.set_page_config(page_title="Tech Challenge 4 - Multimodal", layout="wide")
apply_apple_theme()

# Inicialização de Serviços
@st.cache_resource
def get_dashboard_service():
    return DashboardService()

dashboard_service = get_dashboard_service()

# Estado da Sessão
if 'uploaded_media_bytes' not in st.session_state:
    st.session_state.uploaded_media_bytes = None
if 'uploaded_media_extension' not in st.session_state:
    st.session_state.uploaded_media_extension = None
if 'uploaded_media_name' not in st.session_state:
    st.session_state.uploaded_media_name = None
if 'uploaded_media_is_audio' not in st.session_state:
    st.session_state.uploaded_media_is_audio = False
if 'processing_completed' not in st.session_state:
    st.session_state.processing_completed = False
if 'pipeline_result' not in st.session_state:
    st.session_state.pipeline_result = None
if 'report_data' not in st.session_state:
    st.session_state.report_data = None
if 'report_markdown' not in st.session_state:
    st.session_state.report_markdown = None
if 'processing_error' not in st.session_state:
    st.session_state.processing_error = None
if 'execution_id' not in st.session_state:
    st.session_state.execution_id = None
if 'consent_given' not in st.session_state:
    st.session_state.consent_given = False

# Cabeçalho e Aviso Ético
st.title("Sistema Multimodal de Apoio à Triagem")
st.subheader("Tech Challenge Fase 4")
st.warning("ATENÇÃO: Este sistema é um protótipo educacional para demonstração de IA multimodal. Não possui validade clínica.")

# Área de Upload
uploaded_file = st.file_uploader("Selecione vídeo ou áudio para análise", type=['mp4', 'avi', 'mov', 'mkv', 'wav', 'mp3', 'm4a', 'ogg'])

if uploaded_file is not None:
    # Validate Upload
    is_valid, error_msg = dashboard_service.validate_upload(uploaded_file.name, uploaded_file.size)
    if not is_valid:
        st.error(error_msg)
    else:
        # Se for um novo arquivo, reseta o estado
        if (
            st.session_state.uploaded_media_bytes != uploaded_file.getvalue()
            or st.session_state.uploaded_media_name != uploaded_file.name
        ):
            st.session_state.uploaded_media_bytes = uploaded_file.getvalue()
            st.session_state.uploaded_media_name = uploaded_file.name
            import pathlib
            st.session_state.uploaded_media_extension = pathlib.Path(uploaded_file.name).suffix
            st.session_state.uploaded_media_is_audio = st.session_state.uploaded_media_extension.lower() in {'.wav', '.mp3', '.m4a', '.ogg'}
            st.session_state.processing_completed = False
            st.session_state.pipeline_result = None
            st.session_state.report_data = None
            st.session_state.report_markdown = None
            st.session_state.processing_error = None
            st.session_state.execution_id = str(uuid.uuid4())
            st.session_state.consent_given = False

        if st.session_state.uploaded_media_is_audio:
            st.audio(st.session_state.uploaded_media_bytes)
        else:
            render_video_player(st.session_state.uploaded_media_bytes, st.session_state.uploaded_media_extension)

        st.info(CONSENT_NOTICE)
        consent_given = st.checkbox(
            "Li o aviso e concordo com o processamento temporário deste arquivo.",
            key="consent_given",
        )

        if not st.session_state.processing_completed and not st.session_state.processing_error:
            action_label = "Processar Áudio" if st.session_state.uploaded_media_is_audio else "Processar Vídeo"
            if st.button(action_label, disabled=not consent_given):
                progress_bar = st.progress(0.0)
                status_text = st.empty()

                def progress_callback(step: ProcessingStep, progress: float, msg: str):
                    progress_bar.progress(progress)
                    status_text.text(f"[{step.value}] {msg}")

                try:
                    result = dashboard_service.process_upload(
                        st.session_state.uploaded_media_bytes,
                        st.session_state.uploaded_media_extension,
                        progress_callback
                    )
                    
                    if result.status == 'failed':
                        st.session_state.processing_error = result.errors[0] if result.errors else "Erro crítico desconhecido"
                    else:
                        st.session_state.pipeline_result = result
                        report_data, report_md = dashboard_service.load_generated_results(result)
                        st.session_state.report_data = report_data
                        st.session_state.report_markdown = report_md
                        st.session_state.processing_completed = True
                        
                except Exception as e:
                    st.session_state.processing_error = str(e)

        if st.session_state.processing_error:
            st.error(f"Erro durante o processamento: {st.session_state.processing_error}")

        if st.session_state.processing_completed:
            if st.session_state.pipeline_result and st.session_state.pipeline_result.status == 'partial':
                st.warning("Processamento concluído com restrições (PARTIAL). O sistema continua operando com as modalidades disponíveis.")
            else:
                st.success("Processamento síncrono concluído com sucesso!")

            alert = getattr(st.session_state.pipeline_result, "alert_notification", None)
            if alert:
                if alert.status == "sent":
                    st.success(f"Alerta por e-mail enviado à equipe médica (ID: {alert.alert_id[:8]}).")
                elif alert.status == "simulated":
                    st.info(f"Alerta por e-mail simulado e registrado em {alert.outbox_path}.")
                else:
                    st.error(f"Falha ao enviar alerta por e-mail: {alert.error}")
            
            # Painel de Métricas (usando dados extraídos do report_data ou result_view_data)
            view_data = dashboard_service.build_view_data(st.session_state.pipeline_result, st.session_state.report_data)
            
            if st.session_state.report_data and 'video_info' in st.session_state.report_data:
                render_metrics_panel(st.session_state.report_data['video_info'])
            
            # Botões de Download
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.session_state.report_data:
                    json_str = json.dumps(st.session_state.report_data, indent=2, ensure_ascii=False)
                    st.download_button(
                        label="Download JSON",
                        data=json_str.encode('utf-8'),
                        file_name="report.json",
                        mime="application/json"
                    )
            with col2:
                if st.session_state.report_markdown:
                    st.download_button(
                        label="Download Markdown",
                        data=st.session_state.report_markdown.encode('utf-8'),
                        file_name="report.md",
                        mime="text/markdown"
                    )
            with col3:
                # O fusion_result_json pode ser gerado a partir do fusion_result no pipeline
                if st.session_state.pipeline_result and st.session_state.pipeline_result.fusion_result:
                    fusion_str = json.dumps(st.session_state.pipeline_result.fusion_result.to_dict(), indent=2, ensure_ascii=False)
                    st.download_button(
                        label="Download Fusion Result",
                        data=fusion_str.encode('utf-8'),
                        file_name="fusion_result.json",
                        mime="application/json"
                    )
            
            # Abas do Dashboard
            st.markdown("---")
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["Visual", "Áudio/Texto", "Fusão", "Relatório", "Sobre"])
            
            with tab1:
                render_visual_tab(st.session_state.report_data)
            with tab2:
                render_audio_text_tab(st.session_state.report_data)
            with tab3:
                render_fusion_tab(st.session_state.report_data)
            with tab4:
                render_report_tab(st.session_state.report_markdown)
            with tab5:
                render_about_tab()
