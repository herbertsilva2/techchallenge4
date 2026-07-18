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
2. O arquivo `.env` (onde as chaves reais são armazenadas) está incluído no `.gitignore` e não deve ser comitado.
3. Utilize apenas o `.env.example` como guia para as variáveis de ambiente necessárias.
4. Modelos pesados (.pt, .tflite) estão restritos para otimização de banda, evite subir arquivos não controlados de LFS.

## Como Reportar uma Vulnerabilidade

Caso encontre alguma falha de segurança no processamento de vídeos, exposição de credenciais em logs ou problemas nas dependências, **não abra uma issue pública**.

Envie um relatório de vulnerabilidade diretamente para a equipe de mantenedores na aba "Security" ou entre em contato pelo email de suporte do mantenedor. 
Você deverá receber um retorno em até 48 horas.
