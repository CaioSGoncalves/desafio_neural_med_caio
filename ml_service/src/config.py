import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
QUEUE_INPUT = os.getenv("RABBITMQ_QUEUE_INPUT", "prontuario")
QUEUE_OUTPUT = os.getenv("RABBITMQ_QUEUE_OUTPUT", "resultado")

NER_MODEL_NAME = os.getenv("NER_MODEL_NAME", "pucpr/clinicalnerpt-disorder")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_USER = os.getenv("POSTGRES_USER", "myuser")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "mypassword")
POSTGRES_DB = os.getenv("POSTGRES_DB", "medical_db")
