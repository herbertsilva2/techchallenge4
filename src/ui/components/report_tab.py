import streamlit as st

def render_report_tab(report_md: str):
    st.header("Relatório Detalhado")
    if report_md:
        st.markdown(report_md)
    else:
        st.warning("Relatório Markdown não disponível.")
