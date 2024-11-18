import unittest
from src.ml_service import MLService

class TestMLService(unittest.TestCase):
    def setUp(self):
        self.ml_service = MLService(None, None, None, None)

    def test_extract_alterations(self):
        # B-I merge tokens
        entities = [("Diabetes", "B-Disorder"), ("Type 1", "I-Disorder")]
        result = self.ml_service.extract_alterations(entities)
        self.assertEqual(result, ["Diabetes Type 1"])

        # B-I merge tokens big
        entities = [("Hypertension", "B-Disorder"), ("High", "I-Disorder"), ("Blood", "I-Disorder"), ("Pressure", "I-Disorder")]
        result = self.ml_service.extract_alterations(entities)
        self.assertEqual(result, ["Hypertension High Blood Pressure"])

        # empty entities
        entities = []
        result = self.ml_service.extract_alterations(entities)
        self.assertEqual(result, [])

        # "##" separator case
        entities = [("Cancer", "B-Disorder"), ("##Stage", "I-Disorder")]
        result = self.ml_service.extract_alterations(entities)
        self.assertEqual(result, ["CancerStage"])

        # unique alterations
        entities = [("Cancer", "B-Disorder"), ("Cancer", "B-Disorder")]
        result = self.ml_service.extract_alterations(entities)
        self.assertEqual(result, ["Cancer"])

if __name__ == '__main__':
    unittest.main()