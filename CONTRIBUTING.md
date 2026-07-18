# Guia de Contribuição

Obrigado pelo seu interesse em contribuir com o **Tech Challenge Fase 4**! 

## Como Contribuir

### 1. Criando uma Branch
Crie sempre uma branch a partir da `main` utilizando uma convenção clara de nomes:
- `feature/nome-da-funcionalidade`
- `bugfix/descrição-do-bug`
- `docs/atualizacao-documentacao`

### 2. Padrões de Commit
Utilizamos Conventional Commits. Exemplo de mensagens:
- `feat: adiciona extração de áudio`
- `fix: corrige threshold do MediaPipe`
- `docs: atualiza README com novos badges`

### 3. Testes
- Todos os PRs devem passar na suíte de testes.
- Execute `pytest` localmente antes de enviar suas mudanças.
- Mantenha a cobertura de código alta. Novas features devem vir acompanhadas de testes unitários em `tests/`.

### 4. Boas Práticas
- Siga as PEP 8 para formatação de código Python.
- Não altere a lógica de Fusion Engine sem discutir previamente na seção de Issues.
- Não versionar vídeos de teste, dados confidenciais ou o arquivo `.env`.

### 5. Pull Requests
- Preencha o template do Pull Request corretamente.
- Descreva as motivações, o impacto da mudança e quais testes foram validados.
- Um mantenedor fará a revisão do seu código antes do merge.
