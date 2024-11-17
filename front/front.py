import os
import streamlit as st
import pika
import json
import redis  # Biblioteca do Redis
import psycopg2  # Biblioteca para PostgreSQL
from psycopg2.extras import RealDictCursor  # Para obter resultados como dicionários
from datetime import datetime

# Configurações do RabbitMQ
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
QUEUE_PRONTUARIO = os.getenv('RABBITMQ_QUEUE_INPUT', 'prontuario')  # Fila de envio
QUEUE_RESULTADO = os.getenv('RABBITMQ_QUEUE_OUTPUT', 'resultado')    # Fila de leitura

# Configurações do Redis
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

# Configurações do PostgreSQL
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_USER = os.getenv("POSTGRES_USER", "myuser")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "mypassword")
POSTGRES_DB = os.getenv("POSTGRES_DB", "medical_db")

# Conexão com o Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

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

# Função para consultar histórico no PostgreSQL
def query_patient_history(patient_id):
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB
    )
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM public.patient_history WHERE patient_id = %s;", (patient_id,))
            results = cursor.fetchall()
            return results
    finally:
        conn.close()

# Interface Streamlit
st.title("RabbitMQ, Redis e PostgreSQL Dashboard")

# Menu de navegação
tabs = st.tabs(["Enviar Mensagem", "Mensagens Recebidas", "Consulta Redis", "Consulta Histórica"])

with tabs[0]:
    st.header("Enviar Mensagem")

    # Dados pré-preenchidos
    id_paciente_default = "12345"
    data_nascimento_default = datetime(1990, 5, 15)
    sexo_default = "Masculino"
    texto_prontuario_default = "Paciente com CA de mama, histórico de diabetes mellitus"
    id_atendimento_default = "98765"
    data_atendimento_default = datetime(2024, 11, 15)

    # Campos de entrada para a mensagem, já com valores pré-preenchidos
    id_paciente = st.text_input("ID Paciente", value=id_paciente_default)
    data_nascimento = st.date_input("Data de Nascimento", value=data_nascimento_default)
    sexo = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro"], index=["Masculino", "Feminino", "Outro"].index(sexo_default))
    texto_prontuario = st.text_area("Texto Prontuário", value=texto_prontuario_default)
    id_atendimento = st.text_input("ID Atendimento", value=id_atendimento_default)
    data_atendimento = st.date_input("Data de Atendimento", value=data_atendimento_default)

    if st.button("Enviar", key="send_message"):
        if id_paciente and data_nascimento and sexo and texto_prontuario and id_atendimento and data_atendimento:
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

with tabs[1]:
    st.header("Mensagens Recebidas da Fila 'Resultado'")
    if st.button("Atualizar Mensagens", key="refresh_messages"):
        messages = consume_messages_from_rabbitmq()
        if messages:
            for msg in messages:
                st.json(msg)
        else:
            st.info("Nenhuma mensagem na fila 'resultado'.")

with tabs[2]:
    st.header("Consulta Dados do Redis")

    id_paciente_redis = st.text_input("ID Paciente", key="id_paciente_redis")
    id_atendimento_redis = st.text_input("ID Atendimento", key="id_atendimento_redis")

    redis_key = f"patient:{id_paciente_redis}-visit:{id_atendimento_redis}"

    if st.button("Consultar", key="consult_redis"):
        if id_paciente_redis and id_atendimento_redis:
            value = redis_client.get(redis_key)
            if value:
                st.json(json.loads(value))
            else:
                st.warning(f"Nenhum valor encontrado para a chave '{redis_key}'.")
        else:
            st.error("Por favor, preencha ambos os campos: ID Paciente e ID Atendimento.")

with tabs[3]:
    st.header("Consulta Histórica no PostgreSQL")

    patient_id = st.text_input("ID Paciente para Consulta Histórica", key="patient_id_history")

    if st.button("Consultar Histórico", key="consult_history"):
        if patient_id:
            results = query_patient_history(patient_id)
            if results:
                for record in results:
                    st.json(record)
            else:
                st.warning(f"Nenhum histórico encontrado para o ID Paciente '{patient_id}'.")
        else:
            st.error("Por favor, insira o ID do Paciente.")
