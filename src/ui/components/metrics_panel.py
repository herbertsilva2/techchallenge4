import streamlit as st
from typing import Dict, Any

def render_metrics_panel(video_info: Dict[str, Any]):
    """
    Renderiza um painel com métricas gerais do vídeo no dashboard.
    """
    if not video_info:
        st.warning("Informações do vídeo indisponíveis.")
        return

    st.markdown("### Metadados do Vídeo")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Resolução", f"{video_info.get('width', 0)}x{video_info.get('height', 0)}")
    with col2:
        st.metric("Duração", f"{video_info.get('duration_seconds', 0.0):.2f}s")
    with col3:
        st.metric("FPS", f"{video_info.get('fps', 0.0):.2f}")
        
    st.markdown(f"**Codec:** `{video_info.get('codec', 'N/A')}` | **Total de Frames:** `{video_info.get('frame_count', 0)}`")
