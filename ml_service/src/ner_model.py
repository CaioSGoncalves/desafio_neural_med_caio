import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer

class NERModel:
    def __init__(self, model_name):
        print("Carregando modelo NER...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name)
        print("Modelo carregado com sucesso!")

    def predict(self, text):
        inputs = self.tokenizer(text, max_length=512, truncation=True, return_tensors="pt")
        tokens = inputs.tokens()
        outputs = self.model(**inputs).logits
        predictions = torch.argmax(outputs, dim=2)

        result = [
            (token, self.model.config.id2label[prediction])
            for token, prediction in zip(tokens, predictions[0].numpy())
        ]
        return result
