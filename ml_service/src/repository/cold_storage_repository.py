import psycopg2
from psycopg2.extras import Json

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
        """Cria tabela de histórico de pacientes, se não existir."""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patient_history (
                    id SERIAL PRIMARY KEY,
                    patient_id VARCHAR(255),
                    visit_id VARCHAR(255),
                    data JSONB,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            self.conn.commit()

    def save_patient_data(self, patient_id, visit_id, data):
        """Salva o histórico completo no PostgreSQL."""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO patient_history (patient_id, visit_id, data)
                VALUES (%s, %s, %s)
                """,
                (patient_id, visit_id, Json(data))
            )
            self.conn.commit()
