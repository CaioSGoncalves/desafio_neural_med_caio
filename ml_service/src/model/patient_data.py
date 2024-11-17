from dataclasses import dataclass

@dataclass
class PatientData:
    id_paciente: str
    id_atendimento: str
    alterations: list
    cancer_detected: bool
    cancer_detected_date: str = None