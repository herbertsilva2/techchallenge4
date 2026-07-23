# Security Policy

## Versões Suportadas

Apenas a versão mais recente (`v1.0.0`) receberá atualizações de segurança.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.0   | :white_check_mark: |
| < 1.0   | :x:                |

## Boas Práticas de Segurança e Credenciais

Este projeto integra-se com serviços em nuvem (Azure AI Speech) que exigem chaves de API restritas.
Para garantir a segurança do repositório público:

1. **NUNCA publique chaves ou tokens no repositório GitHub.**
2. Armazene chaves reais somente em `.env.local`, arquivo ignorado pelo Git; nunca versione arquivos com credenciais.
3. Utilize apenas o `.env.example` como guia para as variáveis de ambiente necessárias.
4. Modelos pesados (.pt, .tflite) estão restritos para otimização de banda, evite subir arquivos não controlados de LFS.

## Privacidade e retenção de mídia

O dashboard exige consentimento antes do processamento. O arquivo enviado, os frames extraídos e o áudio derivado são apagados ao final da análise, inclusive quando há erro. Os relatórios e registros de alerta permanecem disponíveis para a sessão; como uma transcrição pode conter conteúdo pessoal falado no arquivo, ela deve ser acessada e compartilhada somente por pessoas autorizadas.

## Como Reportar uma Vulnerabilidade

Caso encontre alguma falha de segurança no processamento de vídeos, exposição de credenciais em logs ou problemas nas dependências, **não abra uma issue pública**.

Envie um relatório de vulnerabilidade diretamente para a equipe de mantenedores na aba "Security" ou entre em contato pelo email de suporte do mantenedor. 
Você deverá receber um retorno em até 48 horas.
