import streamlit as st

def render_about_tab():
    st.header("Sobre o Tech Challenge Fase 4")
    st.write("Este dashboard apresenta os resultados do processamento multimodal para detecção de desconforto psicológico.")
    st.write("Módulos Integrados:")
    st.markdown("- **Vídeo:** MediaPipe (faces) e YOLO (objetos/postura)")
    st.markdown("- **Áudio:** Azure Speech (transcrição)")
    st.markdown("- **Texto:** Análise local de sentimentos")
    st.markdown("- **Fusão:** Algoritmo integrado")
    
    st.info("Nota: O processamento é síncrono. O gráfico de contribuições foi removido por falta de score individual.")
