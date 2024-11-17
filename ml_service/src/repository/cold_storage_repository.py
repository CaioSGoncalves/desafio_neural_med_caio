import json
import psycopg2
from psycopg2.extras import Json

from src.model.patient_data import PatientData, PatientHistory

class ColdStorageRepository:
    def __init__(self, postgres_host, postgres_user, postgres_password, postgres_db):
        self.conn = psycopg2.connect(
            host=postgres_host,
            user=postgres_user,
            password=postgres_password,
            dbname=postgres_db
        )
        self._create_table()

    def _create_table(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patient_history (
                    id SERIAL PRIMARY KEY,
                    patient_id VARCHAR(255),
                    visit_id VARCHAR(255),
                    visit_date TIMESTAMP,
                    medical_record VARCHAR(255),
                    patient_sex VARCHAR(255),
                    entities JSONB,
                    results JSONB,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            self.conn.commit()

    def save_patient_history(self, patient_history: PatientHistory):
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO patient_history (patient_id, visit_id, visit_date, medical_record, patient_sex, entities, results)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (patient_history.patient_id, patient_history.visit_id, patient_history.visit_date,
                 patient_history.medical_record, patient_history.patient_sex, 
                 Json(patient_history.entities), Json(patient_history.results))
            )
            self.conn.commit()

    def get_patient_visit_agg(self, patient_id, visit_id) -> dict:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT patient_id, visit_id, 
                       ARRAY_AGG(results->>'alterations') AS alterations,
                       BOOL_OR((results->>'cancer_detected')::boolean) AS cancer_detected,
                       MAX((results->>'cancer_detected_date')::timestamp) AS cancer_detected_date
                FROM patient_history
                WHERE patient_id = %s AND visit_id = %s
                GROUP BY patient_id, visit_id
                """,
                (patient_id, visit_id)
            )
            result = cursor.fetchone()
            if result:
                alterations_set = {alteration for i_list in result[2] for alteration in json.loads(i_list)}
                print(list(alterations_set))
                return PatientData(
                    patient_id=result[0],
                    visit_id=result[1],
                    alterations=list(alterations_set),
                    cancer_detected=result[3],
                    cancer_detected_date=result[4]
                ).__dict__
            return None

