import json

from src.model.patient_data import PatientData
from src.ner_model import NERModel
from src.repository.cold_storage_repository import ColdStorageRepository
from src.repository.hot_storage_repository import HotStorageRepository
from src.repository.rabbitmq_repository import RabbitMQRepository


class MLService:
    def __init__(self, rabbitmq_repository: RabbitMQRepository, ner_model: NERModel, hot_storage: HotStorageRepository, cold_storage: ColdStorageRepository):
        self.rabbitmq_repository = rabbitmq_repository
        self.ner_model = ner_model
        self.hot_storage = hot_storage
        self.cold_storage = cold_storage

    def process_message(self, ch, method, properties, body):
        print("Mensagem recebida:")
        print(body)

        data = json.loads(body)
        patient_id = data.get("id_paciente")
        visit_id = data.get("id_atendimento")
        texto_prontuario = data.get("texto_prontuario", "")
        data_atendimento = data.get("data_atendimento")

        print(f"Processando texto: {texto_prontuario}")
        entities = self.ner_model.predict(texto_prontuario)

        patient_data = PatientData(
            id_paciente=patient_id,
            id_atendimento=visit_id,
            alterations=[],
            cancer_detected=False,
        )

        for token, label in entities:
            if label.startswith("B-Disorder"):
                alteration = {"token": token, "date": data_atendimento}
                patient_data.alterations.append(alteration)
                if token.lower() in ["câncer", "cancer", "ca"]:
                    patient_data.cancer_detected = True
                    patient_data.cancer_detected_date = data_atendimento

        patient_data_dict = patient_data.__dict__
        self.hot_storage.save_patient_data(patient_id, patient_data_dict)
        self.cold_storage.save_patient_data(patient_id, visit_id, patient_data_dict)
        self.rabbitmq_repository.publish(patient_data_dict)

        print(f"Resultado: {patient_data_dict}")

    def run(self):
        self.rabbitmq_repository.connect()
        self.rabbitmq_repository.consume(self.process_message)
