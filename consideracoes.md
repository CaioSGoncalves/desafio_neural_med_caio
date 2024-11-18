# Considerações:
- Inicialmente, utilizei o Streamlit como interface frontend para facilitar os testes. No entanto, decidi mantê-lo, pois apresenta a solução de forma clara e eficiente. Vale destacar que boa parte do código do frontend foi gerada com o auxílio de modelos de IA, como ChatGPT e Cursor Small LLM.


# Futuras alterações:
- Configurar CI/CI no Github
- Deploy na GCP com Cloud Run ou Google Kubernetes Engine
- Deploy dos bancos(Redis, PosgreSQL) em serviço gerenciados na GCP
- Em caso de erro ao processar da fila de input, enviar para uma fila de erro e não interromper a execução.


# Perguntas extras:
- Como faria para otimizar o desempenho se recebesse 100k prontuários por hora? (não
é preciso fazer as otimizações para o teste, apenas dizer o que mudaria na
implementação para este caso em particular)

## Resposta:
Para otimizar o desempenho e processar 100k prontuários por hora, eu adotaria a escalabilidade horizontal, aumentando o número de workers do ml_service consumindo da fila do RabbitMQ. Isso garantiria um maior paralelismo no processamento das mensagens. 

Já implementei uma solução semelhante utilizando Kafka com Python, onde configurei múltiplos consumidores em AWS ECS (contêineres Docker). Essa abordagem permitiu a empresa lidar com um alto volume de mensagens de forma eficiente, aproveitando a escalabilidade horizontal do ECS e o particionamento do Kafka para garantir throughput elevado e baixa latência.
Adotaria conceitos similares aqui.