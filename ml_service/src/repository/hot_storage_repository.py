import redis
import json

class HotStorageRepository:
    def __init__(self, redis_host, redis_port=6379):
        self.client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

    def save_patient_data(self, patient_id, data):
        key = f"patient:{patient_id}"
        self.client.set(key, json.dumps(data))
    
    def get_patient_data(self, patient_id):
        key = f"patient:{patient_id}"
        data = self.client.get(key)
        return json.loads(data) if data else None
