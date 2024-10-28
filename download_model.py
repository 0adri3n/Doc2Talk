from sentence_transformers import SentenceTransformer, CrossEncoder
modelPath = "models/ms-marco-MiniLM-L-12-v2"

model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')
model.save(modelPath)
model = CrossEncoder(modelPath)