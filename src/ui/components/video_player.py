import streamlit as st

def render_video_player(video_bytes: bytes, extension: str):
    """
    Renderiza o reprodutor de vídeo no dashboard.
    Garante que o tipo MIME seja adequado para o navegador.
    """
    mime_type = "video/mp4"
    if extension.lower() in [".avi"]:
        mime_type = "video/x-msvideo"
    elif extension.lower() in [".mov"]:
        mime_type = "video/quicktime"
    elif extension.lower() in [".mkv"]:
        mime_type = "video/x-matroska"
        
    st.video(video_bytes, format=mime_type)
    st.caption(f"Vídeo carregado (formato: {extension})")
