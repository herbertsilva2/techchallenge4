import streamlit as st
from typing import Dict, Any

def render_visual_tab(report_data: Dict[str, Any]):
    st.header("Análise Visual")
    
    modalities = report_data.get('modalities', {})
    video_status = modalities.get('video', {})
    yolo_status = modalities.get('yolo', {})
    
    if video_status.get('status') == 'completed' or video_status.get('status') == 'partial':
        st.success(f"Status do Processamento de Vídeo: {video_status.get('status').upper()}")
        details = video_status.get('details', {})
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Frames Analisados", details.get('frames_analyzed', 0))
        with col2:
            st.metric("Faces Detectadas", details.get('faces_detected', 0))
        with col3:
            st.metric("Objetos Detectados", details.get('objects_detected', 0))
            
        if video_status.get('reason'):
            st.info(f"Nota: {video_status.get('reason')}")
            
    else:
        st.error(f"Erro ou status inesperado: {video_status.get('status')}")
        if video_status.get('reason'):
            st.write(f"Motivo: {video_status.get('reason')}")

    st.subheader("Detector visual especializado")
    st.write(f"Status: {yolo_status.get('status', 'N/A')}")
    detector_details = yolo_status.get('details', {})
    if detector_details.get('model_mode') == 'pretrained_gesture':
        st.info("MediaPipe Hands + Face Mesh detecta proximidade persistente entre mão e rosto.")
        st.warning("O modelo YOLOv8 customizado ainda não foi treinado; este sinal exige revisão humana.")
    elif yolo_status.get('status') == 'partial' or yolo_status.get('reason'):
        if yolo_status.get('reason'):
            st.info(yolo_status.get('reason'))
