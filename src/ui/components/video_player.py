import streamlit as st


VIDEO_PLAYER_MAX_WIDTH = 360


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
        
    # A largura fixa é automaticamente limitada à do contêiner pai pelo
    # Streamlit, mantendo o player responsivo em telas menores.
    with st.container(horizontal_alignment="center"):
        st.video(video_bytes, format=mime_type, width=VIDEO_PLAYER_MAX_WIDTH)
        st.caption(f"Vídeo carregado (formato: {extension})")
