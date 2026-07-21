import streamlit as st
from typing import Dict, Any

def render_audio_text_tab(report_data: Dict[str, Any]):
    st.header("Análise de Áudio e Texto")
    
    modalities = report_data.get('modalities', {})
    audio_status = modalities.get('audio', {})
    transcription_status = modalities.get('transcription', {})
    text_status = modalities.get('text_analysis', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Áudio")
        st.write(f"Status: {audio_status.get('status', 'N/A')}")
        if audio_status.get('reason'):
            st.info(audio_status.get('reason'))
            
        st.subheader("Transcrição")
        st.write(f"Status: {transcription_status.get('status', 'N/A')}")
        if transcription_status.get('status') == 'partial' and 'Credenciais' in str(transcription_status.get('reason', '')):
            st.warning("Azure Speech não executado por ausência de credenciais.")
        if transcription_status.get('reason'):
            st.info(transcription_status.get('reason'))
        if transcription_status.get('details'):
            st.json(transcription_status.get('details'))
            
        if report_data.get('transcript'):
            st.markdown("---")
            st.subheader("Texto Transcrito")
            if report_data.get('speech_provider'):
                st.caption(f"Realizado por: {report_data.get('speech_provider')}")
            if report_data.get('language'):
                st.caption(f"Idioma: {report_data.get('language')}")
            st.write(report_data.get('transcript'))
        vocal = report_data.get('audio_analysis') or {}
        if vocal:
            st.markdown("---")
            st.subheader("Indicadores vocais")
            st.warning("Indicadores acústicos não permitem inferir ou diagnosticar ansiedade, trauma, fadiga vocal ou qualquer condição de saúde.")
            quality = vocal.get('quality', {})
            if quality.get('reason'):
                st.info(quality['reason'])
            metrics = vocal.get('vocal_metrics')
            if metrics:
                labels = {
                    'speech_duration_seconds': 'Duração de fala (s)', 'pause_count': 'Pausas prolongadas',
                    'total_pause_seconds': 'Tempo em pausas (s)', 'average_pause_seconds': 'Pausa média (s)',
                    'longest_pause_seconds': 'Maior pausa (s)', 'words_per_minute': 'Palavras por minuto',
                    'filler_count': 'Hesitações textuais', 'pitch_mean_hz': 'Tom médio (Hz)',
                    'pitch_std_hz': 'Variação de tom (Hz)', 'intensity_mean_db': 'Intensidade média (dB)',
                    'intensity_std_db': 'Variação de intensidade (dB)'
                }
                st.json({labels.get(key, key): value for key, value in metrics.items() if value is not None})
            
    with col2:
        st.subheader("Texto (Sentimentos)")
        st.write(f"Status: {text_status.get('status', 'N/A')}")
        if text_status.get('reason'):
            st.info(text_status.get('reason'))
        if text_status.get('details'):
            st.json(text_status.get('details'))
