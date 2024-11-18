import json
from typing import List, Tuple

from src.model.patient_data import PatientData, PatientHistory
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
        new_alterations = self.extract_alterations(entities)

        if new_alterations:
            current_data = self.hot_storage.get_patient_data(patient_id, visit_id) or self.cold_storage.get_patient_visit_agg(patient_id, visit_id)
            patient_data = PatientData(
                patient_id=patient_id,
                visit_id=visit_id,
                alterations=current_data.get("alterations", []) if current_data else [],
                cancer_detected=False,
            )
            patient_data.alterations = list(set(patient_data.alterations + new_alterations))
            (
                patient_data.cancer_detected,
                patient_data.cancer_detected_date
            ) = self.check_for_cancer_detection(patient_data.alterations, data_atendimento)

            self.hot_storage.save_patient_data(patient_id, visit_id, patient_data.__dict__)
            self.rabbitmq_repository.publish(patient_data.__dict__)

        cancer_detected, cancer_detected_date = self.check_for_cancer_detection(new_alterations, data_atendimento)
        patient_history = PatientHistory(
            patient_id=patient_id,
            visit_id=visit_id,
            visit_date=data_atendimento,
            medical_record=texto_prontuario,
            patient_sex=data.get("sexo", "Unknown"),
            entities=entities,
            results={
                "alterations": new_alterations,
                "cancer_detected": cancer_detected,
                "cancer_detected_date": cancer_detected_date,
                
            }
        )
        self.cold_storage.save_patient_history(patient_history)
    
    def extract_alterations(self, entities: list) -> List[str]:
        new_alterations = []
        current_alteration = None
        for token, label in entities:
            if label.startswith("B-Disorder"):
                if current_alteration:
                    new_alterations.append(current_alteration)
                current_alteration = token
            elif label.startswith("I-Disorder") and current_alteration:
                if "##" in token:
                    current_alteration += token
                else:
                    current_alteration += " " + token
        if current_alteration:
            new_alterations.append(current_alteration.replace("##", ""))
        new_alterations = list(set(new_alterations))
        return new_alterations

    def check_for_cancer_detection(self, alterations: list, data_atendimento: str) -> Tuple[bool, str]:
        for alteration in alterations:
            if any(x in alteration.lower() for x in ["câncer", "cancer", "ca"]):
                return True, data_atendimento
        return False, None
    
    def run(self):
        self.rabbitmq_repository.connect()
        self.rabbitmq_repository.consume(self.process_message)
