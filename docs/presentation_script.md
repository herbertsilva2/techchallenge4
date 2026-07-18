
### Demonstração do MVP e Dashboard
**[Exibir o comando `streamlit run app.py` e abrir a interface]**
"Com a fundação do pipeline pronta, migramos para a visualização na web através do Streamlit. Note que o limite do dashboard foi estabelecido em uploads de até 200 MB e orienta-se o uso de vídeos curtos, pois toda a inferência multimodal ocorre nativamente de forma síncrona.
Vamos submeter o nosso vídeo exemplo. O sistema suporta processamento resiliente:
- Se não definirmos a chave Azure no `.env`, a transcrição é pulada e o motor prossegue com score parcial;
- Se o nosso YOLO refinado ainda não estiver inserido em `models/yolo/best.pt`, o sistema utiliza os pesos originais do YOLO em modo demonstração automaticamente.
Por fim, podemos observar a aba de Fusão que compila as detecções textuais e visuais. Notem que por limitações presentes nos módulos de áudio individuais, desativamos o gráfico de torta de contribuições para privilegiar o score linear direto."
