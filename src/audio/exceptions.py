class AudioTranscriptionError(Exception):
    """Exceção base para erros de transcrição de áudio."""
    pass

class AzureSpeechConfigurationError(AudioTranscriptionError):
    """Lançada quando há problemas na configuração do Azure Speech."""
    pass

class AzureSpeechServiceError(AudioTranscriptionError):
    """Lançada quando o serviço Azure Speech retorna um erro."""
    pass
