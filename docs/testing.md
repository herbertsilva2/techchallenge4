# Guia de Testes

O Tech Challenge 4 utiliza o `pytest` como principal framework de testes unitários e de integração.

## Executando os Testes

```bash
pytest
```

## Estrutura
- `tests/test_domain_models.py`: Validação de contratos Pydantic e classes de dados.
- `tests/test_pipeline_service.py`: Simulação e mocks do pipeline completo ponta a ponta.
- `tests/test_azure_speech_transcriber.py`: Testes de fallback caso falte chave da Azure.

## Dicas para Novos Testes
Ao contribuir, utilize o `unittest.mock` para simular as requisições web ou operações pesadas com o MediaPipe e YOLO.
