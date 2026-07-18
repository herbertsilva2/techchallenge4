import streamlit as st
from typing import Dict, Any

def render_fusion_tab(report_data: Dict[str, Any]):
    st.header("Fusão Multimodal e Resultado Final")
    
    fusion_result = report_data.get('fusion_result', {})
    
    if fusion_result:
        score = fusion_result.get('score', 0.0)
        risk_level = fusion_result.get('risk_level', 'desconhecido')
        
        st.subheader(f"Nível de Risco: {risk_level.upper()}")
        st.progress(min(1.0, max(0.0, score)))
        st.write(f"**Score Consolidado:** {score:.2f}")
        
        st.markdown("### Contribuições das Modalidades")
        st.info("Contribuição por modalidade indisponível na versão atual do modelo de dados.")
        
        if fusion_result.get('metadata'):
            st.write("Metadados:")
            st.json(fusion_result.get('metadata'))
    else:
        st.warning("Resultado da fusão não disponível.")
