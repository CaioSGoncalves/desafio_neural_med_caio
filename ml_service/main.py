from src.ml_service import MLService
from src.ner_model import NERModel
from src.repository.rabbitmq_repository import RabbitMQRepository
from src.repository.hot_storage_repository import HotStorageRepository
from src.repository.cold_storage_repository import ColdStorageRepository
import src.config as config

def main():
    rabbitmq_repository = RabbitMQRepository(config.RABBITMQ_HOST, 'prontuario', 'resultado')
    ner_model = NERModel(config.NER_MODEL_NAME)
    hot_storage = HotStorageRepository(config.REDIS_HOST)
    cold_storage = ColdStorageRepository(
        postgres_host=config.POSTGRES_HOST,
        postgres_user=config.POSTGRES_USER,
        postgres_password=config.POSTGRES_PASSWORD,
        postgres_db=config.POSTGRES_DB
    )

    service = MLService(rabbitmq_repository, ner_model, hot_storage, cold_storage)
    service.run()

if __name__ == "__main__":
    main()
