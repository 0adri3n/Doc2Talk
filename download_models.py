from sentence_transformers import SentenceTransformer, CrossEncoder

print("\nStarting download : ms-marco-MiniLM-L-12-v2\n")

modelPath = "models/ms-marco-MiniLM-L-12-v2"

model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')
model.save(modelPath)
model = CrossEncoder(modelPath)

print("\nDownload finished : ms-marco-MiniLM-L-12-v2\n")


print("\nStarting download : multilingual-e5-large\n")

modelPath = "models/e5-multilingual"

model = SentenceTransformer('intfloat/multilingual-e5-large')
model.save(modelPath)
model = SentenceTransformer(modelPath)

print("\nDownload finished : multilingual-e5-large\n")

