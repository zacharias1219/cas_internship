from sentence_transformers import SentenceTransformer

class SentenceTransformerModel:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def encode(self, text, convert_to_tensor=False):
        return self.model.encode(text, convert_to_tensor=convert_to_tensor)
