from streamlit.testing.v1 import AppTest
import pytest
import os
from pathlib import Path

def test_app_ui_components():
    # Caminho absoluto para o app.py
    app_path = str(Path(__file__).parent.parent / "app.py")
    
    # Check if streamlit is available, if not skip (though it should be)
    try:
        import streamlit
    except ImportError:
        pytest.skip("Streamlit not installed")

    at = AppTest.from_file(app_path)
    at.run()
    
    assert not at.exception
    
    # Title and subtitle
    assert at.title[0].value == "Sistema Multimodal de Apoio à Triagem"
    assert at.subheader[0].value == "Tech Challenge Fase 4"
    
    # Ethical warning (warning)
    warnings = [w.value for w in at.warning]
    assert any("Este sistema é um protótipo educacional para demonstração de IA multimodal" in w for w in warnings)
    
    # Uploader
    assert len(at.file_uploader) > 0

    # Simulate an upload to show the button and check it
    file_bytes = b"test-video-content"
    at.file_uploader[0].set_value(("test_video.mp4", file_bytes, "video/mp4"))
    
    # Run once to process the upload and let app.py reset the state
    at.run()

    assert len(at.checkbox) == 1
    assert at.button[0].disabled is True
    at.checkbox[0].check()
    at.run()
    assert at.button[0].disabled is False

    at.file_uploader[0].set_value(("another_video.mp4", file_bytes, "video/mp4"))
    at.run()
    assert at.checkbox[0].value is False
    assert at.button[0].disabled is True
    at.checkbox[0].check()
    at.run()
    
    # Now that the upload is registered, we can override the session state to simulate processing completion
    from src.domain.processing_models import PipelineResult

    at.session_state['processing_completed'] = True
    dummy_result = PipelineResult(status='partial', messages=[], errors=[], execution_times=[])
    at.session_state['pipeline_result'] = dummy_result
    at.session_state['report_data'] = {
        'video_info': {},
        'modalities': {
            'yolo': {'status': 'partial', 'reason': 'demo'},
            'transcription': {'status': 'partial', 'reason': 'Credenciais ausentes'}
        },
        'fusion_result': {'score': 50, 'risk_level': 'moderado'}
    }
    at.session_state['report_markdown'] = "Report content"

    at.run()

    # Check button (Processar Vídeo is not visible if processing_completed is True, let's just check the tabs first)
    assert not at.exception
    
    # Check messages
    warnings = [w.value for w in at.warning]
    assert any("O sistema continua operando com as modalidades disponíveis" in w for w in warnings)
    
    # Fusion message
    infos = [i.value for i in at.info]
    assert any("Contribuição por modalidade indisponível na versão atual do modelo de dados." in i for i in infos)
    
    # Check tabs
    assert len(at.tabs) == 5
    assert at.tabs[0].label == "Visual"
    assert at.tabs[1].label == "Áudio/Texto"
    assert at.tabs[2].label == "Fusão"
    
    # To check the button, we set processing_completed to False
    at.session_state['processing_completed'] = False
    at.session_state['consent_given'] = True
    at.run()
    assert len(at.button) > 0
    assert at.button[0].label == "Processar Vídeo"
