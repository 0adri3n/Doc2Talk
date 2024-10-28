from classes.user_query import UserQuery
from classes.query_handler import QueryHandler
import json

def generate_prompt(context_chunks, question):
    """
    Construit le prompt pour Ollama avec le contexte et la question.
    """
    context_text = "\n\n".join([chunk['Chunk Text'] for chunk in context_chunks])  # Limiter à 5 chunks par ex.
    prompt = (
        "You are a knowledgeable assistant.\n"
        "Please answer the following question using the provided context.\n\n"
        "Context:\n"
        f"{context_text}\n\n"
        "Question:\n"
        f"{question}\n\n"
        "Answer:"
    )
    return prompt

import requests

def get_response_from_ollama(prompt):
    """
    Envoie le prompt au serveur Ollama et récupère la réponse.
    """
    url = "http://localhost:11434/api/generate"  # URL mise à jour pour Ollama
    payload = {
        "model": "llama3.2",  # Modèle spécifié
        "prompt": prompt,
        "stream": False
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        try:
            data = json.loads(response.text)
            api_response = data.get("response", "")
            
            if not data.get("done", False): 
                print("Le traitement n'est pas encore terminé.")
            else:
                print(api_response) 
        except json.JSONDecodeError as e:
            print(f"Erreur lors du décodage de la réponse JSON: {e}")
    else:
        print("Erreur:", response.text)
        return None



# Exemple d'utilisation
user_query = UserQuery(index_name="pdf_chunks")

# Question de l'utilisateur
question = input("Quelle est votre question :\n")

# Choisir une méthode (par exemple, standard, knn, rrf, boost)
response = user_query.query(question, method="rrf")
results = user_query.get_metadata_as_list(response)
query_handler = QueryHandler(index_name="pdf_chunks")
reranked_results = query_handler.rerank_results(question=question, results_as_list=results)
    
# 3. Génération du prompt
prompt = generate_prompt(reranked_results, question)

# 4. Envoi du prompt au serveur Ollama et récupération de la réponse
answer = get_response_from_ollama(prompt)
