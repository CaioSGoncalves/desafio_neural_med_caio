import json
import pika

class RabbitMQRepository:
    def __init__(self, host, queue_input, queue_output):
        self.host = host
        self.queue_input = queue_input
        self.queue_output = queue_output
        self.connection = None
        self.channel = None

    def connect(self):
        print("Conectando ao RabbitMQ...")
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_input)
        self.channel.queue_declare(queue=self.queue_output)
        print("Conexão com RabbitMQ estabelecida.")

    def consume(self, callback):
        if not self.channel:
            self.connect()

        self.channel.basic_consume(queue=self.queue_input, on_message_callback=callback, auto_ack=True)
        print("Esperando mensagens... Pressione Ctrl+C para sair.")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("Interrompido pelo usuário.")
            self.close()

    def publish(self, message):
        self.channel.basic_publish(exchange='', routing_key=self.queue_output, body=json.dumps(message))
        print("Mensagem publicada na fila de saída.")

    def close(self):
        if self.connection:
            self.connection.close()
            print("Conexão com RabbitMQ encerrada.")
