import os
import streamlit as st
import pika
import json
from datetime import datetime

# Configurações do RabbitMQ
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
QUEUE_PRONTUARIO = os.getenv('RABBITMQ_QUEUE_INPUT', 'prontuario')  # Fila de envio
QUEUE_RESULTADO = os.getenv('RABBITMQ_QUEUE_OUTPUT', 'resultado')    # Fila de leitura

# Função para enviar mensagem para a fila "prontuario" do RabbitMQ
def send_message_to_rabbitmq(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_PRONTUARIO)  # Certifica-se que a fila existe
    channel.basic_publish(exchange='', routing_key=QUEUE_PRONTUARIO, body=json.dumps(message))
    connection.close()

# Função para consumir mensagens da fila "resultado" do RabbitMQ (Polling)
def consume_messages_from_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_RESULTADO)  # Certifica-se que a fila existe

    messages = []
    while True:
        method_frame, _, body = channel.basic_get(queue=QUEUE_RESULTADO, auto_ack=True)
        if method_frame:
            messages.append(json.loads(body.decode()))
        else:
            break
    connection.close()
    return messages

# Interface Streamlit
st.title("RabbitMQ Dashboard")

# Dados pré-preenchidos
id_paciente_default = "12345"
data_nascimento_default = datetime(1990, 5, 15)  # Exemplo de data de nascimento
sexo_default = "Masculino"
texto_prontuario_default = "Paciente com CA de mama, histórico de diabetes mellitus"
id_atendimento_default = "98765"
data_atendimento_default = datetime(2024, 11, 15)  # Exemplo de data de atendimento

# Enviar mensagem
st.header("Enviar Mensagem")

# Campos de entrada para a mensagem, já com valores pré-preenchidos
id_paciente = st.text_input("ID Paciente", value=id_paciente_default)
data_nascimento = st.date_input("Data de Nascimento", value=data_nascimento_default)
sexo = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro"], index=["Masculino", "Feminino", "Outro"].index(sexo_default))
texto_prontuario = st.text_area("Texto Prontuário", value=texto_prontuario_default)
id_atendimento = st.text_input("ID Atendimento", value=id_atendimento_default)
data_atendimento = st.date_input("Data de Atendimento", value=data_atendimento_default)

# Botão para enviar a mensagem
if st.button("Enviar"):
    if id_paciente and data_nascimento and sexo and texto_prontuario and id_atendimento and data_atendimento:
        # Criando a mensagem conforme o schema solicitado
        message = {
            "id_paciente": id_paciente,
            "data_nascimento": data_nascimento.isoformat(),
            "sexo": sexo,
            "texto_prontuario": texto_prontuario,
            "id_atendimento": id_atendimento,
            "data_atendimento": data_atendimento.isoformat()
        }

        send_message_to_rabbitmq(message)
        st.success("Mensagem enviada com sucesso para a fila 'prontuario'!")
    else:
        st.error("Por favor, preencha todos os campos.")

# Visualizar mensagens
st.header("Mensagens Recebidas da Fila 'Resultado'")
if st.button("Atualizar Mensagens"):
    messages = consume_messages_from_rabbitmq()
    if messages:
        for msg in messages:
            st.write(f"Mensagem: {msg}")
    else:
        st.info("Nenhuma mensagem na fila 'resultado'.")
