from dataclasses import dataclass

@dataclass
class PatientData:
    patient_id: str
    visit_id: str
    alterations: list
    cancer_detected: bool
    cancer_detected_date: str = None


@dataclass
class PatientHistory:
    patient_id: str
    visit_id: str
    visit_date: str
    medical_record: str
    patient_sex: str
    entities: list
    results: dict